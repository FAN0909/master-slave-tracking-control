
from PySide6.QtCore import QObject, Signal, Slot
from src.devices.base.base_robotArm import BaseRobotArm

class MasterRobotThread(QObject):

        sig_connect_result = Signal(bool, str)
        sig_disconnect_result = Signal(bool, str)
        sig_enable_result = Signal(bool, str)
        sig_disable_result = Signal(bool, str)

        def __init__(self, arm: BaseRobotArm):
            super().__init__()
            self.arm = arm
            self.if_connected = False
            self.if_power_on = False


        def Connect(self) -> bool:     
            if self.arm.Connect():
                self.if_connected = True
                self.sig_connect_result.emit(True, "连接成功")
                return True
            else:
                self.sig_connect_result.emit(False, "连接失败")
                return False

        def Disconnect(self) -> bool:
            if self.arm.Disconnect():
                self.if_connected = False
                self.sig_disconnect_result.emit(True, "断开连接成功")
                return True
            else:
                self.sig_disconnect_result.emit(False, "断开连接失败")  
                return False

        def Enable(self) -> bool:
            if self.arm.Enable():
                self.if_power_on = True
                self.sig_enable_result.emit(True, "使能成功")
                return True
            else:
                self.sig_enable_result.emit(False, "使能失败")
                return False

        def Disable(self) -> bool:
            if self.arm.Disable():
                self.if_power_on = False
                self.sig_disable_result.emit(True, "禁用成功")
                return True
            else:
                self.sig_disable_result.emit(False, "禁用失败")
                return False

