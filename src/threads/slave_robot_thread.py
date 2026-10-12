
from PySide6.QtCore import QObject, Signal, Slot,QTimer
from src.devices.base.base_robotArm import BaseRobotArm

class SlaveRobotThread(QObject):

        sig_connect_result = Signal(bool, str)
        sig_disconnect_result = Signal(bool, str)
        sig_enable_result = Signal(bool, str)
        sig_disable_result = Signal(bool, str)
        sig_joint_positions = Signal(list)
        sig_tcp_positions = Signal(list)

        def __init__(self, arm: BaseRobotArm):
            super().__init__()
            self.arm = arm
            self.if_connected = False
            self.if_power_on = False
            self.if_servoj_open = False

            # ServoJ 的目标关节位置
            self.servo_target_positions = None

            self.timer_read_pos = QTimer(self)
            self.timer_read_pos .timeout.connect(self.OnTimerTriggeredReadPos)


        @Slot(int)
        def StartTimer(self, interval_ms: int=20):
            if interval_ms <= 0:
                interval_ms = 20  
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

            self.StopTimer()

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
                self.if_servoj_open = True
                return True
            else:
                return False

        @Slot()
        def CloseServoJ(self) -> bool:
            if self.arm.Close_servoJ():
                self.if_servoj_open = False
                return True
            else:
                return False

        @Slot()
        def MoveJ(self, target_positions: list, speed: float, acceleration: float, deceleration: float) -> bool:
            if self.arm.Move_j(target_positions, speed, acceleration, deceleration):
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


        @Slot(list)
        def AddServoJDelta(self, delta_positions: list):
            """将主手传来的关节增量累加到 ServoJ 目标。"""

            if len(delta_positions) != 7:
                print("ServoJ delta must contain 7 joint values")
                return

            if not self.if_servoj_open:
                return
        
            if self.servo_target_positions is None:
                self.servo_target_positions = self.arm.Get_joint_positions()


            self.servo_target_positions = [
                target + delta
                for target, delta in zip(
                    self.servo_target_positions,
                    delta_positions
                )
            ]
 
            target = list(self.servo_target_positions)
            self.arm.Set_servoJ_pos(target)
