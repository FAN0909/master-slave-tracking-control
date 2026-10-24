"""验证因果采样、短暂延迟补采、断流和队列背压。"""

import time
import unittest

import numpy as np
from PySide6.QtCore import QCoreApplication

from src.recording.data_synchronizer import DataSynchronizer
from src.shared_data.capture_ring_buffer import CaptureRingBuffer
from src.shared_data.robot_share_data import HandState, MasterState, SlaveState


class DataSynchronizerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        self.buffers = {name: CaptureRingBuffer(100) for name in
                        ('master', 'slave', 'hand', 'slave_action', 'hand_action')}
        self.cameras = {name: CaptureRingBuffer(30) for name in ('side', 'front', 'hand')}
        self.sync = self.make_sync()

    def make_sync(self, **kwargs):
        return DataSynchronizer(master_buffer=self.buffers['master'], slave_buffer=self.buffers['slave'],
                                hand_buffer=self.buffers['hand'], camera_buffers=self.cameras,
                                slave_action_buffer=self.buffers['slave_action'],
                                hand_action_buffer=self.buffers['hand_action'], **kwargs)

    def fill(self, timestamp):
        self.buffers['master'].append(MasterState([1.] * 7, []), timestamp)
        self.buffers['slave'].append(SlaveState([2.] * 7, [0.] * 6), timestamp)
        self.buffers['hand'].append(HandState([3.] * 6), timestamp)
        self.buffers['slave_action'].append([4.] * 7, timestamp)
        for camera in self.cameras.values():
            camera.append(np.zeros((4, 4, 3), dtype=np.uint8), timestamp)

    def prepare_manual(self, **kwargs):
        self.sync = self.make_sync(**kwargs)
        self.sync._start_timestamp_ns = 1_000_000_000
        self.buffers['hand_action'].append([5] * 6, 100)
        for timestamp in range(990_000_000, 1_200_000_001, 10_000_000):
            self.fill(timestamp)

    def tearDown(self):
        self.sync.stop()
        self.sync.wait()

    def test_only_past_samples_and_held_hand_command(self):
        self.fill(1_040_000_000)
        self.assertIsNone(self.sync.align_at(1_050_000_000, 0))
        self.buffers['hand_action'].append([5] * 6, 100)
        self.cameras['side'].append(np.ones((4, 4, 3), dtype=np.uint8), 1_060_000_000)
        frame = self.sync.align_at(1_050_000_000, 0)
        self.assertEqual(frame.side_camera.timestamp_ns, 1_040_000_000)
        self.assertEqual(frame.hand_action.timestamp_ns, 100)
        self.assertIsNone(self.sync.align_at(1_130_000_001, 1))

    def test_delayed_scheduler_reconstructs_every_tick(self):
        self.prepare_manual()
        self.sync.collect_once(1_210_000_000)
        frames = [self.sync.output_queue.get_nowait() for _ in range(4)]
        self.assertEqual([frame.tick_index for frame in frames], [0, 1, 2, 3])
        self.assertEqual([frame.timestamp_ns for frame in frames],
                         [1_000_000_000, 1_050_000_000, 1_100_000_000, 1_150_000_000])
        self.assertEqual(self.sync.skipped_count, 0)
        self.assertFalse(self.sync.error)

    def test_delay_window_waits_before_collecting(self):
        self.prepare_manual()
        self.sync.collect_once(1_049_999_999)
        self.assertTrue(self.sync.output_queue.empty())
        self.sync.collect_once(1_050_000_000)
        self.assertEqual(self.sync.output_queue.get_nowait().tick_index, 0)

    def test_missing_camera_stops_at_first_bad_tick(self):
        self.prepare_manual()
        self.cameras['side'].clear()
        self.cameras['side'].append(np.zeros((4, 4, 3), dtype=np.uint8), 990_000_000)
        self.sync.collect_once(1_200_000_000)
        self.assertEqual(self.sync.output_queue.qsize(), 2)
        self.assertIn('side_camera 过期 110.0 ms', self.sync.error)
        self.assertEqual(self.sync.skipped_count, 1)

    def test_overflow_preserves_queued_prefix(self):
        self.prepare_manual(queue_capacity=1)
        self.sync.collect_once(1_150_000_000)
        self.assertEqual(self.sync.output_queue.get_nowait().tick_index, 0)
        self.assertEqual(self.sync.overflow_count, 1)
        self.assertIn('队列已满', self.sync.error)

    def test_excessive_delay_stops_without_compressing_timeline(self):
        self.prepare_manual()
        self.sync.collect_once(1_500_000_000)
        self.assertTrue(self.sync.output_queue.empty())
        self.assertIn('补采窗口', self.sync.error)

    def test_collection_runs_without_processing_qt_events(self):
        now = time.monotonic_ns()
        self.fill(now)
        self.buffers['hand_action'].append([5] * 6, now)
        self.assertTrue(self.sync.start())
        time.sleep(0.125)  # 模拟 GUI 线程阻塞；不调用 processEvents。
        self.sync.stop()
        self.sync.wait()
        self.assertGreaterEqual(self.sync.output_queue.qsize(), 2)
        self.assertFalse(self.sync.error)


if __name__ == '__main__':
    unittest.main()
