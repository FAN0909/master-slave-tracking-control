"""后台暂存、连续前缀保存和退出行为，无需硬件。"""

import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QCoreApplication

from src.recording.data_synchronizer import AlignedFrame, DataSynchronizer, SOURCE_NAMES
from src.recording.episode_recorder import EpisodeRecorder, _write_frame
from src.shared_data.capture_ring_buffer import CaptureRingBuffer, CaptureSample
from src.shared_data.robot_share_data import HandState, MasterState, SlaveState


def make_frame(index=0, timestamp=1_000_000_000):
    sample = lambda data: CaptureSample(timestamp - 10_000_000, data, 'device_feedback')
    image = np.full((32, 32, 3), [10, 50, 200], dtype=np.uint8)
    return AlignedFrame(index, timestamp,
                        sample(MasterState([1.] * 7, [])), sample(SlaveState([2.] * 7, [3.] * 6)),
                        sample(HandState([4.] * 6)), sample(image), sample(image.copy()), sample(image.copy()),
                        sample([5.] * 7), sample([6] * 6))


class EpisodeRecorderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def test_stages_real_state_absolute_action_and_clock_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'frame_000000.npz'
            _write_frame(path, make_frame())
            with np.load(path) as data:
                self.assertEqual(data['state'].tolist(), [2.] * 7 + [4.] * 6)
                self.assertEqual(data['action'].tolist(), [5.] * 7 + [6.] * 6)
                self.assertEqual(data['source_timestamp_ns'].tolist(), [990_000_000] * 8)
                self.assertEqual(data['timestamp_sources'].tolist(), ['device_feedback'] * 8)
            self.assertFalse(path.with_suffix('.part').exists())

    def test_rejects_invalid_state_without_partial_frame(self):
        frame = make_frame()
        frame.slave.data.joints[0] = float('nan')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'frame_000000.npz'
            with self.assertRaises(ValueError):
                _write_frame(path, frame)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_background_stop_drains_queue_and_allows_saving_valid_prefix(self):
        buffers = {name: CaptureRingBuffer(100) for name in SOURCE_NAMES}
        frame = make_frame(timestamp=time.monotonic_ns())
        for name in SOURCE_NAMES:
            sample = getattr(frame, name)
            buffers[name].append(sample.data, sample.timestamp_ns)
        sync = DataSynchronizer(master_buffer=buffers['master'], slave_buffer=buffers['slave'],
                                hand_buffer=buffers['hand'], slave_action_buffer=buffers['slave_action'],
                                hand_action_buffer=buffers['hand_action'],
                                camera_buffers={name: buffers[f'{name}_camera'] for name in ('side','front','hand')})
        recorder = EpisodeRecorder(sync)
        with tempfile.TemporaryDirectory() as directory:
            recorder.start(Path(directory), 'put the block in the box')
            deadline = time.monotonic() + 2
            while recorder._worker.is_alive() and time.monotonic() < deadline:
                time.sleep(0.01)
            recorder.wait_for_background_work()
            recorder.mark_stopped()
            self.assertGreater(recorder.frame_count, 0)
            self.assertIn('缺少数据', recorder.capture_error)
            manifest = json.loads((recorder.staging_dir / 'episode.json').read_text())
            self.assertEqual(manifest['frame_count'], recorder.frame_count)
            self.assertEqual(manifest['task'], 'put the block in the box')
            with patch('src.recording.episode_recorder.export_episode', return_value=recorder.frame_count) as export:
                recorder.save()
                recorder.wait_for_background_work()
                export.assert_called_once()
                recorder.mark_saved(True)
            self.assertEqual(recorder.state, 'idle')

    def test_disk_error_stops_producer_without_waiting_for_gui_signal(self):
        sync = DataSynchronizer(master_buffer=CaptureRingBuffer(2), slave_buffer=CaptureRingBuffer(2),
                                hand_buffer=CaptureRingBuffer(2), slave_action_buffer=CaptureRingBuffer(2),
                                hand_action_buffer=CaptureRingBuffer(2),
                                camera_buffers={name: CaptureRingBuffer(2) for name in ('side','front','hand')})
        recorder = EpisodeRecorder(sync)
        with tempfile.TemporaryDirectory() as directory:
            # 首个 tick 使用已注入的完整帧，后续生产通过 stop 事件结束。
            with patch.object(sync, 'align_at', return_value=make_frame()), \
                    patch('src.recording.episode_recorder._write_frame', side_effect=OSError('disk full')):
                recorder.start(Path(directory))
                recorder._worker.join(timeout=2)
                self.assertFalse(recorder._worker.is_alive())
                self.assertTrue(sync.finished.is_set())
                self.assertEqual(recorder.capture_error, 'disk full')
            recorder.mark_stopped()
            recorder.discard()


if __name__ == '__main__':
    unittest.main()
