from PySide6.QtCore import QObject, Signal, Slot,QTimer
from src.devices.base.base_robotArm import BaseRobotArm
from src.shared_data.robot_share_data import RobotSharedMemory

import math

class MasterRobotThread(QObject):

        sig_connect_result = Signal(bool, str)
        sig_disconnect_result = Signal(bool, str)
        sig_joint_positions = Signal(list)

        sig_start_timer = Signal(int)
        sig_stop_timer = Signal()

        def __init__(self, arm: BaseRobotArm, shared_data: RobotSharedMemory):
            super().__init__()
            self.arm = arm
            self.shared_data = shared_data
            self.reset_shared_positions()
            self.if_connected = False
            self.timer_read_pos = QTimer(self)
            self.timer_read_pos .timeout.connect(self.OnTimerTriggeredReadPos)

        def reset_shared_positions(self):
            self.shared_data.master.update_partial(
                joints=[0.0] * self.arm.MAX_JOINT_COUNT,
                tcp=[0.0] * self.arm.TCP_DIM,
            )

        @Slot(int)
        def StartTimer(self, interval_ms: int =20):
            if interval_ms <= 0:
                interval_ms = 20  
            self.timer_read_pos.start(interval_ms)

        @Slot()
        def StopTimer(self):
            if self.timer_read_pos.isActive():
                self.timer_read_pos.stop()


        @Slot()
        def Connect(self) -> bool:     
            if self.arm.Connect():
                self.reset_shared_positions()
                self.shared_data.master.update_partial(name=self.arm.name)
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
        def Shutdown(self):
            """Stop polling and release the arm in this worker's thread."""
            self.StopTimer()
            if self.if_connected:
                self.Disconnect()


        def OnTimerTriggeredReadPos(self):
            # 获取主手关节位置（弧度）
            joint_pos = self.arm.Get_joint_positions()

            # 弧度转换为角度
            joint_pos_deg = [
                math.degrees(pos)
                for pos in joint_pos
            ]
            self.shared_data.master.update_partial(joints=joint_pos_deg, tcp=[0.0] * self.arm.TCP_DIM)

            # 发送角度数据
            self.sig_joint_positions.emit(joint_pos_deg)

