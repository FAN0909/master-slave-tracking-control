from PySide6.QtCore import QObject, QTimer, Signal, Slot
from numpy import ndarray

from src.devices.drivers_factory import create_camera
from src.shared_data.capture_ring_buffer import CaptureRingBuffer
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
        self.timer_read_frame = QTimer(self)
        self.timer_read_frame.timeout.connect(self.OnTimerTriggeredReadFrame)

    @Slot(str, str, int)
    def ConnectCamera(self, camera_type: str, serial_number: str, interval_ms: int) -> bool:
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
            Logger.instance().error(f"[{self.camera.name}] get color frame failed: {error}")
            return
        if frame is not None:
            self.capture_buffer.append(frame)
            self.sig_color_frame.emit(frame)
