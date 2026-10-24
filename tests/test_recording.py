"""时间对齐、后台采集和真实 LeRobot 视频导出的无硬件回归测试。"""

import json
from pathlib import Path
import tempfile
from threading import Event
from time import monotonic, monotonic_ns
import unittest
from unittest.mock import Mock, patch

import numpy as np
from PySide6.QtCore import QCoreApplication

from src.recording.data_synchronizer import AlignedFrame, CAMERAS, DataSynchronizer, FPS
from src.recording.episode_recorder import EpisodeRecorder, REPO_ID, export_episode
from src.shared_data.capture_ring_buffer import CaptureRingBuffer
from src.shared_data.device_feedback import FeedbackStatus
from src.shared_data.robot_share_data import HandState, MasterState, RobotSharedMemory, SlaveState


def frame_at(timestamp, index):
    image = np.full((32, 32, 3), [200, 40, 20], dtype=np.uint8)
    return AlignedFrame(index, timestamp, np.arange(13, dtype=np.float32),
                        np.arange(13, dtype=np.float32) + 20,
                        np.arange(7, dtype=np.float32), np.arange(6, dtype=np.float32),
                        {name: image.copy() for name in CAMERAS},
                        np.full(9, timestamp, dtype=np.int64), np.zeros(9, dtype=np.float32),
                        np.ones(3, dtype=np.int64))


class SyntheticSynchronizer:
    fps = FPS
    period_ns = 1_000_000_000 // FPS

    def __init__(self):
        self.fail_at = None
        self.image_shapes = {name: (32, 32, 3) for name in CAMERAS}

    def reset(self):
        pass

    def align_at(self, timestamp, index):
        if index == self.fail_at:
            raise RuntimeError("camera disconnected")
        return frame_at(timestamp, index)


def wait_until(predicate, timeout=4):
    deadline = monotonic() + timeout
    while not predicate():
        if monotonic() > deadline:
            raise AssertionError("background operation timed out")
        Event().wait(0.005)


class RecordingRig:
    def __init__(self, timestamp):
        self.shared = RobotSharedMemory()
        self.buffers = {name: CaptureRingBuffer(20)
                        for name in ("master", "slave", "hand", "slave_action", "hand_action")}
        self.cameras = {name: CaptureRingBuffer(5) for name in CAMERAS}
        status = FeedbackStatus(True, timestamp, 1, "")
        states = {
            "master": MasterState([1.] * 7, [], "Gello", status),
            "slave": SlaveState([2.] * 7, [3.] * 6, "NRC", status, timestamp),
            "hand": HandState([4.] * 6, "LinkerO6", status),
        }
        for name, state in states.items():
            getattr(self.shared, name).write(state)
            self.buffers[name].append(state, timestamp)
        self.buffers["slave_action"].append([5.] * 7, timestamp)
        self.buffers["hand_action"].append([6.] * 6, timestamp)
        for buffer in self.cameras.values():
            buffer.append(np.full((32, 32, 3), [10, 20, 30], dtype=np.uint8), timestamp)
        self.sync = DataSynchronizer(self.shared, self.buffers["master"], self.buffers["slave"],
                                     self.buffers["hand"], self.cameras,
                                     self.buffers["slave_action"], self.buffers["hand_action"])


class RecordingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def test_alignment_uses_measured_state_sent_actions_and_rgb(self):
        timestamp = 5_000_000_000
        rig = RecordingRig(timestamp)
        rig.buffers["hand_action"].clear()
        rig.buffers["hand_action"].append([6] * 6, 1_000_000_000)  # 目标可以持续保持。
        rig.buffers["slave_action"].append([99] * 7, timestamp + 1)  # 不可提前使用未来指令。
        with patch("src.recording.data_synchronizer.monotonic_ns", return_value=timestamp + 10):
            frame = rig.sync.align_at(timestamp, 0)
        self.assertEqual(frame.state.tolist(), [2.] * 7 + [4.] * 6)
        self.assertEqual(frame.action.tolist(), [5.] * 7 + [6.] * 6)
        self.assertEqual(frame.images["side"][0, 0].tolist(), [30, 20, 10])
        self.assertEqual(frame.source_ages_ms[-1], 4000)
        self.assertTrue(np.all(frame.source_timestamps_ns <= timestamp))

    def test_alignment_rejects_current_invalid_feedback_even_with_cached_samples(self):
        timestamp = 5_000_000_000
        rig = RecordingRig(timestamp)
        rig.shared.hand.update_partial(feedback=FeedbackStatus(error="CAN failed"))
        with patch("src.recording.data_synchronizer.monotonic_ns", return_value=timestamp):
            with self.assertRaisesRegex(RuntimeError, "CAN failed"):
                rig.sync.align_at(timestamp, 0)

    def test_alignment_rejects_old_images_and_resolution_changes(self):
        timestamp = 5_000_000_000
        rig = RecordingRig(timestamp)
        with patch("src.recording.data_synchronizer.monotonic_ns", return_value=timestamp + 110_000_000):
            with self.assertRaisesRegex(RuntimeError, "相机"):
                rig.sync.align_at(timestamp + 110_000_000, 0)
            rig.sync.align_at(timestamp, 0)
            rig.cameras["side"].append(np.zeros((64, 32, 3), np.uint8), timestamp + 1)
            with self.assertRaisesRegex(RuntimeError, "分辨率"):
                rig.sync.align_at(timestamp + 1, 1)

    def test_alignment_rejects_missing_action_and_future_tcp(self):
        timestamp = 5_000_000_000
        rig = RecordingRig(timestamp)
        rig.buffers["hand_action"].clear()
        with patch("src.recording.data_synchronizer.monotonic_ns", return_value=timestamp + 10):
            with self.assertRaisesRegex(RuntimeError, "hand_action"):
                rig.sync.align_at(timestamp, 0)
            rig.buffers["hand_action"].append([0] * 6, timestamp)
            rig.buffers["slave"].latest().data.tcp_timestamp_ns = timestamp + 1
            with self.assertRaisesRegex(RuntimeError, "TCP"):
                rig.sync.align_at(timestamp, 0)

    def test_capture_stages_continuous_ticks_and_discards(self):
        recorder = EpisodeRecorder(SyntheticSynchronizer())
        with tempfile.TemporaryDirectory() as directory:
            recorder.start(Path(directory), "place the block")
            try:
                wait_until(lambda: recorder.frame_count >= 2)
            finally:
                recorder.shutdown()
            self.assertEqual(recorder.state, "stopped")
            self.assertFalse(recorder.capture_error)
            staging = recorder.staging_dir
            manifest = json.loads((staging / "session.json").read_text())
            self.assertEqual(manifest["frame_count"], recorder.frame_count)
            for index in range(recorder.frame_count):
                with np.load(staging / f"frame_{index:06d}.npz") as frame:
                    self.assertEqual(frame["tick_index"].item(), index)
                    self.assertEqual(frame["timestamp_ns"].item(),
                                     manifest["start_timestamp_ns"] + index * 50_000_000)
            recorder.discard()
            recorder.shutdown()
            self.assertEqual(recorder.state, "idle")
            self.assertFalse(staging.exists())

    def test_capture_failure_preserves_frames_and_disables_save(self):
        sync = SyntheticSynchronizer()
        sync.fail_at = 1
        recorder = EpisodeRecorder(sync)
        with tempfile.TemporaryDirectory() as directory:
            recorder.start(directory, "place the block")
            wait_until(lambda: recorder.state == "stopped")
            recorder.shutdown()
            self.assertIn("disconnected", recorder.capture_error)
            self.assertEqual(recorder.frame_count, 1)
            self.assertTrue(recorder.staging_dir.exists())
            with self.assertRaises(RuntimeError):
                recorder.save()

    def test_queue_overflow_is_reported_instead_of_skipping_ticks(self):
        recorder = EpisodeRecorder(SyntheticSynchronizer(), queue_capacity=1)
        original = np.savez

        def slow_save(*args, **kwargs):
            Event().wait(0.2)
            original(*args, **kwargs)

        with tempfile.TemporaryDirectory() as directory, patch(
                "src.recording.episode_recorder.np.savez", side_effect=slow_save):
            recorder.start(directory, "place the block")
            wait_until(lambda: recorder.state == "stopped")
            recorder.shutdown()
            self.assertIn("队列已满", recorder.capture_error)

    def test_disk_write_failure_does_not_leave_an_active_sampler(self):
        recorder = EpisodeRecorder(SyntheticSynchronizer())
        with tempfile.TemporaryDirectory() as directory, patch(
                "src.recording.episode_recorder.np.savez", side_effect=OSError("disk full")):
            recorder.start(directory, "place the block")
            wait_until(lambda: recorder.state == "stopped")
            recorder.shutdown()
            self.assertIn("disk full", recorder.capture_error)
            self.assertTrue(all(not thread.is_alive() for thread in recorder._threads))

    def test_slow_sampling_fails_instead_of_compressing_elapsed_time(self):
        sync = SyntheticSynchronizer()
        original = sync.align_at

        def slow_sample(timestamp, index):
            if index == 1:
                Event().wait(0.08)
            return original(timestamp, index)

        sync.align_at = slow_sample
        recorder = EpisodeRecorder(sync)
        with tempfile.TemporaryDirectory() as directory:
            recorder.start(directory, "place the block")
            wait_until(lambda: recorder.state == "stopped")
            recorder.shutdown()
            self.assertIn("超时", recorder.capture_error)
            self.assertEqual(recorder.frame_count, 1)

    def test_recorder_exports_real_videos_from_background_thread(self):
        recorder = EpisodeRecorder(SyntheticSynchronizer())
        with tempfile.TemporaryDirectory() as directory:
            recorder.start(directory, "place the block", {"test_config": "preserved"})
            wait_until(lambda: recorder.frame_count >= 2)
            recorder.stop()
            wait_until(lambda: recorder.state == "stopped")
            recorder.save()
            wait_until(lambda: recorder.state in ("idle", "stopped"), timeout=20)
            recorder.shutdown()
            self.assertEqual(recorder.state, "idle")
            self.assertIsNone(recorder.staging_dir)
            session = Path(directory) / "lerobot_v3/meta/recording_sessions/episode_000000.json"
            self.assertEqual(json.loads(session.read_text())["device_config"], {"test_config": "preserved"})

    @staticmethod
    def make_staging(parent, name, task="place the block"):
        staging = parent / name
        staging.mkdir()
        start_ns = monotonic_ns()
        for index in range(2):
            np.savez(staging / f"frame_{index:06d}.npz",
                     **frame_at(start_ns + index * 50_000_000, index).arrays())
        (staging / "session.json").write_text(json.dumps({
            "fps": FPS, "task": task, "frame_count": 2, "capture_error": "",
            "start_timestamp_ns": start_ns, "image_shapes": {name: [32, 32, 3] for name in CAMERAS},
        }))
        return staging

    def test_real_lerobot_export_decodes_rgb_and_appends_after_finalize(self):
        from lerobot.datasets import LeRobotDataset
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            first = self.make_staging(parent, "first")
            self.assertEqual(export_episode(first, parent), 0)
            with self.assertRaisesRegex(RuntimeError, "已保存"):
                export_episode(first, parent)
            second = self.make_staging(parent, "second", "return the block")
            self.assertEqual(export_episode(second, parent), 1)
            dataset = LeRobotDataset(REPO_ID, root=parent / "lerobot_v3",
                                     video_backend="pyav", return_uint8=True)
            self.assertEqual(dataset.meta.total_episodes, 2)
            self.assertEqual(len(dataset), 4)
            np.testing.assert_allclose(dataset[2]["action"].numpy(), np.arange(13) + 20)
            for name in CAMERAS:
                image = dataset[0][f"observation.images.{name}"]
                self.assertEqual(tuple(image.shape), (3, 32, 32))
                self.assertGreater(float(image[0].float().mean() - image[2].float().mean()), 100)
            self.assertFalse((parent / ".lerobot_v3.saving.json").exists())
            # 追加失败保留标记，下一次保存拒绝盲目重试。
            third = self.make_staging(parent, "third")
            failed = Mock()
            failed.meta.total_episodes = 2
            failed.save_episode.side_effect = RuntimeError("encode failed")
            with patch.object(LeRobotDataset, "resume", return_value=failed):
                with self.assertRaisesRegex(RuntimeError, "encode failed"):
                    export_episode(third, parent)
            self.assertTrue((parent / ".lerobot_v3.saving.json").exists())
            with self.assertRaisesRegex(RuntimeError, "上次保存未完成"):
                export_episode(third, parent)

    def test_export_rejects_missing_frames_before_creating_dataset(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            staging = self.make_staging(parent, "staging")
            (staging / "frame_000001.npz").unlink()
            with self.assertRaisesRegex(RuntimeError, "缺少帧"):
                export_episode(staging, parent)
            self.assertFalse((parent / "lerobot_v3").exists())


if __name__ == "__main__":
    unittest.main()
