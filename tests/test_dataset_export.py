"""使用真实 LeRobot / H.264 编码器验证追加、读回和故障恢复。"""

import importlib.util
import fcntl
import json
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import numpy as np

from src.recording.dataset_export import export_episode, write_json
from src.recording.episode_recorder import _write_frame
from test_episode_recorder import make_frame


def stage(root, name='staging', count=4):
    directory = root / name
    directory.mkdir()
    write_json(directory / 'episode.json', {'version': 2, 'episode_id': str(uuid4()),
               'fps': 20, 'task': 'put the block in the box', 'frame_count': count})
    for index in range(count):
        _write_frame(directory / f'frame_{index:06d}.npz', make_frame(index, 1_000_000_000 + index * 50_000_000))
    return directory


@unittest.skipUnless(importlib.util.find_spec('lerobot'), 'requires requirements.txt dataset dependencies')
class DatasetExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cache_directory = tempfile.TemporaryDirectory(prefix='lerobot_test_cache_')
        cls.addClassCleanup(cls.cache_directory.cleanup)
        cls.cache_env = patch.dict(os.environ, {'HF_HUB_OFFLINE': '1',
                'HF_DATASETS_CACHE': cls.cache_directory.name})
        cls.cache_env.start()
        cls.addClassCleanup(cls.cache_env.stop)
        from lerobot.datasets import LeRobotDataset
        cls.dataset_type = LeRobotDataset

    def info(self, root):
        return json.loads((root / 'lerobot_v3/meta/info.json').read_text())

    def test_append_idempotency_rgb_and_original_timestamps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = stage(root)
            second = stage(root, 'second')
            with ThreadPoolExecutor(max_workers=1) as pool:
                self.assertEqual(pool.submit(export_episode, first, root).result(timeout=30), 4)
            self.assertEqual(export_episode(first, root), 4)
            self.assertEqual(self.info(root)['total_episodes'], 1)
            self.assertEqual(export_episode(second, root), 4)
            self.assertEqual(self.info(root)['total_frames'], 8)
            dataset = self.dataset_type('local/master-slave-tracking-control', root=root / 'lerobot_v3', video_backend='pyav')
            self.assertEqual(len(dataset), 8)
            self.assertEqual(dataset[7]['action'].shape, (13,))
            pixel = dataset[0]['observation.images.side'][:, 0, 0].numpy() * 255
            np.testing.assert_allclose(pixel, [200, 50, 10], atol=8)
            np.testing.assert_allclose(dataset.hf_dataset['timestamp'], [0, .05, .1, .15] * 2, atol=1e-6)
            episode_id = json.loads((first / 'episode.json').read_text())['episode_id']
            with np.load(root / f'lerobot_v3/meta/capture/{episode_id}.npz') as timing:
                self.assertEqual(timing['source_timestamp_ns'].shape, (4, 8))
                self.assertEqual(timing['timestamp_sources'][0, 0], 'device_feedback')
            self.assertFalse((root / '.lerobot_v3.pending').exists())

    def test_finalize_error_leaves_dataset_unchanged_and_retry_is_single_episode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staged = stage(root)
            original = self.dataset_type.finalize
            def fail_after_flush(dataset):
                original(dataset)
                raise OSError('simulated finalize error')
            with patch.object(self.dataset_type, 'finalize', fail_after_flush):
                with self.assertRaisesRegex(OSError, 'finalize error'):
                    export_episode(staged, root)
            self.assertFalse((root / 'lerobot_v3').exists())
            self.assertEqual(len(list(staged.glob('frame_*.npz'))), 4)
            export_episode(staged, root)
            export_episode(staged, root)
            self.assertEqual(self.info(root)['total_episodes'], 1)

    def test_interrupted_metadata_swap_recovers_without_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_episode(stage(root), root)
            staged = stage(root, 'second')
            original = os.replace
            def fail_metadata_swap(source, target):
                if Path(source) == root / '.lerobot_v3.pending/dataset/meta':
                    raise OSError('simulated interrupted metadata swap')
                return original(source, target)
            with patch('src.recording.dataset_export.os.replace', side_effect=fail_metadata_swap):
                with self.assertRaisesRegex(OSError, 'metadata swap'):
                    export_episode(staged, root)
            self.assertTrue((root / '.lerobot_v3.pending/commit.json').exists())
            self.assertEqual(export_episode(staged, root), 4)
            self.assertEqual(self.info(root)['total_episodes'], 2)
            self.assertEqual(self.info(root)['total_frames'], 8)
            dataset = self.dataset_type('local/master-slave-tracking-control', root=root / 'lerobot_v3', video_backend='pyav')
            self.assertEqual(dataset[7]['episode_index'].item(), 1)

    def test_frame_gap_is_rejected_without_changing_existing_dataset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_episode(stage(root), root)
            staged = stage(root, 'second')
            (staged / 'frame_000001.npz').unlink()
            with self.assertRaisesRegex(ValueError, '编号不连续'):
                export_episode(staged, root)
            self.assertEqual(self.info(root)['total_episodes'], 1)
            self.assertEqual(self.info(root)['total_frames'], 4)

    def test_recovery_refuses_an_episode_that_is_still_recording(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staged = stage(root)
            with (staged / '.capture.lock').open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaisesRegex(RuntimeError, '仍在采集'):
                    export_episode(staged, root)
            self.assertFalse((root / 'lerobot_v3').exists())


if __name__ == '__main__':
    unittest.main()
