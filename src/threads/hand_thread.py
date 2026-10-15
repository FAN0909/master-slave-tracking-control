from PySide6.QtCore import QObject, Signal, Slot,QTimer
from src.devices.base.base_hand import BaseHand
from src.shared_data.robot_share_data import RobotSharedMemory
from src.ui.log_stream import Logger

class HandThread(QObject):
    sig_connect_result = Signal(bool, str)
    sig_disconnect_result = Signal(bool, str)

    def __init__(self, hand: BaseHand, shared_data: RobotSharedMemory):
        super().__init__()
        self.hand = hand
        self.shared_data = shared_data
        self.if_connected = False
   
    @Slot()
    def Connect(self) -> bool:
        if self.hand.Connect():
            Logger.instance().info(f"[{self.hand.name}] connected successfully")
            self.if_connected = True
            self.sig_connect_result.emit(True, f"[{self.hand.name}] connected successfully")
            return True
        else:
            self.sig_connect_result.emit(False, f"[{self.hand.name}] failed to connect")
            Logger.instance().error(f"[{self.hand.name}] failed to connect")
            return False

    @Slot()
    def Disconnect(self) -> bool:
        if self.hand.Disconnect():
            Logger.instance().info(f"[{self.hand.name}] disconnected successfully")
            self.if_connected = False
            self.sig_disconnect_result.emit(True, f"[{self.hand.name}] disconnected successfully")
            return True
        else:
            self.sig_disconnect_result.emit(False, f"[{self.hand.name}] failed to disconnect")
            Logger.instance().error(f"[{self.hand.name}] failed to disconnect")
            return False
        
    @Slot(list)
    def Set_joint_positions(self, positions: list) -> bool:
        if self.hand.Set_joint_positions(positions):
            Logger.instance().info(f"[{self.hand.name}] set joint positions successfully")
            return True
        else:
            Logger.instance().error(f"[{self.hand.name}] failed to set joint positions")
            return False

    @Slot(list)
    def Set_speed(self, speed: list) -> bool:
        if self.hand.Set_speed(speed):
            Logger.instance().info(f"[{self.hand.name}] set speed successfully")
            return True
        else:
            Logger.instance().error(f"[{self.hand.name}] failed to set speed")
            return False
        
