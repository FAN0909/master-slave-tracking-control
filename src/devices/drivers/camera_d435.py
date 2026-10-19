import numpy as np

from src.devices.base.base_camera import BaseCamera
from src.ui.log_stream import Logger
from vendor.realsense.realsense_manager import RealSenseManager


class CameraD435(BaseCamera):
    """Intel RealSense D435 彩色相机驱动。"""

    def __init__(self, name: str):
        super().__init__(name)
        self.camera_manager = RealSenseManager()

    def Connect(self) -> bool:
        if self.is_connected:
            return True
        try:
            self.camera_manager.connect()
            self.is_connected = self.camera_manager.is_connected()
            if not self.is_connected:
                Logger.instance().error(f"[{self.name}] connect failed: camera is not connected")
            return self.is_connected
        except Exception as error:
            Logger.instance().error(f"[{self.name}] connect failed: {error}")
            self.is_connected = False
            return False

    def Disconnect(self) -> bool:
        try:
            self.camera_manager.disconnect()
            self.is_connected = False
            Logger.instance().info(f"[{self.name}] disconnected")
            return True
        except Exception as error:
            Logger.instance().error(f"[{self.name}] disconnect failed: {error}")
            self.is_connected = self.camera_manager.is_connected()
            return False

    def Get_color_frame(self) -> np.ndarray | None:
        if not self.is_connected:
            return None
        try:
            return self.camera_manager.get_color_frame()
        except Exception as error:
            Logger.instance().error(f"[{self.name}] get color frame failed: {error}")
            return None
