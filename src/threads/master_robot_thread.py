
from PySide6.QtCore import QObject, Signal, Slot
from src.devices.base.base_robotArm import BaseRobotArm

class MasterRobotThread(QObject):
        def __init__(self, arm: BaseRobotArm):
            super().__init__()
            self.arm = arm
            self.If_Connected = False
            self.If_PowerOn = False

            self.sig_connect_result = Signal(bool, str)
            self.sig_enable_result = Signal(bool, str)


        def Connect(self) -> bool:     
            if self.arm.Connect():
                self.If_Connected = True
                return True
            else:
                return False

        def Disconnect(self) -> bool:
            if self.arm.Disconnect():
                self.If_Connected = False
                return True
            else:
                return False

        def Enable(self) -> bool:
            if self.arm.Enable():
                self.If_PowerOn = True
                return True
            else:
                return False

        def Disable(self) -> bool:
            if self.arm.Disable():
                self.If_PowerOn = False
                return True
            else:
                return False

