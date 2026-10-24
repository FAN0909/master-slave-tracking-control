"""独立线程上的固定时间轴采样；短暂调度延迟从历史缓存补取。"""

from dataclasses import dataclass
from queue import Full, Queue
from threading import Event, Thread, current_thread
from time import monotonic_ns
from typing import Mapping

from numpy import ndarray
from PySide6.QtCore import QObject, Signal

from src.shared_data.capture_ring_buffer import CaptureRingBuffer, CaptureSample
from src.shared_data.robot_share_data import HandState, MasterState, SlaveState

SOURCE_NAMES = ("master", "slave", "hand", "side_camera", "front_camera",
                "hand_camera", "slave_action", "hand_action")


@dataclass(frozen=True)
class AlignedFrame:
    tick_index: int
    timestamp_ns: int
    master: CaptureSample[MasterState]
    slave: CaptureSample[SlaveState]
    hand: CaptureSample[HandState]
    side_camera: CaptureSample[ndarray]
    front_camera: CaptureSample[ndarray]
    hand_camera: CaptureSample[ndarray]
    slave_action: CaptureSample[list[float]]
    hand_action: CaptureSample[list[int]]


class DataSynchronizer(QObject):
    """只使用目标时刻之前的样本，命令按零阶保持，禁止跳帧或无限积压。

    延迟一个采样周期查询历史，让设备线程有时间发布已采集的反馈。
    Qt 信号仅负责通知界面，实际采样不依赖 Qt 事件循环。
    """

    sig_error = Signal(str)

    def __init__(self, *, master_buffer: CaptureRingBuffer[MasterState],
                 slave_buffer: CaptureRingBuffer[SlaveState],
                 hand_buffer: CaptureRingBuffer[HandState],
                 camera_buffers: Mapping[str, CaptureRingBuffer[ndarray]],
                 slave_action_buffer: CaptureRingBuffer[list[float]],
                 hand_action_buffer: CaptureRingBuffer[list[int]],
                 fps: int = 20, max_camera_age_ns: int = 80_000_000,
                 max_robot_age_ns: int = 150_000_000,
                 max_slave_action_age_ns: int = 100_000_000,
                 alignment_delay_ns: int = 50_000_000,
                 max_catchup_ns: int = 250_000_000, queue_capacity: int = 40):
        super().__init__()
        if type(fps) is not int or not 1 <= fps <= 120:
            raise ValueError("fps must be an integer between 1 and 120")
        if type(queue_capacity) is not int or queue_capacity <= 0:
            raise ValueError("queue_capacity must be a positive integer")
        for value in (max_camera_age_ns, max_robot_age_ns, max_slave_action_age_ns,
                      alignment_delay_ns, max_catchup_ns):
            if type(value) is not int or value < 0:
                raise ValueError("time limits must be non-negative integers")
        if {"side", "front", "hand"} - camera_buffers.keys():
            raise ValueError("camera_buffers requires side, front and hand")
        self.fps = fps
        self.period_ns = 1_000_000_000 // fps
        self.alignment_delay_ns = alignment_delay_ns
        self.max_catchup_ns = max_catchup_ns
        self.sources = {
            "master": (master_buffer, max_robot_age_ns),
            "slave": (slave_buffer, max_robot_age_ns),
            "hand": (hand_buffer, max_robot_age_ns),
            **{f"{name}_camera": (camera_buffers[name], max_camera_age_ns)
               for name in ("side", "front", "hand")},
            "slave_action": (slave_action_buffer, max_slave_action_age_ns),
            "hand_action": (hand_action_buffer, None),
        }
        self.output_queue = Queue(maxsize=queue_capacity)
        self.finished = Event()
        self.finished.set()
        self._stop = Event()
        self._thread = None
        self._start_timestamp_ns = None
        self._next_tick = 0
        self.error = ""
        self.skipped_count = 0
        self.overflow_count = 0

    @property
    def is_running(self):
        return not self.finished.is_set()

    def align_at(self, timestamp_ns: int, tick_index: int) -> AlignedFrame | None:
        samples = {name: buffer.latest_before_or_at(timestamp_ns, limit)
                   for name, (buffer, limit) in self.sources.items()}
        if any(sample is None for sample in samples.values()):
            return None
        return AlignedFrame(tick_index, timestamp_ns, **samples)

    def missing_source_details(self, timestamp_ns: int) -> str:
        details = []
        for name, (buffer, limit) in self.sources.items():
            if buffer.latest_before_or_at(timestamp_ns, limit) is not None:
                continue
            sample = buffer.latest_before_or_at(timestamp_ns)
            if sample is None:
                details.append(f"{name} 无可用样本")
            else:
                age = (timestamp_ns - sample.timestamp_ns) / 1e6
                details.append(f"{name} 过期 {age:.1f} ms（上限 {limit / 1e6:.0f} ms）")
        return "；".join(details)

    def start(self) -> bool:
        if self.is_running or not self.output_queue.empty():
            return False
        self.error = ""
        self.skipped_count = self.overflow_count = 0
        self._start_timestamp_ns = monotonic_ns()
        self._next_tick = 0
        self._stop.clear()
        self.finished.clear()
        self._thread = Thread(target=self._run, name="capture-synchronizer", daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._stop.set()

    def wait(self):
        if self._thread is not None and self._thread is not current_thread():
            self._thread.join()

    def _fail(self, message):
        self.error = message
        self._stop.set()
        self.sig_error.emit(message)

    def collect_once(self, now_ns: int | None = None):
        """按顺序补齐所有已到期 tick；可单独调用以验证调度行为。"""
        if self._start_timestamp_ns is None or self._stop.is_set():
            return
        now_ns = monotonic_ns() if now_ns is None else now_ns
        target = self._start_timestamp_ns + self._next_tick * self.period_ns
        if now_ns - target - self.alignment_delay_ns > self.max_catchup_ns:
            self._fail("采集线程延迟超过历史补采窗口，已保留此前连续有效帧")
            return
        while target + self.alignment_delay_ns <= now_ns and not self._stop.is_set():
            frame = self.align_at(target, self._next_tick)
            if frame is None:
                self.skipped_count += 1
                self._fail(f"同步 tick {self._next_tick} 缺少数据：{self.missing_source_details(target)}")
                return
            try:
                self.output_queue.put_nowait(frame)
            except Full:
                self.overflow_count += 1
                self._fail("写盘跟不上采集，队列已满；已保留此前连续有效帧")
                return
            self._next_tick += 1
            target = self._start_timestamp_ns + self._next_tick * self.period_ns

    def _run(self):
        try:
            while not self._stop.is_set():
                deadline = (self._start_timestamp_ns + self._next_tick * self.period_ns
                            + self.alignment_delay_ns)
                if self._stop.wait(max(0, (deadline - monotonic_ns()) / 1e9)):
                    break
                self.collect_once()
        except Exception as error:
            self._fail(f"采集调度失败：{error}")
        finally:
            self.finished.set()
