from PySide6.QtCore import QObject, QTimer, Signal, Slot
from time import monotonic_ns
import numpy as np
from numpy import ndarray

from src.devices.drivers_factory import create_camera
from src.shared_data.capture_ring_buffer import CaptureRingBuffer
from src.shared_data.device_feedback import FeedbackStatus, DEFAULT_MAX_AGE_NS
from src.ui.log_stream import Logger


class CameraThread(QObject):
    """相机工作对象，在所属线程中连接设备并定时读取彩色帧。"""

    sig_connect_result = Signal(bool, str)
    sig_disconnect_result = Signal(bool, str)
    sig_color_frame = Signal(object)  # BGR8 numpy.ndarray，形状为 (高, 宽, 3)

    def __init__(self, capture_buffer: CaptureRingBuffer[ndarray]):
        super().__init__()
        self.camera = None
        self.capture_buffer = capture_buffer
        self.if_connected = False
        self.feedback_status = FeedbackStatus()
        self.timer_read_frame = QTimer(self)
        self.timer_read_frame.timeout.connect(self.OnTimerTriggeredReadFrame)

    @Slot(str, str, int)
    def ConnectCamera(self, camera_type: str, serial_number: str, interval_ms: int =20) -> bool:
        if self.if_connected:
            self.sig_connect_result.emit(False, "Disconnect this camera before connecting another device")
            return False

        try:
            camera = create_camera(camera_type, serial_number=serial_number)
            if not camera.Connect():
                message = f"[{camera.name}] failed to connect"
                Logger.instance().error(message)
                self.sig_connect_result.emit(False, message)
                return False
        except Exception as error:
            message = f"Camera connection failed: {error}"
            Logger.instance().error(message)
            self.sig_connect_result.emit(False, message)
            return False

        self.camera = camera
        self.if_connected = True
        self.capture_buffer.clear()
        self.feedback_status = FeedbackStatus()
        self.StartTimer(interval_ms)
        message = f"[{camera.name}] connected successfully"
        Logger.instance().info(message)
        self.sig_connect_result.emit(True, message)
        return True

    @Slot()
    def Disconnect(self) -> bool:
        self.StopTimer()
        if self.camera is None or not self.if_connected:
            self.sig_disconnect_result.emit(False, "Camera is not connected")
            return False

        try:
            if not self.camera.Disconnect():
                message = f"[{self.camera.name}] failed to disconnect"
                Logger.instance().error(message)
                self.sig_disconnect_result.emit(False, message)
                return False
        except Exception as error:
            message = f"[{self.camera.name}] disconnect failed: {error}"
            Logger.instance().error(message)
            self.sig_disconnect_result.emit(False, message)
            return False

        name = self.camera.name
        self.camera = None
        self.if_connected = False
        self.capture_buffer.clear()
        self.feedback_status = FeedbackStatus()
        message = f"[{name}] disconnected successfully"
        Logger.instance().info(message)
        self.sig_disconnect_result.emit(True, message)
        return True

    @Slot()
    def Shutdown(self):
        """Release the camera in its own thread before the event loop exits."""
        self.StopTimer()
        if self.if_connected:
            self.Disconnect()

    @Slot(int)
    def StartTimer(self, interval_ms: int = 20) -> bool:
        if not self.if_connected:
            Logger.instance().error("Camera is not connected; cannot start frame capture")
            return False
        self.timer_read_frame.start(interval_ms if interval_ms > 0 else 20)
        return True

    @Slot()
    def StopTimer(self):
        if self.timer_read_frame.isActive():
            self.timer_read_frame.stop()

    @Slot()
    def OnTimerTriggeredReadFrame(self):
        if not self.if_connected or self.camera is None:
            return
        try:
            frame = self.camera.Get_color_frame()
        except Exception as error:
            self._invalidate_feedback(error)
            return
        if frame is None:
            # 相机 30 FPS、轮询 20 ms 时没有新帧属于正常情况。
            if (self.feedback_status.valid
                    and not self.feedback_status.is_fresh(DEFAULT_MAX_AGE_NS)):
                self._invalidate_feedback("相机帧已超时")
            return
        if (not isinstance(frame, ndarray) or frame.dtype != np.uint8
                or frame.ndim != 3 or frame.shape[2] != 3
                or frame.shape[0] == 0 or frame.shape[1] == 0):
            self._invalidate_feedback("相机帧必须是非空的 H×W×3 uint8 BGR 图像")
            return
        # 缓存拥有独立内存，不能随驱动下一次采样而被修改。
        frame = frame.copy()
        timestamp_ns = monotonic_ns()
        self.feedback_status = FeedbackStatus(
            True, timestamp_ns, self.feedback_status.sequence + 1, "",
        )
        self.capture_buffer.append(frame, timestamp_ns)
        self.sig_color_frame.emit(frame)

    def _invalidate_feedback(self, error):
        if self.feedback_status.valid or self.feedback_status.error != str(error):
            Logger.instance().error(f"[{self.camera.name}] {error}")
        self.feedback_status = self.feedback_status.failure(error)
        self.capture_buffer.clear()
