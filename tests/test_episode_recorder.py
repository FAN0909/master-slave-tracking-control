"""Exercise staging and LeRobot export without robot hardware or video codecs."""

import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QCoreApplication

from src.recording.data_synchronizer import AlignedFrame, DataSynchronizer
from src.recording.episode_recorder import EpisodeRecorder, _write_frame, export_episode
from src.shared_data.capture_ring_buffer import CaptureRingBuffer, CaptureSample
from src.shared_data.robot_share_data import HandState, MasterState, SlaveState


class EpisodeRecorderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def test_stages_measured_state_action_and_original_timestamps(self):
        sample = lambda data, timestamp: CaptureSample(timestamp, data)
        image = np.array([[[1, 2, 3]]], dtype=np.uint8)
        frame = AlignedFrame(
            tick_index=3, timestamp_ns=150,
            master=sample(MasterState([1.0] * 7, [0.0] * 6), 110),
            slave=sample(SlaveState([2.0] * 7, [4.0] * 6), 120),
            hand=sample(HandState([3.0] * 6), 130),
            side_camera=sample(image, 111),
            front_camera=sample(image, 112),
            hand_camera=sample(image, 113),
            slave_action=sample([5.0] * 7, 125),
            hand_action=sample([6] * 6, 100),
        )
        with tempfile.TemporaryDirectory() as directory:
            staged = Path(directory) / "frame_000000.npz"
            _write_frame(staged, frame)
            with np.load(staged) as data:
                self.assertEqual(data["state"].tolist(), [2.0] * 7 + [3.0] * 6)
                self.assertEqual(data["action"].tolist(), [5.0] * 7 + [6.0] * 6)
                self.assertEqual(int(data["hand_action_timestamp_ns"]), 100)
                self.assertEqual(int(data["front_timestamp_ns"]), 112)
                self.assertEqual(data["source_ages_ms"].shape, (8,))

    def test_export_writes_rgb_and_finalizes(self):
        class FakeDataset:
            def __init__(self, features):
                self.meta = types.SimpleNamespace(features=features, fps=20)
                self.frames = []
                self.saved = False
                self.finalized = False

            def add_frame(self, frame):
                self.frames.append(frame)

            def save_episode(self):
                self.saved = True

            def finalize(self):
                self.finalized = True

        created = []

        def create(**kwargs):
            result = FakeDataset(kwargs["features"])
            created.append(result)
            return result

        fake_lerobot = types.ModuleType("lerobot")
        fake_datasets = types.ModuleType("lerobot.datasets")
        fake_datasets.LeRobotDataset = types.SimpleNamespace(create=create)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staging = root / "staging"
            staging.mkdir()
            np.savez(
                staging / "frame_000000.npz",
                state=np.arange(13, dtype=np.float32),
                action=np.arange(13, dtype=np.float32),
                master=np.arange(7, dtype=np.float32),
                tcp=np.arange(6, dtype=np.float32),
                source_ages_ms=np.zeros(8, dtype=np.float32),
                image_side=np.array([[[1, 2, 3]]], dtype=np.uint8),
                image_front=np.array([[[1, 2, 3]]], dtype=np.uint8),
                image_hand=np.array([[[1, 2, 3]]], dtype=np.uint8),
            )
            with patch.dict(sys.modules, {"lerobot": fake_lerobot, "lerobot.datasets": fake_datasets}):
                self.assertEqual(export_episode(staging, root), 1)
        self.assertTrue(created[0].saved)
        self.assertTrue(created[0].finalized)
        self.assertEqual(created[0].frames[0]["observation.images.side"].tolist(), [[[3, 2, 1]]])
        self.assertEqual(created[0].frames[0]["observation.state"].shape, (13,))

    def test_start_stop_and_discard_remove_staged_episode(self):
        buffers = {name: CaptureRingBuffer(5) for name in ("master", "slave", "hand", "slave_action", "hand_action")}
        cameras = {name: CaptureRingBuffer(5) for name in ("side", "front", "hand")}
        timestamp = 1_040_000_000
        buffers["master"].append(MasterState([1.0] * 7, [0.0] * 6), timestamp)
        buffers["slave"].append(SlaveState([2.0] * 7, [0.0] * 6), timestamp)
        buffers["hand"].append(HandState([3.0] * 6), timestamp)
        buffers["slave_action"].append([4.0] * 7, timestamp)
        buffers["hand_action"].append([5] * 6, timestamp)
        for camera in cameras.values():
            camera.append(np.zeros((16, 16, 3), dtype=np.uint8), timestamp)
        synchronizer = DataSynchronizer(
            master_buffer=buffers["master"], slave_buffer=buffers["slave"],
            hand_buffer=buffers["hand"], camera_buffers=cameras,
            slave_action_buffer=buffers["slave_action"],
            hand_action_buffer=buffers["hand_action"],
        )
        recorder = EpisodeRecorder(synchronizer)
        with tempfile.TemporaryDirectory() as directory:
            with patch("src.recording.data_synchronizer.monotonic_ns", side_effect=[1_000_000_000, 1_050_000_000]):
                recorder.start(Path(directory))
                synchronizer.collect_once()
            recorder.stop()
            recorder.wait_for_background_work()
            recorder.mark_stopped()
            self.assertEqual(recorder.frame_count, 1)
            self.assertEqual(len(list(recorder.staging_dir.glob("frame_*.npz"))), 1)
            recorder.discard()
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
