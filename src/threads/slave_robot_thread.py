import math
from time import monotonic_ns

from src.ui.log_stream import Logger

from PySide6.QtCore import QObject, Signal, Slot, QTimer, Qt
from src.devices.drivers_factory import create_slave_arm
from src.shared_data.robot_share_data import RobotSharedMemory, SlaveState
from src.shared_data.capture_ring_buffer import CaptureRingBuffer
from src.controller.teleop_controller import MasterSlaveTeleopCalculator
class SlaveRobotThread(QObject):

        sig_connect_result = Signal(bool, str)
        sig_disconnect_result = Signal(bool, str)
        sig_enable_result = Signal(bool, str)
        sig_disable_result = Signal(bool, str)
        sig_joint_positions = Signal(list)
        sig_tcp_positions = Signal(list)
        sig_follow_result = Signal(bool)
        sig_hand_closed_changed = Signal(bool)
        sig_movej_result = Signal(bool, str)

        def __init__(self, shared_data: RobotSharedMemory,
                     capture_buffer: CaptureRingBuffer[SlaveState],
                     action_buffer: CaptureRingBuffer[list[float]]):
            super().__init__()
            self.arm = None
            self.shared_data = shared_data
            self.capture_buffer = capture_buffer
            self.action_buffer = action_buffer
            self.if_connected = False
            self.if_power_on = False
            self.if_servoj_open = False

            # ServoJ 的目标关节位置
            self.servo_target_positions = None

            self.if_running_follow = False
            self.hand_trigger_start_deg = None
            self.hand_trigger_closed = False
            self.hand_close_threshold_deg = 30.0
            self.hand_open_threshold_deg = 25.0
            self._resume_read_timer_interval = None

            self.timer_read_pos = QTimer(self)
            self.timer_read_pos .timeout.connect(self.OnTimerTriggeredReadPos)

            # 跟随控制使用独立周期，不再绑定到从手状态刷新频率。
            self.timer_follow = QTimer(self)
            self.timer_follow.timeout.connect(self.RunFollow)

            self.teleop_controller = MasterSlaveTeleopCalculator(shared_data)

        def reset_shared_positions(self):
            self.shared_data.slave.update_partial(
                joints=[0.0] * self.arm.MAX_JOINT_COUNT,
                tcp=[0.0] * self.arm.TCP_DIM,
            )
            self.shared_data.slave_increment.update_partial(
                delta_joints=[0.0] * self.arm.MAX_JOINT_COUNT,
            )

        @Slot(str, str)
        def ConnectRobot(self, robot_type, ip_address):
            if self.if_connected or self.if_running_follow:
                self.sig_connect_result.emit(False, "请先停止跟随并断开从手，再连接设备")
                return False

            try:
                self.arm = create_slave_arm(robot_type)
            except Exception as error:
                message = str(error)
                Logger.instance().error(message)
                self.sig_connect_result.emit(False, message)
                return False

            self.if_power_on = False
            self.if_servoj_open = False
            self.servo_target_positions = None
            self._resume_read_timer_interval = None
            self.reset_shared_positions()
            return self.Connect(ip_address)


        @Slot(int)
        def StartTimer(self, interval_ms: int=20):
            if interval_ms <= 0:
                interval_ms = 20  
            self.timer_read_pos.start(interval_ms)

        @Slot()
        def StopTimer(self):
            if self.timer_read_pos.isActive():
                self.timer_read_pos.stop()

        def OnTimerTriggeredReadPos(self):
            if not self.if_connected or self.arm is None:
                return
            joint_pos = self.arm.Get_joint_positions()
            tcp_pos = self.arm.Get_tcp_positions()
            sample_timestamp_ns = monotonic_ns()

            self.shared_data.slave.update_partial(joints=joint_pos, tcp=tcp_pos)
            self.capture_buffer.append(
                SlaveState(joints=joint_pos.copy(), tcp=tcp_pos.copy(), name=self.arm.name),
                sample_timestamp_ns,
            )

            self.sig_joint_positions.emit(joint_pos)
            self.sig_tcp_positions.emit(tcp_pos)

        @Slot(str)
        def Connect(self, ip_address: str) -> bool:
            self.arm.ip_address = ip_address
            if self.arm.Connect():
                self.reset_shared_positions()
                self.shared_data.slave.update_partial(name=self.arm.name)
                self.capture_buffer.clear()
                self.action_buffer.clear()
                self.if_connected = True
                self.sig_connect_result.emit(True, "connected successfully")
                return True
            else:
                self.sig_connect_result.emit(False, "failed to connect")
                return False
            
        @Slot()
        def Disconnect(self) -> bool:

            self.StopFollow()
            self.StopTimer()
            if self.if_servoj_open and not self.CloseServoJ():
                self.sig_disconnect_result.emit(False, "关闭 ServoJ 失败，未断开从手")
                return False

            if self.arm.Disconnect():
                self.if_connected = False
                self.if_power_on = False
                self.if_servoj_open = False
                self.servo_target_positions = None
                self.capture_buffer.clear()
                self.action_buffer.clear()
                self.sig_disconnect_result.emit(True, "disconnected successfully")
                return True
            else:
                self.sig_disconnect_result.emit(False, "failed to disconnect")
                return False

        @Slot()
        def Shutdown(self):
            """Stop both timers before this worker's thread exits."""
            self.StopFollow()
            self.StopTimer()
            if self.if_connected:
                self.Disconnect()

        @Slot()
        def Enable(self) -> bool:
            if self.arm.Enable():
                self.if_power_on = True
                self.sig_enable_result.emit(True, "enable successful")
                return True
            else:
                self.sig_enable_result.emit(False, "enable failed")
                return False

        @Slot()
        def Disable(self) -> bool:
            if self.arm.Disable():
                self.if_power_on = False
                self.sig_disable_result.emit(True, "disable successful")
                return True
            else:
                self.sig_disable_result.emit(False, "disable failed")
                return False

        @Slot()
        def OpenServoJ(self) -> bool:
            if self.arm.Open_servoJ():
                self.if_servoj_open = True
                return True
            else:
                return False

        @Slot()
        def CloseServoJ(self) -> bool:
            if self.arm.Close_servoJ():
                self.if_servoj_open = False
                return True
            else:
                return False

        @Slot(list)
        def MoveJ(self, target_positions: list, speed: float = 80,
                  acceleration: float = 80, deceleration: float = 80) -> bool:
            if not self.if_connected or not self.if_power_on or self.arm is None:
                self.sig_movej_result.emit(False, "从手未连接或未上电")
                return False
            if self.if_running_follow:
                self.sig_movej_result.emit(False, "请先停止跟随，再执行 RobotHome")
                return False
            if (len(target_positions) != self.arm.MAX_JOINT_COUNT
                    or any(not isinstance(value, (int, float)) or not math.isfinite(value)
                           for value in target_positions)):
                self.sig_movej_result.emit(False, "Home Pos 关节角度无效")
                return False
            if any(not math.isfinite(value) or value <= 0
                   for value in (speed, acceleration, deceleration)):
                self.sig_movej_result.emit(False, "MoveJ 速度和加减速度必须为正数")
                return False
            try:
                if self.if_servoj_open and not self.CloseServoJ():
                    self.sig_movej_result.emit(False, "关闭 ServoJ 失败，未执行 RobotHome")
                    return False
                success = self.arm.Move_j(target_positions, speed, acceleration, deceleration)
            except Exception as error:
                self.sig_movej_result.emit(False, f"RobotHome 指令失败: {error}")
                return False
            message = "RobotHome 指令已发送" if success else "RobotHome 指令发送失败"
            self.sig_movej_result.emit(success, message)
            return success


        def testservoj(self):
            pos = self.arm.Get_joint_positions()
            if not pos:
                return

            count = 0
            while count < 10:
                pos[0] -= 1.0
                Logger.instance().info(f"[{self.arm.name}] test servoJ angle: {pos[0]} deg")
                self.arm.Set_servoJ_pos(pos)
                count += 1


        @Slot()
        def StartFollow(self, time_interval_ms: int=20):
            """启动主从跟随，只在点击开始时调用一次reset"""
            if self.if_running_follow:
                return

            if not self.if_servoj_open:
                self.OpenServoJ()
            if not self.if_servoj_open:
                Logger.instance().error("ServoJ未打开，无法启动跟随")
                self.sig_follow_result.emit(False)
                return
            # 初始化伺服目标为当前从手位置
            self.servo_target_positions = self.arm.Get_joint_positions()
            # 重置遥操作零点（内部读取当前主手作为基准）
            ok = self.teleop_controller.reset()
            if not ok:
                Logger.instance().error("遥操作重置失败，主手数据无效，无法开启跟随")
                self.sig_follow_result.emit(False)
                return
            if (len(self.teleop_controller.master_start_positions) < 7
                    or not math.isfinite(self.teleop_controller.master_start_positions[6])):
                Logger.instance().error("主手第七关节角度缺失或无效，无法启用 hand 扳机")
                self.sig_follow_result.emit(False)
                return
            self.hand_trigger_start_deg = self.teleop_controller.master_start_positions[6]
            self.hand_trigger_closed = False
            Logger.instance().info(
                f"hand 扳机已校准：松开角度 {self.hand_trigger_start_deg:.2f}°，"
                f"扣下阈值 {self.hand_close_threshold_deg:g}°，"
                f"松开阈值 {self.hand_open_threshold_deg:g}°"
            )
            if time_interval_ms <= 0:
                time_interval_ms = 20
            self.if_running_follow = True
            self.timer_follow.start(time_interval_ms)
            self.sig_hand_closed_changed.emit(False)
            self.sig_follow_result.emit(True)

            Logger.instance().info("主从跟随开启")

        @Slot()
        def StopFollow(self):
            """停止跟随"""
            self.if_running_follow = False
            self.hand_trigger_start_deg = None
            self.hand_trigger_closed = False
            self.timer_follow.stop()
            self.sig_follow_result.emit(False)

            Logger.instance().info("🛑 主从跟随关闭")

        @Slot()
        def SyncHandTriggerState(self):
            """灵巧手在跟随期间连接时，补发当前扳机状态。"""
            if self.if_running_follow and self.hand_trigger_start_deg is not None:
                self.sig_hand_closed_changed.emit(self.hand_trigger_closed)

        @Slot()
        def RunFollow(self):
            if not self.if_running_follow:
                return

            # 同一份主手快照同时用于从手跟随和第七轴扳机判断。
            master_joints = self.shared_data.master.read().joints
            delta = self.teleop_controller.compute_increment(master_joints)
            # 启动跟随时记录的第七轴角度是扳机“松开”位置；读数无效时跳过本次判断。
            if (self.hand_trigger_start_deg is not None and len(master_joints) >= 7
                    and math.isfinite(master_joints[6])):
                # 取绝对值：无论扣动时角度增大还是减小，都按离开松开位置的幅度判断。
                travel_deg = abs(master_joints[6] - self.hand_trigger_start_deg)
                # 原本松开，且扣动幅度达到闭合阈值时，只发一次 True 给 hand 线程。
                if not self.hand_trigger_closed and travel_deg >= self.hand_close_threshold_deg:
                    self.hand_trigger_closed = True
                    self.sig_hand_closed_changed.emit(True)
                    Logger.instance().info(f"hand 扳机扣下：第七轴变化 {travel_deg:.2f}°")
                # 原本闭合，且扳机回到释放阈值以内时，只发一次 False。
                # 闭合阈值大于释放阈值，中间区域保持原状态，避免临界位置反复开合。
                elif self.hand_trigger_closed and travel_deg <= self.hand_open_threshold_deg:
                    self.hand_trigger_closed = False
                    self.sig_hand_closed_changed.emit(False)
                    Logger.instance().info(f"hand 扳机松开：第七轴变化 {travel_deg:.2f}°")
            if self.servo_target_positions is None:
                self.servo_target_positions = self.arm.Get_joint_positions()
            # 叠加增量
            self.servo_target_positions = [
                target + d
                for target, d in zip(self.servo_target_positions, delta)
            ]
            target = list(self.servo_target_positions)
            if self.arm.Set_servoJ_pos(target):
                self.action_buffer.append(target.copy(), monotonic_ns())
