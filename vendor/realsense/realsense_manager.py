try:
    import pyrealsense2 as rs
except ImportError:  # pragma: no cover - runtime fallback for systems without the package
    rs = None

import numpy as np


class RealSenseManager:
    def __init__(self):
        self.pipeline = None
        self.config = None

    def connect(self):
        if rs is None:
            raise RuntimeError(
                "未检测到 pyrealsense2。请先安装 Intel RealSense SDK / Python 包。"
            )

        if self.pipeline is not None:
            return

        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        pipeline.start(config)
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

    def get_color_frame(self) -> np.ndarray | None:
        """返回一帧 BGR8 图像；未连接或没有新帧时返回 None。"""
        if self.pipeline is None:
            return None

        # 非阻塞轮询，调用方可以按自己的频率获取最新帧。
        frames = self.pipeline.poll_for_frames()
        if not frames:
            return None

        color_frame = frames.get_color_frame()
        if not color_frame:
            return None

        # SDK 帧缓冲区可能随帧对象释放而失效，交给上层独立的数组。
        return np.asanyarray(color_frame.get_data()).copy()
