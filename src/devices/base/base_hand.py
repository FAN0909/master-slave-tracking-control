from abc import ABC, abstractmethod

class BaseHand(ABC):
    """Abstract base class for Hand devices.

    This interface defines the common operations required by all Hand
    implementations, including connection management,
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
    def Set_joint_positions(self, positions: list) -> bool:
        """Set the joint positions."""
        pass

    @abstractmethod
    def Set_speed(self, speed: float) -> bool:
        """Set the speed of the hand."""
        pass

    @abstractmethod
    def Get_joint_positions(self) -> list:
        """get joints pos."""
        pass

