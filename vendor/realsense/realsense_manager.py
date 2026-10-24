try:
    import pyrealsense2 as rs
except ImportError:  # pragma: no cover - runtime fallback for systems without the package
    rs = None

import numpy as np
from time import monotonic_ns, time_ns


class RealSenseManager:
    def __init__(self):
        self.pipeline = None
        self.config = None

    def list_devices(self):
        if rs is None:
            raise RuntimeError(
                "未检测到 pyrealsense2。请先安装 Intel RealSense SDK / Python 包。"
            )

        return [
            (device.get_info(rs.camera_info.name),
             device.get_info(rs.camera_info.serial_number))
            for device in rs.context().query_devices()
        ]
    
    def connect(self, serial_number: str | None = None):
        if rs is None:
            raise RuntimeError(
                "未检测到 pyrealsense2。请先安装 Intel RealSense SDK / Python 包。"
            )

        if self.pipeline is not None:
            return

        pipeline = rs.pipeline()
        config = rs.config()
        if serial_number:
            config.enable_device(serial_number)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        profile = pipeline.start(config)
        for sensor in profile.get_device().query_sensors():
            if sensor.supports(rs.option.global_time_enabled):
                try:
                    sensor.set_option(rs.option.global_time_enabled, 1)
                except RuntimeError:
                    pass  # 某些设备不支持全局时钟，逐帧记录 fallback 来源。
        self.pipeline = pipeline
        self.config = config

    def disconnect(self):
        if self.pipeline is not None:
            try:
                self.pipeline.stop()
            except Exception:
                pass
        self.pipeline = None
        self.config = None

    def is_connected(self):
        return self.pipeline is not None

    def get_color_sample(self):
        """返回 BGR 图像、映射到单调时钟的采集时间及时间戳来源。"""
        if self.pipeline is None:
            return None

        # 非阻塞轮询，调用方可以按自己的频率获取最新帧。
        frames = self.pipeline.poll_for_frames()
        if not frames:
            return None

        color_frame = frames.get_color_frame()
        if not color_frame:
            return None

        arrival_ns = monotonic_ns()
        domain = color_frame.get_frame_timestamp_domain()
        if domain in (rs.timestamp_domain.global_time, rs.timestamp_domain.system_time):
            timestamp_ns = int(color_frame.get_timestamp() * 1_000_000) + arrival_ns - time_ns()
            if timestamp_ns < 0 or timestamp_ns > arrival_ns + 5_000_000:
                return None  # 全局时钟尚未收敛时，不把错误时间戳伪装成新帧。
            # 全局时钟的微小估计误差不能制造未来样本。
            timestamp_ns = min(timestamp_ns, arrival_ns)
            source = f"realsense_{domain.name}"
        else:
            timestamp_ns, source = arrival_ns, "host_arrival"
        # SDK 内存随帧对象释放，必须复制后才能交给采集和预览线程。
        return np.asanyarray(color_frame.get_data()).copy(), timestamp_ns, source

    def get_color_frame(self) -> np.ndarray | None:
        sample = self.get_color_sample()
        return sample[0] if sample else None
