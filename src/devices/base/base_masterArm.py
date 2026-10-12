from abc import ABC, abstractmethod

class BaseMasterArm(ABC):
    """Abstract base class for robot arm devices.

    This interface defines the common operations required by all robot arm
    implementations, including connection management, enable/disable 
    """

    def __init__(self, name: str):
        self.name = name
        self.is_connected = False
        self.is_enabled = False

    @abstractmethod
    def Connect(self) -> bool:
        """Connect to the robot arm and return the socket connection."""
        pass

    @abstractmethod
    def Disconnect(self) -> bool:
        """Disconnect from the robot arm."""
        pass

    @abstractmethod
    def Enable(self) -> bool:
        """Enable the robot arm."""
        pass

    @abstractmethod
    def Disable(self) -> bool:
        """Disable the robot arm."""
        pass

    @abstractmethod
    def Get_joint_positions(self) -> list:
        """Read the current joint positions."""
        pass

    @abstractmethod
    def Get_tcp_positions(self) -> list:
        """Read the current TCP positions."""
        pass

