"""按固定时间轴，从设备环形缓存组成一条同步采集样本。"""

from dataclasses import dataclass
from queue import Full, Queue
from time import monotonic_ns
from typing import Mapping

from numpy import ndarray
from PySide6.QtCore import QObject, QTimer, Qt, Signal, Slot

from src.shared_data.capture_ring_buffer import CaptureRingBuffer, CaptureSample
from src.shared_data.robot_share_data import HandState, MasterState, SlaveState


@dataclass(frozen=True)
class AlignedFrame:
    """一个目标时刻对应的原始样本，保留各设备实际采样时间戳。"""

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
    """在所属 Qt 线程内定时对齐数据，交给另一个线程从 output_queue 取走。

    设备线程继续独立写各自的环形缓存。相机、状态和 Slave action 过期时
    跳过该时刻；Hand action 仅在下发时更新，因此一直沿用最近一次命令。
    输出队列满时停止采集并发出错误，防止未写盘数据无限积压。
    """

    sig_error = Signal(str)

    def __init__(
        self,
        *,
        master_buffer: CaptureRingBuffer[MasterState],
        slave_buffer: CaptureRingBuffer[SlaveState],
        hand_buffer: CaptureRingBuffer[HandState],
        camera_buffers: Mapping[str, CaptureRingBuffer[ndarray]],
        slave_action_buffer: CaptureRingBuffer[list[float]],
        hand_action_buffer: CaptureRingBuffer[list[int]],
        fps: int = 20,
        max_camera_age_ns: int = 100_000_000,
        max_robot_age_ns: int = 200_000_000,
        max_slave_action_age_ns: int = 100_000_000,
        queue_capacity: int = 20,
    ) -> None:
        super().__init__()
        if isinstance(fps, bool) or not isinstance(fps, int) or not 1 <= fps <= 1000:
            raise ValueError("fps must be an integer between 1 and 1000")
        if isinstance(queue_capacity, bool) or not isinstance(queue_capacity, int) or queue_capacity <= 0:
            raise ValueError("queue_capacity must be a positive integer")
        for name, age in (
            ("max_camera_age_ns", max_camera_age_ns),
            ("max_robot_age_ns", max_robot_age_ns),
            ("max_slave_action_age_ns", max_slave_action_age_ns),
        ):
            if isinstance(age, bool) or not isinstance(age, int) or age < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        missing = {"side", "front", "hand"} - camera_buffers.keys()
        if missing:
            raise ValueError(f"camera_buffers missing: {', '.join(sorted(missing))}")

        self.master_buffer = master_buffer
        self.slave_buffer = slave_buffer
        self.hand_buffer = hand_buffer
        self.camera_buffers = dict(camera_buffers)
        self.slave_action_buffer = slave_action_buffer
        self.hand_action_buffer = hand_action_buffer
        self.max_camera_age_ns = max_camera_age_ns
        self.max_robot_age_ns = max_robot_age_ns
        self.max_slave_action_age_ns = max_slave_action_age_ns
        self.output_queue: Queue[AlignedFrame] = Queue(maxsize=queue_capacity)
        self.period_ns = 1_000_000_000 // fps
        self._start_timestamp_ns: int | None = None
        self._last_tick_index = 0
        self.skipped_count = 0
        self.overflow_count = 0
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.setInterval(round(1000 / fps))
        self.timer.timeout.connect(self.collect_once)

    def align_at(self, timestamp_ns: int, tick_index: int) -> AlignedFrame | None:
        """取每路在目标时刻及之前的最近样本；任一路缺失则返回 None。"""
        master = self.master_buffer.latest_before_or_at(timestamp_ns, self.max_robot_age_ns)
        slave = self.slave_buffer.latest_before_or_at(timestamp_ns, self.max_robot_age_ns)
        hand = self.hand_buffer.latest_before_or_at(timestamp_ns, self.max_robot_age_ns)
        side_camera = self.camera_buffers["side"].latest_before_or_at(timestamp_ns, self.max_camera_age_ns)
        front_camera = self.camera_buffers["front"].latest_before_or_at(timestamp_ns, self.max_camera_age_ns)
        hand_camera = self.camera_buffers["hand"].latest_before_or_at(timestamp_ns, self.max_camera_age_ns)
        slave_action = self.slave_action_buffer.latest_before_or_at(
            timestamp_ns, self.max_slave_action_age_ns
        )
        hand_action = self.hand_action_buffer.latest_before_or_at(timestamp_ns)
        if any(sample is None for sample in (
            master, slave, hand, side_camera, front_camera, hand_camera,
            slave_action, hand_action,
        )):
            return None
        return AlignedFrame(
            tick_index=tick_index,
            timestamp_ns=timestamp_ns,
            master=master,
            slave=slave,
            hand=hand,
            side_camera=side_camera,
            front_camera=front_camera,
            hand_camera=hand_camera,
            slave_action=slave_action,
            hand_action=hand_action,
        )

    @Slot()
    def start(self) -> bool:
        """从新的固定帧率时间轴开始；先清空上一段的输出队列。"""
        if self.timer.isActive():
            return False
        if not self.output_queue.empty():
            self.sig_error.emit("采集输出队列尚有未处理的数据")
            return False
        self._start_timestamp_ns = monotonic_ns()
        self._last_tick_index = 0
        self.skipped_count = 0
        self.overflow_count = 0
        self.timer.start()
        return True

    @Slot()
    def stop(self) -> None:
        """停止产生新样本；已有输出仍留在队列中供写盘线程处理。"""
        self.timer.stop()

    @Slot()
    def collect_once(self) -> None:
        """处理当前时间轴上的一个时刻；定时器延迟时跳过错过的时刻。"""
        if self._start_timestamp_ns is None or not self.timer.isActive():
            return
        tick_index = (monotonic_ns() - self._start_timestamp_ns) // self.period_ns
        if tick_index <= self._last_tick_index:
            return
        self.skipped_count += tick_index - self._last_tick_index - 1
        self._last_tick_index = tick_index
        target_timestamp_ns = self._start_timestamp_ns + tick_index * self.period_ns
        frame = self.align_at(target_timestamp_ns, tick_index)
        if frame is None:
            self.skipped_count += 1
            return
        try:
            self.output_queue.put_nowait(frame)
        except Full:
            self.overflow_count += 1
            self.stop()
            self.sig_error.emit("采集输出队列已满，采集已停止")
