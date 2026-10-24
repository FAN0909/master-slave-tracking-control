"""后台暂存连续有效帧，支持停止、保存、丢弃和异常后的离线恢复。"""

import shutil
import fcntl
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from queue import Empty
from threading import Thread
from uuid import uuid4

import numpy as np
from PySide6.QtCore import QObject, Signal

from src.recording.data_synchronizer import AlignedFrame, DataSynchronizer, SOURCE_NAMES
from src.recording.dataset_export import CAMERAS, DATASET_DIR, export_episode, write_json
from src.recording.settings import SETTINGS

FPS = SETTINGS.fps
TASK = SETTINGS.task


def _vector(values, length, name):
    result = np.asarray(values, dtype=np.float32)
    if result.shape != (length,) or not np.isfinite(result).all():
        raise ValueError(f"{name} 应为 {length} 个有限数值，实际形状为 {result.shape}")
    return result


def _write_frame(path: Path, frame: AlignedFrame):
    """写入原始 BGR 图像、实测状态、绝对目标及时间戳，完整后原子改名。"""
    source_times = np.asarray([getattr(frame, name).timestamp_ns for name in SOURCE_NAMES], dtype=np.int64)
    if np.any(source_times > frame.timestamp_ns):
        raise ValueError("采集帧包含未来样本")
    samples = {
        "tick_index": np.int64(frame.tick_index), "timestamp_ns": np.int64(frame.timestamp_ns),
        "state": np.concatenate((_vector(frame.slave.data.joints, 7, "slave.joints"),
                                 _vector(frame.hand.data.joints, 6, "hand.joints"))),
        "action": np.concatenate((_vector(frame.slave_action.data, 7, "slave_action"),
                                  _vector(frame.hand_action.data, 6, "hand_action"))),
        "master": _vector(frame.master.data.joints, 7, "master.joints"),
        "tcp": _vector(frame.slave.data.tcp, 6, "slave.tcp"),
        "source_timestamp_ns": source_times,
        "source_ages_ms": ((frame.timestamp_ns - source_times) / 1e6).astype(np.float32),
        "timestamp_sources": np.asarray([getattr(frame, name).timestamp_source for name in SOURCE_NAMES]),
    }
    for name in CAMERAS:
        image = np.asarray(getattr(frame, f"{name}_camera").data)
        if image.ndim != 3 or image.shape[2] != 3 or image.dtype != np.uint8 or min(image.shape[:2]) <= 0:
            raise ValueError(f"{name} 需要 H×W×3 的 uint8 BGR 图像")
        samples[f"image_{name}"] = image
    temporary = path.with_suffix(".part")
    try:
        with temporary.open("wb") as file:
            np.savez(file, **samples)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


class EpisodeRecorder(QObject):
    capture_finished = Signal(int, str)
    save_finished = Signal(bool, str)

    def __init__(self, synchronizer: DataSynchronizer):
        super().__init__()
        self.synchronizer = synchronizer
        self.state = "idle"
        self.output_dir = self.staging_dir = None
        self.frame_count = 0
        self.capture_error = ""
        self._worker = self._save_worker = None
        self._manifest = {}
        self._capture_lock = None

    def start(self, output_dir: Path, task: str = TASK):
        if self.state != "idle":
            raise RuntimeError("请先保存或丢弃上一条 episode")
        if not task.strip():
            raise ValueError("请填写本条 episode 的任务描述")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir
        self.staging_dir = Path(tempfile.mkdtemp(prefix=".episode_", dir=output_dir))
        self.frame_count = 0
        self.capture_error = ""
        self._manifest = {
            "version": 2, "episode_id": str(uuid4()), "fps": self.synchronizer.fps,
            "task": task.strip(), "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "recording", "frame_count": 0,
            "settings": asdict(SETTINGS),
        }
        try:
            self._capture_lock = (self.staging_dir / ".capture.lock").open("a")
            fcntl.flock(self._capture_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            write_json(self.staging_dir / "episode.json", self._manifest)
            self.state = "recording"
            if not self.synchronizer.start():
                raise RuntimeError("采集线程仍在运行或队列中有未处理数据")
            self._worker = Thread(target=self._capture_loop, name="capture-disk-writer", daemon=True)
            self._worker.start()
        except Exception:
            self.synchronizer.stop()
            self.synchronizer.wait()
            self.state = "idle"
            if self._capture_lock is not None:
                self._capture_lock.close()
            shutil.rmtree(self.staging_dir)
            self.staging_dir = None
            raise

    def _capture_loop(self):
        previous_tick = previous_time = None
        shapes = None
        try:
            while True:
                try:
                    frame = self.synchronizer.output_queue.get(timeout=0.05)
                except Empty:
                    if self.synchronizer.finished.is_set():
                        break
                    continue
                if previous_tick is not None and (frame.tick_index != previous_tick + 1
                        or frame.timestamp_ns - previous_time != self.synchronizer.period_ns):
                    raise ValueError("采集时间轴不连续，已保留此前有效帧")
                frame_shapes = tuple(getattr(frame, f"{name}_camera").data.shape for name in CAMERAS)
                if shapes is not None and shapes != frame_shapes:
                    raise ValueError("录制期间相机图像尺寸发生变化")
                _write_frame(self.staging_dir / f"frame_{self.frame_count:06d}.npz", frame)
                shapes = frame_shapes
                previous_tick, previous_time = frame.tick_index, frame.timestamp_ns
                self.frame_count += 1
        except Exception as error:
            self.capture_error = str(error)
            self.synchronizer.stop()
        finally:
            self.synchronizer.wait()
            self.capture_error = self.capture_error or self.synchronizer.error
            while True:
                try:
                    self.synchronizer.output_queue.get_nowait()
                except Empty:
                    break
            self._manifest.update(status="ready", frame_count=self.frame_count,
                                  capture_error=self.capture_error)
            try:
                write_json(self.staging_dir / "episode.json", self._manifest)
            except Exception as error:
                self.capture_error = f"{self.capture_error}；无法更新采集清单：{error}"
            self._capture_lock.close()
            self.capture_finished.emit(self.frame_count, self.capture_error)

    def stop(self):
        if self.state == "recording":
            self.state = "stopping"
            self.synchronizer.stop()

    def mark_stopped(self):
        if self.state in ("recording", "stopping"):
            self.state = "stopped"

    def save(self):
        if self.state != "stopped" or self.frame_count == 0:
            raise RuntimeError("没有可保存的有效帧")
        self.state = "saving"
        self._save_worker = Thread(target=self._save_loop, name="lerobot-export", daemon=True)
        self._save_worker.start()

    def _save_loop(self):
        try:
            count = export_episode(self.staging_dir, self.output_dir)
            shutil.rmtree(self.staging_dir, ignore_errors=True)
            self.save_finished.emit(True, f"已保存 {count} 帧到 {self.output_dir / DATASET_DIR}")
        except Exception as error:
            self.save_finished.emit(False, f"保存失败：{error}；可重试，原始数据保留在 {self.staging_dir}")

    def mark_saved(self, success):
        if self.state == "saving":
            self.state = "idle" if success else "stopped"
            if success:
                self.staging_dir = None

    def discard(self):
        if self.state != "stopped":
            raise RuntimeError("请先停止录制")
        shutil.rmtree(self.staging_dir)
        self.staging_dir = None
        self.frame_count = 0
        self.capture_error = ""
        self.state = "idle"

    def wait_for_background_work(self):
        self.stop()
        if self._worker is not None and self._worker.is_alive():
            self._worker.join()
        self.synchronizer.wait()
        if self._save_worker is not None and self._save_worker.is_alive():
            self._save_worker.join()
