import math

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from src.devices.base.base_masterArm import BaseMasterArm
from src.shared_data.device_feedback import FeedbackStatus
from src.shared_data.capture_ring_buffer import CaptureRingBuffer
from src.shared_data.robot_share_data import MasterState, RobotSharedMemory
from src.ui.log_stream import Logger

class MasterRobotThread(QObject):

        sig_connect_result = Signal(bool, str)
        sig_disconnect_result = Signal(bool, str)
        sig_joint_positions = Signal(list)

        sig_start_timer = Signal(int)
        sig_stop_timer = Signal()

        def __init__(self, arm: BaseMasterArm, shared_data: RobotSharedMemory,
                     capture_buffer: CaptureRingBuffer[MasterState]):
            super().__init__()
            self.arm = arm
            self.shared_data = shared_data
            self.capture_buffer = capture_buffer
            self._last_capture_sequence = 0
            self.reset_shared_positions()
            self.if_connected = False
            self.timer_read_pos = QTimer(self)
            self.timer_read_pos .timeout.connect(self.OnTimerTriggeredReadPos)

        def reset_shared_positions(self):
            self.shared_data.master.update_partial(
                joints=[], tcp=[], feedback=FeedbackStatus(),
            )
            self._last_capture_sequence = 0

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
                self.capture_buffer.clear()
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
                self.capture_buffer.clear()
                self.reset_shared_positions()
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
            if not self.if_connected:
                return
            try:
                sample = self.arm.Read_joint_positions()
            except Exception as error:
                previous = self.shared_data.master.read().feedback
                if previous.error != str(error) or previous.valid:
                    Logger.instance().error(f"[{self.arm.name}] {error}")
                self.shared_data.master.update_partial(
                    joints=[], tcp=[], feedback=previous.failure(error),
                )
                return
            joint_pos_deg = [math.degrees(pos) for pos in sample.values]
            # Gello 不提供 TCP；空列表明确表示缺失，不伪造零位姿。
            state = MasterState(joint_pos_deg, [], self.arm.name, FeedbackStatus.success(sample))
            self.shared_data.master.write(state)
            if sample.sequence == self._last_capture_sequence:
                return
            self.capture_buffer.append(
                state.snapshot(), sample.timestamp_ns,
            )
            self._last_capture_sequence = sample.sequence

            # 发送角度数据
            self.sig_joint_positions.emit(joint_pos_deg)

