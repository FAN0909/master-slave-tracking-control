
from PySide6.QtCore import QObject, Signal, Slot,QTimer
from src.devices.base.base_robotArm import BaseRobotArm

class MasterRobotThread(QObject):

        sig_connect_result = Signal(bool, str)
        sig_disconnect_result = Signal(bool, str)
        sig_enable_result = Signal(bool, str)
        sig_disable_result = Signal(bool, str)
        sig_joint_positions = Signal(list)
        sig_tcp_positions = Signal(list)

        sig_start_timer = Signal(int)
        sig_stop_timer = Signal()

        def __init__(self, arm: BaseRobotArm):
            super().__init__()
            self.arm = arm
            self.if_connected = False
            self.if_power_on = False
            self.timer_read_pos = QTimer(self)
            self.timer_read_pos .timeout.connect(self.OnTimerTriggeredReadPos)


        @Slot(int)
        def StartTimer(self, interval_ms: int):
            if interval_ms <= 0:
                interval_ms = 100  
            self.timer_read_pos.start(interval_ms)

        @Slot()
        def StopTimer(self):
            if self.timer_read_pos.isActive():
                self.timer_read_pos.stop()

        def OnTimerTriggeredReadPos(self):
            joint_pos = self.arm.Get_joint_positions()
            tcp_pos = self.arm.Get_tcp_positions()   
            self.sig_joint_positions.emit(joint_pos)
            self.sig_tcp_positions.emit(tcp_pos)

        @Slot()
        def Connect(self) -> bool:     
            if self.arm.Connect():
                self.if_connected = True
                self.sig_connect_result.emit(True, "connected successfully")
                return True
            else:
                self.sig_connect_result.emit(False, "failed to connect")
                return False
            
        @Slot()
        def Disconnect(self) -> bool:
            if self.arm.Disconnect():
                self.if_connected = False
                self.sig_disconnect_result.emit(True, "disconnected successfully")
                return True
            else:
                self.sig_disconnect_result.emit(False, "failed to disconnect")
                return False

        @Slot()
        def Enable(self) -> bool:
            if self.arm.Enable():
                self.if_power_on = True
                self.sig_enable_result.emit(True, "enable successful")
                return True
            else:
                self.sig_enable_result.emit(False, "enable failed")
                return False

        @Slot()
        def Disable(self) -> bool:
            if self.arm.Disable():
                self.if_power_on = False
                self.sig_disable_result.emit(True, "disable successful")
                return True
            else:
                self.sig_disable_result.emit(False, "disable failed")
                return False

        @Slot()
        def OpenServoJ(self) -> bool:
            if self.arm.Open_servoJ():
                return True
            else:
                return False

        @Slot()
        def CloseServoJ(self) -> bool:
            if self.arm.Close_servoJ():
                return True
            else:
                return False
            
        def testservoj(self):
            pos = self.arm.Get_joint_positions()
            if not pos:
                return

            count = 0
            while count < 10:
                pos[0] -= 1.0
                print(f"[{self.arm.name}] test servoJ angle: {pos[0]} deg")
                self.arm.Set_servoJ_pos(pos)
                count += 1


        

