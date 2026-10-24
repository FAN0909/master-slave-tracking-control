"""按固定时间网格读取设备缓存，只使用采样时刻及之前的有效数据。"""

from dataclasses import dataclass
from time import monotonic_ns

import numpy as np

from src.shared_data.device_feedback import validate_positions


FPS = 20
CAMERAS = ("side", "front", "hand")
SOURCE_NAMES = ("master", "slave", "hand", "tcp", "side_camera", "front_camera",
                "hand_camera", "slave_action", "hand_action")


@dataclass(frozen=True)
class AlignedFrame:
    tick_index: int
    timestamp_ns: int
    state: np.ndarray
    action: np.ndarray
    master: np.ndarray
    tcp: np.ndarray
    images: dict[str, np.ndarray]
    source_timestamps_ns: np.ndarray
    source_ages_ms: np.ndarray
    feedback_sequences: np.ndarray

    def arrays(self):
        return {
            "tick_index": np.array([self.tick_index], dtype=np.int64),
            "timestamp_ns": np.array([self.timestamp_ns], dtype=np.int64),
            "state": self.state, "action": self.action, "master": self.master,
            "tcp": self.tcp, "source_timestamps_ns": self.source_timestamps_ns,
            "source_ages_ms": self.source_ages_ms,
            "feedback_sequences": self.feedback_sequences,
            **{f"image_{name}": self.images[name] for name in CAMERAS},
        }


class DataSynchronizer:
    """state 是实测位置，action 是当时已成功下发并保持的绝对目标位置。

    相机最长允许落后 100 ms，状态与机械臂指令最长 150 ms。
    灵巧手目标仅在开合时更新，允许保持，但真实手部反馈仍必须持续刷新。
    """

    def __init__(self, shared_data, master_buffer, slave_buffer, hand_buffer,
                 camera_buffers, slave_action_buffer, hand_action_buffer,
                 health_check=None, fps=FPS):
        if type(fps) is not int or fps <= 0 or 1_000_000_000 % fps:
            raise ValueError("fps 必须为能整除 1 秒纳秒数的正整数")
        self.shared_data = shared_data
        self.buffers = {"master": master_buffer, "slave": slave_buffer, "hand": hand_buffer,
                        "slave_action": slave_action_buffer, "hand_action": hand_action_buffer}
        self.camera_buffers = camera_buffers
        self.health_check = health_check
        self.fps = fps
        self.period_ns = 1_000_000_000 // fps
        self.image_shapes = {}

    @staticmethod
    def _sample(buffer, name, timestamp_ns, max_age_ns):
        sample = buffer.latest_before_or_at(timestamp_ns)
        if sample is None:
            raise RuntimeError(f"{name} 数据缺失：当前采样点之前没有可用样本，请检查设备反馈及跟随状态")
        age_ns = timestamp_ns - sample.timestamp_ns
        if max_age_ns is not None and age_ns > max_age_ns:
            raise RuntimeError(f"{name} 数据过期：最近样本距采样点 {age_ns / 1e6:.1f} ms，"
                               f"允许 {max_age_ns / 1e6:.1f} ms；请检查设备反馈及跟随状态")
        return sample

    def reset(self):
        self.image_shapes = {}

    def align_at(self, timestamp_ns, tick_index):
        if self.health_check:
            error = self.health_check()
            if error:
                raise RuntimeError(error)
        now_ns = monotonic_ns()
        if timestamp_ns > now_ns:
            raise RuntimeError("不能从未来时间点采样")
        for name in ("master", "slave", "hand"):
            status = getattr(self.shared_data, name).read().feedback
            if not status.is_fresh(now_ns=now_ns):
                raise RuntimeError(f"{name} 反馈无效：{status.error or '反馈超时'}")

        samples = {
            name: self._sample(buffer, name, timestamp_ns,
                               None if name == "hand_action" else 150_000_000)
            for name, buffer in self.buffers.items()
        }
        for name in ("master", "slave", "hand"):
            sample = samples[name]
            if (not sample.data.feedback.valid
                    or not 0 <= timestamp_ns - sample.data.feedback.timestamp_ns <= 150_000_000
                    or sample.data.feedback.timestamp_ns > sample.timestamp_ns):
                raise RuntimeError(f"{name} 缓存反馈状态或时间戳无效")

        master = validate_positions(samples["master"].data.joints, 7)
        slave = validate_positions(samples["slave"].data.joints, 7)
        hand = validate_positions(samples["hand"].data.joints, 6, 0, 255)
        tcp = validate_positions(samples["slave"].data.tcp, 6)
        tcp_ns = samples["slave"].data.tcp_timestamp_ns
        if not 0 <= timestamp_ns - tcp_ns <= 150_000_000:
            raise RuntimeError("TCP 反馈缺失、过期或晚于当前采样点")
        arm_action = validate_positions(samples["slave_action"].data, 7)
        hand_action = validate_positions(samples["hand_action"].data, 6, 0, 255)

        images = {}
        for name in CAMERAS:
            sample = self._sample(self.camera_buffers[name], f"{name} 相机", timestamp_ns, 100_000_000)
            image = sample.data
            if (not isinstance(image, np.ndarray) or image.dtype != np.uint8
                    or image.ndim != 3 or image.shape[2] != 3 or min(image.shape[:2]) <= 0
                    or any(dimension % 2 for dimension in image.shape[:2])):
                raise RuntimeError(f"{name} 相机需要宽高为偶数的 H×W×3 uint8 图像")
            if name in self.image_shapes and tuple(image.shape) != self.image_shapes[name]:
                raise RuntimeError(f"{name} 相机在 episode 中改变了分辨率")
            self.image_shapes[name] = tuple(image.shape)
            images[name] = image[:, :, ::-1].copy()  # BGR -> RGB，拥有独立内存。
            samples[f"{name}_camera"] = sample

        timestamps = np.array([
            tcp_ns if name == "tcp" else samples[name].data.feedback.timestamp_ns
            if name in ("master", "slave", "hand") else samples[name].timestamp_ns
            for name in SOURCE_NAMES
        ], dtype=np.int64)
        return AlignedFrame(
            tick_index, timestamp_ns,
            np.asarray(slave + hand, dtype=np.float32),
            np.asarray(arm_action + hand_action, dtype=np.float32),
            np.asarray(master, dtype=np.float32), np.asarray(tcp, dtype=np.float32), images,
            timestamps, ((timestamp_ns - timestamps) / 1e6).astype(np.float32),
            np.asarray([samples[name].data.feedback.sequence for name in ("master", "slave", "hand")],
                       dtype=np.int64),
        )
