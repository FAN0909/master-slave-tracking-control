from PySide6.QtCore import QObject, Signal, Slot,QTimer
from src.devices.drivers_factory import create_hand
from src.shared_data.robot_share_data import RobotSharedMemory
from src.ui.log_stream import Logger

class HandThread(QObject):
    sig_connect_result = Signal(bool, str)
    sig_disconnect_result = Signal(bool, str)

    def __init__(self, shared_data: RobotSharedMemory):
        super().__init__()
        self.hand = None
        self.shared_data = shared_data
        self.if_connected = False

    @Slot(str, str, str, str)
    def ConnectHand(self, hand_model, hand_type, comm_type, comm_info) -> bool:
        if self.if_connected:
            self.sig_connect_result.emit(False, "请先断开灵巧手，再连接设备")
            return False

        driver_hand_type = "right" if hand_type == "Right Hand" else "left"
        comm_type = comm_type.strip().lower()
        kwargs = {
            "hand_type": driver_hand_type,
            "hand_joint": "O6" if hand_model == "LinkerO6" else hand_model,
        }
        if comm_type in ("modbus", "modebus"):
            kwargs.update(modbus=comm_info, can="None")
        elif comm_type == "can":
            kwargs.update(can=comm_info, modbus="None")

        try:
            self.hand = create_hand(hand_model, **kwargs)
        except Exception as error:
            message = str(error)
            Logger.instance().error(message)
            self.sig_connect_result.emit(False, message)
            return False

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
        if self.hand is None:
            self.sig_disconnect_result.emit(False, "灵巧手驱动尚未创建")
            return False
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
        if self.hand is None:
            Logger.instance().error("灵巧手驱动尚未创建")
            return False
        if self.hand.Set_joint_positions(positions):
            Logger.instance().info(f"[{self.hand.name}] set joint positions successfully")
            return True
        else:
            Logger.instance().error(f"[{self.hand.name}] failed to set joint positions")
            return False

    @Slot(list)
    def Set_speed(self, speed: list) -> bool:
        if self.hand is None:
            Logger.instance().error("灵巧手驱动尚未创建")
            return False
        if self.hand.Set_speed(speed):
            Logger.instance().info(f"[{self.hand.name}] set speed successfully")
            return True
        else:
            Logger.instance().error(f"[{self.hand.name}] failed to set speed")
            return False
        
