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
            with self.assertRaisesRegex(RuntimeError, r"side 相机.*110\.0 ms.*100\.0 ms"):
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

    def test_modbus_trigger_keeps_real_feedback_fresh_during_serial_writes(self):
        from types import SimpleNamespace
        from src.devices.drivers.Link_hand import LinkHand
        from src.threads.hand_thread import HandThread

        timestamp = 5_000_000_000
        rig = RecordingRig(timestamp)
        clock = [timestamp]
        next_tick = [timestamp + 50_000_000]
        errors, frames = [], []

        def advance(duration_ns):
            end = clock[0] + duration_ns
            while next_tick[0] <= end:
                clock[0] = next_tick[0]
                for name in ("master", "slave"):
                    state = getattr(rig.shared, name).read()
                    state.feedback = FeedbackStatus(True, clock[0], state.feedback.sequence + 1, "")
                    if name == "slave":
                        state.tcp_timestamp_ns = clock[0]
                    getattr(rig.shared, name).write(state)
                    rig.buffers[name].append(state, clock[0])
                rig.buffers["slave_action"].append([5.] * 7, clock[0])
                for buffer in rig.cameras.values():
                    buffer.append(buffer.latest().data, clock[0])
                try:
                    frames.append(rig.sync.align_at(clock[0], len(frames)))
                except RuntimeError as error:
                    errors.append(str(error))
                next_tick[0] += 50_000_000
            clock[0] = end

        def read_positions():
            advance(35_000_000)
            return [10.] * 6  # 实测反馈，与下发的目标故意不同。

        api = SimpleNamespace(
            get_state=Mock(side_effect=read_positions),
            set_torque=Mock(side_effect=lambda values: advance(55_000_000)),
            set_speed=Mock(side_effect=lambda values: advance(55_000_000)),
            finger_move=Mock(side_effect=lambda values: advance(55_000_000)),
        )
        hand = LinkHand("LinkerO6", modbus="/dev/fake")
        hand.is_connected, hand.hand_api = True, api
        hand._feedback.publish([4.] * 6, timestamp)
        worker = HandThread(rig.shared, rig.buffers["hand"], rig.buffers["hand_action"])
        worker.hand, worker.if_connected = hand, True
        worker._last_capture_sequence = 1
        with patch("src.recording.data_synchronizer.monotonic_ns", side_effect=lambda: clock[0]), \
                patch("src.shared_data.device_feedback.monotonic_ns", side_effect=lambda: clock[0]), \
                patch("src.threads.hand_thread.monotonic_ns", side_effect=lambda: clock[0]):
            worker._execute_action("LinkerO6", "close", [100] * 6, 255, 255, {"min": 0, "max": 255})
            worker.OnTimerTriggeredReadPos()
            worker._execute_action("LinkerO6", "open", [200] * 6, 255, 255, {"min": 0, "max": 255})
            worker.OnTimerTriggeredReadPos()
            self.assertFalse(errors, errors)
            self.assertEqual(api.set_torque.call_count, 1)
            self.assertEqual(api.set_speed.call_count, 1)
            self.assertEqual(api.finger_move.call_count, 2)
            worker._execute_action("LinkerO6", "changed", [50] * 6, 64, 128, {"min": 0, "max": 255})
            self.assertEqual(api.set_torque.call_args.args[0], [128] * 6)
            self.assertEqual(api.set_speed.call_args.args[0], [64] * 6)
            self.assertEqual(api.set_torque.call_count, 2)
            self.assertEqual(api.set_speed.call_count, 2)
            self.assertFalse(errors, errors)
            self.assertEqual(rig.shared.hand.read().joints, [10.] * 6)
            self.assertEqual(rig.buffers["hand_action"].latest().data, [50] * 6)
            self.assertTrue(frames)
            self.assertTrue(all(frame.source_ages_ms[2] <= 150 for frame in frames))

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
        for dataset_format, folder in (("v3.0", "lerobot_v3"), ("v2.1", "lerobot_v2_1")):
            with self.subTest(dataset_format=dataset_format), tempfile.TemporaryDirectory() as directory:
                recorder = EpisodeRecorder(SyntheticSynchronizer())
                recorder.start(directory, "place the block", {"test_config": "preserved"},
                               dataset_format=dataset_format)
                wait_until(lambda: recorder.frame_count >= 2)
                recorder.stop()
                wait_until(lambda: recorder.state == "stopped")
                staged_manifest = json.loads((recorder.staging_dir / "session.json").read_text())
                self.assertEqual(staged_manifest["dataset_format"], dataset_format)
                recorder.save()
                wait_until(lambda: recorder.state in ("idle", "stopped"), timeout=20)
                recorder.shutdown()
                self.assertEqual(recorder.state, "idle")
                self.assertIsNone(recorder.staging_dir)
                session = Path(directory) / folder / "meta/recording_sessions/episode_000000.json"
                manifest = json.loads(session.read_text())
                self.assertEqual(manifest["device_config"], {"test_config": "preserved"})
                self.assertEqual(manifest["dataset_format"], dataset_format)

    def test_unknown_format_is_rejected_before_capture_or_export(self):
        recorder = EpisodeRecorder(SyntheticSynchronizer())
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            with self.assertRaisesRegex(ValueError, "不支持的采集格式"):
                recorder.start(parent, "place the block", dataset_format="v1.0")
            self.assertEqual(recorder.state, "idle")
            self.assertEqual(list(parent.iterdir()), [])
            staging = self.make_staging(parent, "staging", dataset_format="v1.0")
            with self.assertRaisesRegex(ValueError, "不支持的采集格式"):
                export_episode(staging, parent)
            self.assertEqual(list(parent.iterdir()), [staging])

    @staticmethod
    def make_staging(parent, name, task="place the block", dataset_format=None):
        staging = parent / name
        staging.mkdir()
        start_ns = monotonic_ns()
        for index in range(2):
            np.savez(staging / f"frame_{index:06d}.npz",
                     **frame_at(start_ns + index * 50_000_000, index).arrays())
        manifest = {
            "fps": FPS, "task": task, "frame_count": 2, "capture_error": "",
            "start_timestamp_ns": start_ns, "image_shapes": {name: [32, 32, 3] for name in CAMERAS},
        }
        if dataset_format is not None:
            manifest["dataset_format"] = dataset_format
        (staging / "session.json").write_text(json.dumps(manifest))
        return staging

    def test_v21_export_appends_tasks_indices_stats_and_decodable_videos(self):
        import av
        import pyarrow.parquet as pq
        from lerobot.datasets import LeRobotDataset
        from lerobot.scripts.convert_dataset_v21_to_v30 import convert_dataset

        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "lerobot_v2_1"
            for index, task in enumerate(("拿起方块", "放回方块", "拿起方块")):
                staging = self.make_staging(parent, f"episode{index}", task, dataset_format="v2.1")
                self.assertEqual(export_episode(staging, parent), index)
                with self.assertRaisesRegex(RuntimeError, "已保存"):
                    export_episode(staging, parent)
                table = pq.read_table(root / f"data/chunk-000/episode_{index:06d}.parquet").to_pydict()
                self.assertEqual(table["index"], [index * 2, index * 2 + 1])
                self.assertEqual(table["episode_index"], [index, index])
                self.assertEqual(table["task_index"], [index % 2, index % 2])
                np.testing.assert_allclose(table["timestamp"], [0., 1. / FPS])
                np.testing.assert_allclose(table["action"][0], np.arange(13) + 20)
                for name in CAMERAS:
                    video = root / f"videos/chunk-000/observation.images.{name}/episode_{index:06d}.mp4"
                    with av.open(str(video)) as container:
                        images = [frame.to_ndarray(format="rgb24") for frame in container.decode(video=0)]
                    self.assertEqual(len(images), 2)
                    self.assertGreater(float(images[0][..., 0].mean() - images[0][..., 2].mean()), 100)
            info = json.loads((root / "meta/info.json").read_text())
            self.assertEqual(info["codebase_version"], "v2.1")
            self.assertEqual((info["total_episodes"], info["total_frames"], info["total_tasks"],
                              info["total_videos"], info["total_chunks"]), (3, 6, 2, 9, 1))
            self.assertEqual(info["splits"], {"train": "0:3"})
            stats = json.loads((root / "meta/stats.json").read_text())
            np.testing.assert_allclose(stats["index"]["mean"], [2.5])
            np.testing.assert_allclose(stats["index"]["std"], [np.arange(6).std()])
            np.testing.assert_allclose(stats["episode_index"]["mean"], [1.])
            np.testing.assert_allclose(stats["task_index"]["mean"], [1. / 3])
            episode_stats = [json.loads(line) for line in (root / "meta/episodes_stats.jsonl").read_text().splitlines()]
            self.assertEqual(episode_stats[2]["stats"]["episode_index"]["min"], [2])
            self.assertEqual(len((root / "meta/tasks.jsonl").read_text().splitlines()), 2)
            self.assertFalse((parent / "lerobot_v3").exists())
            self.assertFalse((parent / ".lerobot_v2_1.saving.json").exists())
            # 用官方旧格式读取/转换流程验证元数据、索引与视频定位可以被重建。
            convert_dataset(REPO_ID, root=root, push_to_hub=False)
            dataset = LeRobotDataset(REPO_ID, root=root, video_backend="pyav", return_uint8=True)
            self.assertEqual((len(dataset), dataset.meta.total_episodes), (6, 3))
            self.assertEqual([dataset[i]["task"] for i in (0, 2, 4)], ["拿起方块", "放回方块", "拿起方块"])
            self.assertEqual(tuple(dataset[4]["observation.images.side"].shape), (3, 32, 32))

    def test_v21_failed_append_preserves_marker_and_can_save_elsewhere(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            first = self.make_staging(parent, "first", dataset_format="v2.1")
            export_episode(first, parent)
            second = self.make_staging(parent, "second", dataset_format="v2.1")
            with patch("src.recording.lerobot_v21.write_episode_v21", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(OSError, "disk full"):
                    export_episode(second, parent)
            self.assertTrue((parent / ".lerobot_v2_1.saving.json").exists())
            self.assertNotIn("saved_to", json.loads((second / "session.json").read_text()))
            with self.assertRaisesRegex(RuntimeError, "上次保存未完成"):
                export_episode(second, parent)
            self.assertEqual(export_episode(second, parent / "recovery"), 0)

    def test_export_rejects_existing_dataset_version_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            first = self.make_staging(parent, "first")
            export_episode(first, parent)
            info_path = parent / "lerobot_v3/meta/info.json"
            info = json.loads(info_path.read_text())
            info["codebase_version"] = "v2.1"
            info_path.write_text(json.dumps(info))
            second = self.make_staging(parent, "second")
            with self.assertRaisesRegex(RuntimeError, "格式版本"):
                export_episode(second, parent)
            self.assertFalse((parent / ".lerobot_v3.saving.json").exists())

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
