import json
from pathlib import Path
from time import monotonic_ns

from PySide6.QtCore import QObject, Signal, Slot,QTimer
from src.devices.drivers_factory import create_hand
from src.shared_data.capture_ring_buffer import CaptureRingBuffer
from src.shared_data.device_feedback import FeedbackStatus
from src.shared_data.robot_share_data import HandState, RobotSharedMemory
from src.ui.log_stream import Logger

class HandThread(QObject):
    CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "hand_control.json"
    sig_connect_result = Signal(bool, str)
    sig_disconnect_result = Signal(bool, str)

    def __init__(self, shared_data: RobotSharedMemory,
                 capture_buffer: CaptureRingBuffer[HandState],
                 action_buffer: CaptureRingBuffer[list[int]]):
        super().__init__()
        self.hand = None
        self.shared_data = shared_data
        self.capture_buffer = capture_buffer
        self.action_buffer = action_buffer
        self.if_connected = False
        self._last_capture_sequence = 0
        self.recording_locked = False
        self.timer_read_pos = QTimer(self)
        self.timer_read_pos.setInterval(20)
        self.timer_read_pos.timeout.connect(self.OnTimerTriggeredReadPos)

    @Slot()
    def OnTimerTriggeredReadPos(self):
        """定时读取真实关节位置，失败时清空旧读数。"""
        if not self.if_connected or self.hand is None:
            return
        try:
            sample = self.hand.Read_joint_positions()
        except Exception as error:
            previous = self.shared_data.hand.read().feedback
            if previous.error != str(error) or previous.valid:
                Logger.instance().error(f"[{self.hand.name}] {error}")
            self.shared_data.hand.update_partial(joints=[], feedback=previous.failure(error))
            return
        state = HandState(list(sample.values), self.hand.name, FeedbackStatus.success(sample))
        self.shared_data.hand.write(state)
        if sample.sequence != self._last_capture_sequence:
            self.capture_buffer.append(state.snapshot(), sample.timestamp_ns)
            self._last_capture_sequence = sample.sequence

    @Slot(str, str, str, str)
    def ConnectHand(self, hand_model, hand_type, comm_type, comm_info) -> bool:
        if self.if_connected:
            self.sig_connect_result.emit(False, "请先断开灵巧手，再连接设备")
            return False

        driver_hand_type = "right" if hand_type == "Right Hand" else "left"
        comm_type = comm_type.strip().lower()
        kwargs = {
            "hand_type": driver_hand_type,
            "hand_joint": "O6" if hand_model == "LinkerO6" else hand_model,
        }
        if comm_type in ("modbus", "modebus"):
            kwargs.update(modbus=comm_info, can="None")
        elif comm_type == "can":
            kwargs.update(can=comm_info, modbus="None")

        try:
            self.hand = create_hand(hand_model, **kwargs)
        except Exception as error:
            message = str(error)
            Logger.instance().error(message)
            self.sig_connect_result.emit(False, message)
            return False

        if self.hand.Connect():
            Logger.instance().info(f"[{self.hand.name}] connected successfully")
            self.if_connected = True
            self.shared_data.hand.update_partial(name=hand_model, joints=[], feedback=FeedbackStatus())
            self._last_capture_sequence = 0
            self.capture_buffer.clear()
            self.action_buffer.clear()
            self.timer_read_pos.start()
            self.sig_connect_result.emit(True, f"[{self.hand.name}] connected successfully")
            return True
        else:
            self.sig_connect_result.emit(False, f"[{self.hand.name}] failed to connect")
            Logger.instance().error(f"[{self.hand.name}] failed to connect")
            return False

    @Slot()
    def Disconnect(self) -> bool:
        if self.hand is None:
            self.sig_disconnect_result.emit(False, "灵巧手驱动尚未创建")
            return False
        if self.hand.Disconnect():
            self.timer_read_pos.stop()
            Logger.instance().info(f"[{self.hand.name}] disconnected successfully")
            self.if_connected = False
            self.shared_data.hand.update_partial(name="", joints=[], feedback=FeedbackStatus())
            self._last_capture_sequence = 0
            self.capture_buffer.clear()
            self.action_buffer.clear()
            self.sig_disconnect_result.emit(True, f"[{self.hand.name}] disconnected successfully")
            return True
        else:
            self.sig_disconnect_result.emit(False, f"[{self.hand.name}] failed to disconnect")
            Logger.instance().error(f"[{self.hand.name}] failed to disconnect")
            return False

    @Slot()
    def Shutdown(self):
        self.timer_read_pos.stop()
        if self.if_connected:
            self.Disconnect()
        
    @Slot(list)
    def Set_joint_positions(self, positions: list) -> bool:
        if self.recording_locked:
            Logger.instance().error("采集期间不能手动改变灵巧手目标")
            return False
        if self.hand is None:
            Logger.instance().error("灵巧手驱动尚未创建")
            return False
        if self.hand.Set_joint_positions(positions):
            self.action_buffer.append(list(positions), monotonic_ns())
            Logger.instance().info(f"[{self.hand.name}] set joint positions successfully")
            return True
        else:
            self.action_buffer.clear()
            Logger.instance().error(f"[{self.hand.name}] failed to set joint positions")
            return False

    @Slot(list)
    def Set_speed(self, speed: list) -> bool:
        if self.recording_locked:
            Logger.instance().error("采集期间不能手动改变灵巧手速度")
            return False
        if self.hand is None:
            Logger.instance().error("灵巧手驱动尚未创建")
            return False
        if self.hand.Set_speed(speed):
            Logger.instance().info(f"[{self.hand.name}] set speed successfully")
            return True
        else:
            Logger.instance().error(f"[{self.hand.name}] failed to set speed")
            return False

    @Slot(bool)
    def ExecuteFollowState(self, closed: bool) -> bool:
        """执行扳机对应的灵巧手动作。

        closed=True 执行设置页选定的 Close 动作，False 执行 Open 动作。
        动作包含关节位置、统一速度和统一力矩；配置或设备命令失败时返回 False。
        """
        if not self.if_connected or self.hand is None:
            Logger.instance().error("hand 扳机状态已变化，但灵巧手未连接")
            return False
        action_kind = "close" if closed else "open"
        try:
            hand_model = self.shared_data.hand.read().name
            with self.CONFIG_PATH.open(encoding="utf-8") as file:
                hand_config = json.load(file)[hand_model]
            # 优先使用设置页保存的动作名称；旧配置没有选择项时使用 close/open。
            action_name = hand_config.get(f"current_{action_kind}", action_kind)
            action = hand_config["actions"][action_name]
            speed = action.get("speed", hand_config.get("default_speed", 255))
            force = action.get("force", hand_config.get("default_force", 255))
            self._execute_action(hand_model, action_name, action["positions"], speed, force,
                                 hand_config["position_range"])
            Logger.instance().info(f"[{hand_model}] 扳机执行 {action_kind}: {action_name}")
            return True
        except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError) as error:
            self.action_buffer.clear()
            Logger.instance().error(f"hand {action_kind} 动作执行失败: {error}")
            return False

    @Slot(str, str, list, int, int)
    def ExecuteTestAction(self, hand_model: str, action_name: str,
                          positions: list, speed: int, force: int) -> bool:
        """执行设置页当前表格中的动作，包括尚未保存的数值。"""
        if self.recording_locked:
            Logger.instance().error("采集期间不能执行灵巧手测试动作")
            return False
        try:
            with self.CONFIG_PATH.open(encoding="utf-8") as file:
                hand_config = json.load(file)[hand_model]
            self._execute_action(hand_model, action_name, positions, speed, force,
                                 hand_config["position_range"])
            Logger.instance().info(f"[{hand_model}] 测试动作成功: {action_name}")
            return True
        except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError) as error:
            self.action_buffer.clear()
            Logger.instance().error(f"[{hand_model}] 测试动作 {action_name} 失败: {error}")
            return False

    def _execute_action(self, hand_model, action_name, positions, speed, force, position_range):
        """在手线程中校验参数并按力矩、速度、位置顺序发送命令。"""
        if not self.if_connected or self.hand is None:
            raise RuntimeError("灵巧手未连接")
        if self.shared_data.hand.read().name != hand_model:
            raise ValueError(f"当前连接的灵巧手不是 {hand_model}")
        if len(positions) != self.hand.MAX_JOINTS():
            raise ValueError(f"动作 {action_name} 的关节数量与 {hand_model} 不一致")
        if any(type(value) is not int or not position_range["min"] <= value <= position_range["max"]
               for value in positions):
            raise ValueError(f"动作 {action_name} 的位置超出配置范围")
        if any(type(value) is not int or not 0 <= value <= 255 for value in (speed, force)):
            raise ValueError(f"动作 {action_name} 的速度或力矩必须是 0～255 的整数")
        if not self.hand.Set_force([force] * len(positions)):
            raise RuntimeError("设置力矩失败")
        if not self.hand.Set_speed([speed] * len(positions)):
            raise RuntimeError("设置速度失败")
        if not self.hand.Set_joint_positions(positions):
            raise RuntimeError("设置关节位置失败")
        self.action_buffer.append(list(positions), monotonic_ns())

    @Slot(bool)
    def SetRecordingLocked(self, locked):
        self.recording_locked = locked
        
