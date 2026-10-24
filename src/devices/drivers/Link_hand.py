from src.devices.base.base_hand import BaseHand
from src.devices.sdk_feedback_adapters import LinkerO6CanFeedbackAdapter
from src.shared_data.device_feedback import DeviceReadError, FeedbackTracker, validate_positions
from vendor.linkerhand_python_sdk.LinkerHand.linker_hand_api import LinkerHandApi
from src.ui.log_stream import Logger
class LinkHand(BaseHand):
    def __init__(self, name: str,hand_type="left", hand_joint="O6", modbus = "None",can="can0"):
        super().__init__(name)
        self.hand_type = hand_type
        self.hand_joint = hand_joint
        self.modbus = modbus
        self.can = can
        self.is_connected = False
        self.is_enabled = False
        self.hand_api = None  # Placeholder for the actual hand API instance
        self._feedback_adapter = None
        self._feedback = FeedbackTracker(self.MAX_JOINTS(), 0, 255)

    def MAX_JOINTS(self) -> int:
        if (self.hand_joint.upper() == "O6" or self.hand_joint.upper() == "L6"):
            return 6
        elif self.hand_joint.upper() == "L7":
            return 7
        elif self.hand_joint.upper() == "L10":
            return 10
        elif self.hand_joint.upper() == "L20":
            return 20
        elif self.hand_joint.upper() == "G20":
            return 20
        elif self.hand_joint.upper() == "L21":
            return 25
        elif self.hand_joint.upper() == "L25":
            return 25
        return 0

    def Connect(self) -> bool:
        # Implement the connection logic for LinkHandO6
        # For example, establish a serial connection or network connection
        try:
            if self.hand_api is None:
                self.hand_api = LinkerHandApi(hand_type=self.hand_type, hand_joint=self.hand_joint, modbus=self.modbus, can=self.can)
            self._feedback = FeedbackTracker(self.MAX_JOINTS(), 0, 255)
            if self.modbus == "None":
                if self.hand_joint.upper() != "O6":
                    raise DeviceReadError("当前仅实现 O6 CAN 的反馈有效性校验")
                self._feedback_adapter = LinkerO6CanFeedbackAdapter(self.hand_api.hand)
            else:
                self._feedback_adapter = None
            self.is_connected = True
            return True
        except Exception as e:
            Logger.instance().error(f"[{self.name}] connect failed: {e}")
            if self.hand_api is not None:
                self.Disconnect()
            self.is_connected = False
            return False

    def Disconnect(self) -> bool:
        try:
            if self.hand_api is not None:
                backend = self.hand_api.hand
                # SDK close_can() references an undefined `modbus` variable.
                # Close the actual transport, including its CAN receive thread.
                if hasattr(backend, "close_can_interface"):
                    backend.close_can_interface()
                else:
                    backend.close()
                self.hand_api = None
            self._feedback_adapter = None
            self.is_connected = False
            Logger.instance().info(f"[{self.name}] disconnected")
            return True
        except Exception as e:
            Logger.instance().error(f"[{self.name}] disconnect failed: {e}")
            return False

    def Set_joint_positions(self, positions: list) -> bool:
        # Implement the logic to set joint positions for LinkHandO6
        try:
            if not self.is_connected or self.hand_api is None:
                Logger.instance().error(f"[{self.name}] hand API not connected")
                return False

            max_joints = self.MAX_JOINTS()
            if max_joints <= 0:
                Logger.instance().error(f"[{self.name}] unsupported joint type: {self.hand_joint}")
                return False

            values = validate_positions(positions, self.MAX_JOINTS(), 0, 255)
            if any(not value.is_integer() for value in values):
                raise ValueError("灵巧手目标位置必须是整数")
            pos = [int(p) for p in values]
            # True 表示传输层接受指令，不代表机械动作已经完成。
            if self.hand_api.finger_move(pos) is False:
                raise RuntimeError("灵巧手拒绝位置指令")
            return True
        except Exception as e:
            Logger.instance().error(f"[{self.name}] set joint positions failed: {e}")
            return False

    def Read_joint_positions(self):
        """CAN 保留接收包时间，Modbus 使用成功响应时间；不重标旧反馈。"""
        if not self.is_connected or self.hand_api is None:
            raise DeviceReadError("灵巧手未连接")
        try:
            positions = self.hand_api.get_state()
            if self._feedback_adapter is not None:
                return self._feedback_adapter.tracker.read()
            return self._feedback.publish(positions)
        except Exception as error:
            raise DeviceReadError(str(error)) from error

    def Get_joint_positions(self) -> list:
        """兼容列表接口，读取失败返回空列表。"""
        try:
            return list(self.Read_joint_positions().values)
        except DeviceReadError as error:
            Logger.instance().error(f"[{self.name}] get joint positions failed: {error}")
            return []

    def Set_speed(self, speed=None) -> bool:
        # Implement the logic to set speed for LinkHandO6
        try:
            if not self.is_connected or self.hand_api is None:
                raise RuntimeError("灵巧手未连接")
            if speed is None:
                speed = [100] * self.MAX_JOINTS()
            # API 对非法参数只打印错误，封装层先校验再调用。
            values = validate_positions(speed, self.MAX_JOINTS(), 0, 255)
            if any(not value.is_integer() for value in values):
                raise ValueError("灵巧手速度必须是整数")
            if self.hand_api.set_speed([int(value) for value in values]) is False:
                raise RuntimeError("灵巧手拒绝速度指令")
            return True
        except Exception as e:
            Logger.instance().error(f"[{self.name}] set speed failed: {e}")
            return False

    def Set_force(self, force: list) -> bool:
        try:
            if not self.is_connected or self.hand_api is None:
                raise RuntimeError("灵巧手未连接")
            values = validate_positions(force, self.MAX_JOINTS(), 0, 255)
            if any(not value.is_integer() for value in values):
                raise ValueError("灵巧手力矩必须是整数")
            if self.hand_api.set_torque([int(value) for value in values]) is False:
                raise RuntimeError("灵巧手拒绝力矩指令")
            return True
        except Exception as error:
            Logger.instance().error(f"[{self.name}] set force failed: {error}")
            return False
