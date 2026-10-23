"""无需连接硬件的采集时间对齐测试。"""

import unittest
from unittest.mock import patch

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
        self.master = CaptureRingBuffer(5)
        self.slave = CaptureRingBuffer(5)
        self.hand = CaptureRingBuffer(5)
        self.cameras = {name: CaptureRingBuffer(5) for name in ("side", "front", "hand")}
        self.slave_action = CaptureRingBuffer(5)
        self.hand_action = CaptureRingBuffer(5)
        self.synchronizer = DataSynchronizer(
            master_buffer=self.master,
            slave_buffer=self.slave,
            hand_buffer=self.hand,
            camera_buffers=self.cameras,
            slave_action_buffer=self.slave_action,
            hand_action_buffer=self.hand_action,
            queue_capacity=1,
        )

    def tearDown(self):
        self.synchronizer.stop()

    def fill_streams(self, timestamp_ns):
        self.master.append(MasterState([1.0], []), timestamp_ns)
        self.slave.append(SlaveState([2.0], []), timestamp_ns)
        self.hand.append(HandState([3.0]), timestamp_ns)
        for camera in self.cameras.values():
            camera.append(np.zeros((2, 2, 3), dtype=np.uint8), timestamp_ns)
        self.slave_action.append([4.0], timestamp_ns)

    def test_uses_only_past_samples_and_holds_hand_action(self):
        self.fill_streams(1_040_000_000)
        self.assertIsNone(self.synchronizer.align_at(1_050_000_000, 1))
        self.hand_action.append([5], 1_000_000_000)
        self.cameras["side"].append(np.ones((2, 2, 3), dtype=np.uint8), 1_060_000_000)

        frame = self.synchronizer.align_at(1_050_000_000, 1)
        self.assertEqual(frame.side_camera.timestamp_ns, 1_040_000_000)
        self.assertEqual(frame.hand_action.timestamp_ns, 1_000_000_000)
        self.assertEqual(frame.hand_action.data, [5])
        self.assertEqual(frame.slave_action.data, [4.0])
        self.assertIsNone(self.synchronizer.align_at(1_150_000_001, 3))

    def test_queue_full_stops_capture_instead_of_dropping_data(self):
        self.fill_streams(1_040_000_000)
        self.hand_action.append([5], 1_000_000_000)
        errors = []
        self.synchronizer.sig_error.connect(errors.append)
        with patch("src.recording.data_synchronizer.monotonic_ns", side_effect=[
            1_000_000_000, 1_050_000_000, 1_100_000_000,
        ]):
            self.assertTrue(self.synchronizer.start())
            self.synchronizer.collect_once()
            self.synchronizer.collect_once()

        self.assertFalse(self.synchronizer.timer.isActive())
        self.assertEqual(self.synchronizer.output_queue.qsize(), 1)
        self.assertEqual(self.synchronizer.output_queue.get_nowait().tick_index, 1)
        self.assertEqual(self.synchronizer.overflow_count, 1)
        self.assertEqual(len(errors), 1)

    def test_missing_camera_reports_its_age_and_stops(self):
        self.fill_streams(1_040_000_000)
        self.hand_action.append([5], 1_000_000_000)
        errors = []
        self.synchronizer.sig_error.connect(errors.append)
        with patch("src.recording.data_synchronizer.monotonic_ns", side_effect=[
            1_000_000_000, 1_050_000_000, 1_100_000_000, 1_150_000_000,
        ]):
            self.assertTrue(self.synchronizer.start())
            self.synchronizer.collect_once()
            self.synchronizer.output_queue.get_nowait()
            self.cameras["front"].append(np.zeros((2, 2, 3), dtype=np.uint8), 1_140_000_000)
            self.master.append(MasterState([1.0], []), 1_140_000_000)
            self.slave.append(SlaveState([2.0], []), 1_140_000_000)
            self.hand.append(HandState([3.0]), 1_140_000_000)
            self.cameras["hand"].append(np.zeros((2, 2, 3), dtype=np.uint8), 1_140_000_000)
            self.slave_action.append([4.0], 1_140_000_000)
            self.synchronizer.collect_once()
            self.synchronizer.output_queue.get_nowait()
            self.synchronizer.collect_once()

        self.assertFalse(self.synchronizer.timer.isActive())
        self.assertEqual(self.synchronizer.skipped_count, 1)
        self.assertEqual(self.synchronizer.output_queue.qsize(), 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("side_camera 过期 110.0 ms（上限 100 ms）", errors[0])

    def test_late_timer_reports_skipped_tick_and_stops(self):
        self.fill_streams(1_040_000_000)
        self.hand_action.append([5], 1_000_000_000)
        errors = []
        self.synchronizer.sig_error.connect(errors.append)
        with patch("src.recording.data_synchronizer.monotonic_ns", side_effect=[
            1_000_000_000, 1_050_000_000, 1_150_000_000,
        ]):
            self.assertTrue(self.synchronizer.start())
            self.synchronizer.collect_once()
            self.synchronizer.collect_once()

        self.assertFalse(self.synchronizer.timer.isActive())
        self.assertEqual(self.synchronizer.skipped_count, 1)
        self.assertEqual(self.synchronizer.output_queue.qsize(), 1)
        self.assertEqual(errors, ["同步定时器延迟，跳过 1 帧（当前 tick 3）"])


if __name__ == "__main__":
    unittest.main()
