"""保存带时间戳的采集数据，供设备线程和采集线程共享。"""

from collections import deque
from dataclasses import dataclass
from threading import Lock
from time import monotonic_ns
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class CaptureSample(Generic[T]):
    """一条采集样本：单调时钟时间戳（纳秒）和对应的数据。"""

    timestamp_ns: int
    data: T


class CaptureRingBuffer(Generic[T]):
    """线程安全的定长环形缓存，容量满时覆盖最早写入的样本。

    数据对象按引用保存，不会自动复制。调用方写入后不要再修改数据；
    如果相机帧底层内存会被复用，应在写入前先复制帧。
    """

    def __init__(self, capacity: int):
        """创建缓存；capacity 是最多保留的样本数，必须为正整数。"""
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self._samples: deque[CaptureSample[T]] = deque(maxlen=capacity)
        self._lock = Lock()
        self._dropped_count = 0

    @property
    def capacity(self) -> int:
        """返回缓存能同时保留的最大样本数。"""
        return self._samples.maxlen

    @property
    def dropped_count(self) -> int:
        """返回因缓存已满而被覆盖的样本数；clear() 后重新计数。"""
        with self._lock:
            return self._dropped_count

    def __len__(self) -> int:
        """返回当前缓存中的样本数，可用 len(buffer) 调用。"""
        with self._lock:
            return len(self._samples)

    def append(self, data: T, timestamp_ns: int | None = None) -> CaptureSample[T]:
        """写入数据并返回样本；满容量时自动覆盖最早写入的样本。

        timestamp_ns 为单调时钟时间戳，单位纳秒；省略时使用写入时的
        time.monotonic_ns()。显式传入时应与查询使用同一个时钟。
        """
        if timestamp_ns is None:
            timestamp_ns = monotonic_ns()
        if isinstance(timestamp_ns, bool) or not isinstance(timestamp_ns, int) or timestamp_ns < 0:
            raise ValueError("timestamp_ns must be a non-negative integer")
        sample = CaptureSample(timestamp_ns=timestamp_ns, data=data)
        with self._lock:
            if len(self._samples) == self.capacity:
                self._dropped_count += 1
            self._samples.append(sample)
        return sample

    def latest(self) -> CaptureSample[T] | None:
        """返回最后写入的样本；缓存为空时返回 None。"""
        with self._lock:
            return self._samples[-1] if self._samples else None

    def closest(self, timestamp_ns: int, max_delta_ns: int | None = None) -> CaptureSample[T] | None:
        """按时间戳查找距离 timestamp_ns 最近的样本。

        max_delta_ns 是允许的最大时间差，单位纳秒；省略时不限制。
        缓存为空或最近样本超过该时间差时返回 None。距离相同则优先返回
        时间戳较早的样本。查找不会从缓存中移除样本。
        """
        if max_delta_ns is not None and max_delta_ns < 0:
            raise ValueError("max_delta_ns must be non-negative")
        with self._lock:
            if not self._samples:
                return None
            sample = min(self._samples, key=lambda item: (abs(item.timestamp_ns - timestamp_ns), item.timestamp_ns))
            if max_delta_ns is not None and abs(sample.timestamp_ns - timestamp_ns) > max_delta_ns:
                return None
            return sample

    def clear(self) -> None:
        """清空所有样本，并将覆盖计数归零。"""
        with self._lock:
            self._samples.clear()
            self._dropped_count = 0
