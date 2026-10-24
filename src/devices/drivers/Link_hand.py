import math
from time import monotonic_ns

from src.devices.base.base_hand import BaseHand
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

            self.is_connected = True
            return True
        except Exception as e:
            Logger.instance().error(f"[{self.name}] connect failed: {e}")
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
            self.is_connected = False
            Logger.instance().info(f"[{self.name}] disconnected")
            return True
        except Exception as e:
            Logger.instance().error(f"[{self.name}] disconnect failed: {e}")
            return False

    def Set_joint_positions(self, positions: list) -> bool:
        # Implement the logic to set joint positions for LinkHandO6
        try:
            if self.hand_api is None:
                Logger.instance().error(f"[{self.name}] hand API not connected")
                return False

            max_joints = self.MAX_JOINTS()
            if max_joints <= 0:
                Logger.instance().error(f"[{self.name}] unsupported joint type: {self.hand_joint}")
                return False

            pos = [int(p) for p in positions]
            if len(pos) != max_joints:
                Logger.instance().error(
                    f"[{self.name}] joint count mismatch: expected {max_joints}, got {len(pos)}"
                )
                return False

            self.hand_api.finger_move(pos)
            return True
        except Exception as e:
            Logger.instance().error(f"[{self.name}] set joint positions failed: {e}")
            return False

    def Get_joint_sample(self):
        """返回关节位置与实际反馈时间；读取失败时返回 None。"""
        if not self.is_connected or self.hand_api is None:
            Logger.instance().error(f"[{self.name}] hand API not connected")
            return None

        try:
            backend = self.hand_api.hand
            if hasattr(backend, "get_current_status_sample"):
                positions, timestamp_ns = backend.get_current_status_sample()
            else:
                positions = self.hand_api.get_state()
                timestamp_ns = monotonic_ns()
            if positions is None:
                raise ValueError("SDK returned no joint positions")
            joint_positions = [float(value) for value in positions]
            if len(joint_positions) != self.MAX_JOINTS() or not all(
                math.isfinite(value) and 0 <= value <= 255 for value in joint_positions
            ):
                raise ValueError(f"invalid joint positions: {joint_positions}")
            return joint_positions, timestamp_ns
        except Exception as error:
            Logger.instance().error(f"[{self.name}] get joint positions failed: {error}")
            return None

    def Get_joint_positions(self) -> list:
        sample = self.Get_joint_sample()
        return sample[0] if sample else []

    def Set_speed(self, speed=[100]*5) -> bool:
        # Implement the logic to set speed for LinkHandO6
        try:
            # Set speed logic here
            speed_values = speed
            self.hand_api.set_speed(speed_values)
            return True
        except Exception as e:
            Logger.instance().error(f"[{self.name}] set speed failed: {e}")
            return False

    def Set_force(self, force: list) -> bool:
        try:
            if self.hand_api is None or len(force) != self.MAX_JOINTS():
                return False
            self.hand_api.set_torque(force)
            return True
        except Exception as error:
            Logger.instance().error(f"[{self.name}] set force failed: {error}")
            return False
