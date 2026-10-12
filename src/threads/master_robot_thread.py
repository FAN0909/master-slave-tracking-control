from PySide6.QtCore import QObject, Signal, Slot,QTimer
from src.devices.base.base_robotArm import BaseRobotArm
import math

class MasterRobotThread(QObject):

        sig_connect_result = Signal(bool, str)
        sig_disconnect_result = Signal(bool, str)
        sig_joint_positions = Signal(list)

        sig_start_timer = Signal(int)
        sig_stop_timer = Signal()

        def __init__(self, arm: BaseRobotArm):
            super().__init__()
            self.arm = arm
            self.if_connected = False
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


        def OnTimerTriggeredReadPos(self):
            # 获取主手关节位置（弧度）
            joint_pos = self.arm.Get_joint_positions()

            # 弧度转换为角度
            joint_pos_deg = [
                math.degrees(pos)
                for pos in joint_pos
            ]

            # 发送角度数据
            self.sig_joint_positions.emit(joint_pos_deg)

