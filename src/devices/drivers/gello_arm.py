from src.devices.base.base_robotArm import BaseRobotArm
from vendor.gello.dynamixel import DynamixelDriver
from typing import Optional, Sequence

class GelloArm(BaseRobotArm):
    def __init__(
        self,
        name: str,
        ids: Sequence[int],
        servo_types: Optional[Sequence[str]] = None,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 57600,
        max_retries: int = 3,
        use_fake_fallback: bool = False,
    ):
            super().__init__(name)
            self.ids = ids
            self.servo_types = servo_types
            self.port = port
            self.baudrate = baudrate
            self.max_retries = max_retries
            self.use_fake_fallback = use_fake_fallback

            self.dynamixel_driver = None
            self.is_connected = False
            self.is_enabled = False
            self.MAX_POSITION_SIZE = len(self.ids) if self.ids is not None else 0

    def Connect(self) -> bool:
        try:
            # 这里的调用方式和底层库签名一致，参数名与 __init__ 一一对应
            self.dynamixel_driver = DynamixelDriver(
                ids=self.ids,
                servo_types=self.servo_types,
                port=self.port,
                baudrate=self.baudrate,
                max_retries=self.max_retries,
                use_fake_fallback=self.use_fake_fallback,
            )
            self.is_connected = True
            return True
        except Exception as e:
            print(f"[{self.name}] connect failed: {e}")
            self.dynamixel_driver = None
            self.is_connected = False
            return False

    def Disconnect(self) -> bool:
        try:
            if getattr(self, "dynamixel_driver", None) is not None:
                self.dynamixel_driver.close()

            self.dynamixel_driver = None
            self.is_connected = False
            print(f"[{self.name}] disconnected")
            return True
        except Exception as e:
            print(f"[{self.name}] disconnect failed: {e}")
            self.dynamixel_driver = None
            self.is_connected = False
            return False

    def Get_joint_positions(self) -> list:
        try:
            pos = self.dynamixel_driver.get_joints()
            if pos is None:
                return [0.0] * self.MAX_POSITION_SIZE

            values = [float(value) for value in pos]
            if len(values) < self.MAX_POSITION_SIZE:
                values.extend([0.0] * (self.MAX_POSITION_SIZE - len(values)))
            elif len(values) > self.MAX_POSITION_SIZE:
                values = values[: self.MAX_POSITION_SIZE]
            return values

        except Exception as e:
            print(f"[{self.name}] get_current_position error: {e}")
            return [0.0] * self.MAX_POSITION_SIZE
    

