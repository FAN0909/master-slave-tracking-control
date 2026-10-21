import json
from pathlib import Path

from src.ui.log_stream import Logger
from src.devices.base.base_masterArm import BaseMasterArm
from vendor.gello.dynamixel import DynamixelDriver
from typing import Optional, Sequence

class GelloArm(BaseMasterArm):
    CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "master_arm.json"

    def __init__(
        self,
        name: str,
        ids: Optional[Sequence[int]] = None,
        servo_types: Optional[Sequence[str]] = None,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 57600,
        max_retries: int = 3,
        use_fake_fallback: bool = False,
        config_path=None,
    ):
            super().__init__(name)
            self.config_path = Path(config_path) if config_path is not None else self.CONFIG_PATH
            self._load_config(ids)
            self.servo_types = servo_types
            self.port = port
            self.baudrate = baudrate
            self.max_retries = max_retries
            self.use_fake_fallback = use_fake_fallback

            self.dynamixel_driver = None
            self.is_connected = False
            self.is_enabled = False

    def _load_config(self, ids=None):
        """读取主手维度和默认舵机 ID，允许显式传入 ID。"""
        try:
            with self.config_path.open(encoding="utf-8") as file:
                config = json.load(file)["Gello"]
            joint_count = config["MAX_JOINT_COUNT"]
            tcp_dim = config["TCP_DIM"]
            if type(joint_count) is not int or joint_count <= 0:
                raise ValueError("MAX_JOINT_COUNT 必须是正整数")
            if type(tcp_dim) is not int or tcp_dim < 0:
                raise ValueError("TCP_DIM 必须是非负整数")
            joint_ids = list(config["IDS"] if ids is None else ids)
            if len(joint_ids) != joint_count:
                raise ValueError("IDS 数量必须与 MAX_JOINT_COUNT 一致")
            if any(type(value) is not int or not 0 <= value <= 252 for value in joint_ids):
                raise ValueError("IDS 必须是 0 到 252 之间的整数")
            if len(set(joint_ids)) != len(joint_ids):
                raise ValueError("IDS 不得重复")
            self.MAX_JOINT_COUNT = joint_count
            self.TCP_DIM = tcp_dim
            self.ids = joint_ids
        except (OSError, ValueError, KeyError, TypeError) as error:
            message = f"Gello 配置读取失败 ({self.config_path}): {error}"
            Logger.instance().error(message)
            raise ValueError(message) from error

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
            Logger.instance().error(f"[{self.name}] connect failed: {e}")
            self.dynamixel_driver = None
            self.is_connected = False
            return False

    def Disconnect(self) -> bool:
        try:
            if getattr(self, "dynamixel_driver", None) is not None:
                self.dynamixel_driver.close()

            self.dynamixel_driver = None
            self.is_connected = False
            Logger.instance().info(f"[{self.name}] disconnected")
            return True
        except Exception as e:
            Logger.instance().error(f"[{self.name}] disconnect failed: {e}")
            self.dynamixel_driver = None
            self.is_connected = False
            return False

    def Get_joint_positions(self) -> list:
        try:
            pos = self.dynamixel_driver.get_joints()
            if pos is None:
                return [0.0] * self.MAX_JOINT_COUNT

            values = [float(value) for value in pos]
            if len(values) < self.MAX_JOINT_COUNT:
                values.extend([0.0] * (self.MAX_JOINT_COUNT - len(values)))
            elif len(values) > self.MAX_JOINT_COUNT:
                values = values[: self.MAX_JOINT_COUNT]
            return values

        except Exception as e:
            Logger.instance().error(f"[{self.name}] get_current_position error: {e}")
            return [0.0] * self.MAX_JOINT_COUNT


    def Enable(self) -> bool:
        raise NotImplementedError(
            f"[{self.name}] Gello does not support Enable"
        )

    def Disable(self) -> bool:
        raise NotImplementedError(
            f"[{self.name}] Gello does not support Disable"
        )

    def Get_tcp_positions(self) -> list:
        raise NotImplementedError(
            f"[{self.name}] Gello does not provide TCP positions"
        )


