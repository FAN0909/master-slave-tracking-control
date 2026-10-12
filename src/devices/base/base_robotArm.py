from abc import ABC, abstractmethod


class BaseRobotArm(ABC):
    """Abstract base class for robot arm devices.

    This interface defines the common operations required by all robot arm
    implementations, including connection management, enable/disable control,
    state reading, and motion execution.
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

    @abstractmethod
    def Move_j(
        self,
        target_positions: list,
        speed: float,
        acceleration: float,
        deceleration: float
    ) -> bool:
        """Move the robot arm in joint space."""
        pass

    @abstractmethod
    def Move_l(
        self,
        target_positions: list,
        speed: float,
        acceleration: float,
        deceleration: float
    ) -> bool:
        """Move the robot arm in Cartesian space."""
        pass

    @abstractmethod
    def Open_servoJ(self) -> bool:
        """Open the servo control."""
        pass

    @abstractmethod
    def Close_servoJ(self) -> bool:
        """Close the servo control."""
        pass
    
    @abstractmethod
    def Set_servoJ_pos(self,target_positions: list,) -> bool:
        """Set the servo control to a specific position."""
        pass