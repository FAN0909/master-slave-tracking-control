"""设备反馈的校验、时间戳和有效性；不以补零代替读取失败。"""

from dataclasses import dataclass
from math import isfinite
from numbers import Real
from threading import Lock
from time import monotonic_ns


DEFAULT_MAX_AGE_NS = 500_000_000


class DeviceReadError(RuntimeError):
    """设备没有返回可使用的真实反馈。"""


def validate_positions(values, count, minimum=None, maximum=None):
    """要求维度准确、数值有限；合法的全零位置仍然有效。"""
    if values is None:
        raise DeviceReadError("设备未返回位置")
    try:
        values = tuple(values)
    except TypeError as error:
        raise DeviceReadError("位置必须是一维数值序列") from error
    if len(values) != count:
        raise DeviceReadError(f"位置维度错误：期望 {count}，实际 {len(values)}")
    if any(isinstance(value, bool) or not isinstance(value, Real)
           or not isfinite(value) for value in values):
        raise DeviceReadError("位置包含非数值、NaN 或 Inf")
    if any((minimum is not None and value < minimum)
           or (maximum is not None and value > maximum) for value in values):
        raise DeviceReadError(f"位置超出范围 {minimum}～{maximum}")
    return tuple(float(value) for value in values)


@dataclass(frozen=True)
class PositionFeedback:
    values: tuple[float, ...]
    timestamp_ns: int
    sequence: int


@dataclass(frozen=True)
class FeedbackStatus:
    valid: bool = False
    timestamp_ns: int = 0
    sequence: int = 0
    error: str = "尚未收到有效反馈"

    @classmethod
    def success(cls, sample):
        return cls(True, sample.timestamp_ns, sample.sequence, "")

    def failure(self, error):
        return FeedbackStatus(False, self.timestamp_ns, self.sequence, str(error))

    def is_fresh(self, max_age_ns=DEFAULT_MAX_AGE_NS, now_ns=None):
        if now_ns is None:
            now_ns = monotonic_ns()
        return self.valid and 0 <= now_ns - self.timestamp_ns <= max_age_ns


class FeedbackTracker:
    """由 SDK 收到新反馈时更新；重复读取不会改变时间戳或序号。"""

    def __init__(self, count, minimum=None, maximum=None):
        self.count = count
        self.minimum = minimum
        self.maximum = maximum
        self._lock = Lock()
        self._sample = None
        self._sequence = 0
        self._error = "尚未收到有效反馈"

    def publish(self, values, timestamp_ns=None):
        values = validate_positions(values, self.count, self.minimum, self.maximum)
        if timestamp_ns is None:
            timestamp_ns = monotonic_ns()
        with self._lock:
            self._sequence += 1
            self._sample = PositionFeedback(values, timestamp_ns, self._sequence)
            self._error = ""
            return self._sample

    def invalidate(self, error):
        with self._lock:
            self._error = str(error)

    def read(self, max_age_ns=DEFAULT_MAX_AGE_NS):
        with self._lock:
            if self._error or self._sample is None:
                raise DeviceReadError(self._error or "尚未收到有效反馈")
            sample = self._sample
        if not 0 <= monotonic_ns() - sample.timestamp_ns <= max_age_ns:
            raise DeviceReadError("设备反馈已超时")
        return sample
