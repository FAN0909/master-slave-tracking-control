from abc import ABC, abstractmethod
import numpy as np
class BaseCamera(ABC):
    """Abstract base class for Camera devices.

    This interface defines the common operations required by all Camera
    implementations, including connection management,
    """

    def __init__(self, name: str):
        self.name = name
        self.is_connected = False
        self.is_enabled = False

    @abstractmethod
    def Connect(self) -> bool:
        """Connect to the camera."""
        pass

    @abstractmethod
    def Disconnect(self) -> bool:
        """Disconnect from the camera."""
        pass

    @abstractmethod
    def Get_color_frame(self) -> np.ndarray | None:
        """获取一帧 BGR8 彩色图像，形状为 (高, 宽, 3)。

        尚未连接或当前没有新帧时返回 None。
        """
        raise NotImplementedError
