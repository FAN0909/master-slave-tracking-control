from abc import ABC, abstractmethod


class BaseRobotArm(ABC):
    """Abstract base class for robot arm devices.

    This interface defines the common operations required by all robot arm
    implementations, including connection management, enable/disable control,
    state reading, and motion execution.
    """

    def __init__(self, name: str, ip_address: str, port: int):
        self.name = name
        self.ip_address = ip_address
        self.port = port
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

    @abstractmethod
    def Move_j(self, joint_positions: list) -> bool:
        """Move the robot arm to the specified joint positions."""
        pass

    @abstractmethod
    def Move_l(self, tcp_positions: list) -> bool:
        """Move the robot arm in a straight line to the specified TCP positions."""
        pass