"""将同步采集的一条 episode 暂存到磁盘，再导出为 LeRobot v3 数据集。"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from queue import Empty
from threading import Event, Thread

import numpy as np
from PySide6.QtCore import QObject, Signal

from src.recording.data_synchronizer import AlignedFrame, DataSynchronizer


FPS = 20
TASK = "Teleoperated manipulation"
DATASET_DIR = "lerobot_v3"
CAMERAS = ("side", "front", "hand")


def _vector(values, length: int, name: str) -> np.ndarray:
    """将关节等数值转换为定长 float32 向量，并拒绝缺失或非有限值。"""
    result = np.asarray(values, dtype=np.float32)
    if result.shape != (length,) or not np.isfinite(result).all():
        raise ValueError(f"{name} 应为 {length} 个有限数值，实际形状为 {result.shape}")
    return result


def _image(sample, name: str) -> np.ndarray:
    """检查相机样本是否为三通道 uint8 BGR 图像。"""
    image = np.asarray(sample.data)
    if image.ndim != 3 or image.shape[2] != 3 or image.dtype != np.uint8:
        raise ValueError(f"{name} 需要 H×W×3 的 uint8 BGR 图像")
    return image


def _write_frame(path: Path, frame: AlignedFrame) -> None:
    """把一条对齐样本及各设备时间戳原子地写成临时 NPZ 帧。"""
    state = np.concatenate((
        _vector(frame.slave.data.joints, 7, "slave.joints"),
        _vector(frame.hand.data.joints, 6, "hand.joints"),
    ))
    action = np.concatenate((
        _vector(frame.slave_action.data, 7, "slave_action"),
        _vector(frame.hand_action.data, 6, "hand_action"),
    ))
    samples = {
        "tick_index": np.int64(frame.tick_index),
        "timestamp_ns": np.int64(frame.timestamp_ns),
        "state": state,
        "action": action,
        "master": _vector(frame.master.data.joints, 7, "master.joints"),
        "tcp": _vector(frame.slave.data.tcp, 6, "slave.tcp"),
    }
    for name in CAMERAS:
        sample = getattr(frame, f"{name}_camera")
        samples[f"image_{name}"] = _image(sample, name)
        samples[f"{name}_timestamp_ns"] = np.int64(sample.timestamp_ns)
    for name in ("master", "slave", "hand", "slave_action", "hand_action"):
        samples[f"{name}_timestamp_ns"] = np.int64(getattr(frame, name).timestamp_ns)
    samples["source_ages_ms"] = np.asarray([
        (frame.timestamp_ns - getattr(frame, name).timestamp_ns) / 1_000_000
        for name in ("master", "slave", "hand", "side_camera", "front_camera",
                     "hand_camera", "slave_action", "hand_action")
    ], dtype=np.float32)
    temporary = path.with_suffix(".part")
    try:
        with temporary.open("wb") as file:
            np.savez(file, **samples)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _features(image_shape: tuple[int, int, int]) -> dict:
    """根据图像尺寸定义 LeRobot 的状态、动作、时间差和视频字段。"""
    height, width, channels = image_shape
    features = {
        "observation.state": {
            "dtype": "float32", "shape": (13,),
            "names": [f"slave_joint_{i}" for i in range(7)]
                     + [f"hand_{name}" for name in ("thumb", "palm", "index", "middle", "ring", "pinky")],
        },
        "action": {
            "dtype": "float32", "shape": (13,),
            "names": [f"slave_joint_{i}" for i in range(7)]
                     + [f"hand_{name}" for name in ("thumb", "palm", "index", "middle", "ring", "pinky")],
        },
        "observation.master_joints": {
            "dtype": "float32", "shape": (7,),
            "names": [f"master_joint_{i}" for i in range(7)],
        },
        "observation.slave_tcp": {
            "dtype": "float32", "shape": (6,),
            "names": ["x", "y", "z", "a", "b", "c"],
        },
        "observation.source_ages_ms": {
            "dtype": "float32", "shape": (8,),
            "names": ["master", "slave", "hand", "side_camera", "front_camera",
                      "hand_camera", "slave_action", "hand_action"],
        },
    }
    for name in CAMERAS:
        features[f"observation.images.{name}"] = {
            "dtype": "video", "shape": (height, width, channels),
            "names": ["height", "width", "channels"],
        }
    return features


def export_episode(staging_dir: Path, output_dir: Path) -> int:
    """把暂存帧追加到本地 LeRobot v3 数据集，并返回写入帧数。"""
    try:
        from lerobot.datasets import LeRobotDataset
    except ImportError as error:
        raise RuntimeError("未安装 lerobot；请在 .venv 中安装 requirements.txt") from error

    files = sorted(staging_dir.glob("frame_*.npz"))
    if not files:
        raise ValueError("本条 episode 没有有效帧")
    with np.load(files[0]) as first:
        shape = tuple(first["image_side"].shape)
    features = _features(shape)
    dataset_root = output_dir / DATASET_DIR
    repo_id = "local/master-slave-tracking-control"
    if dataset_root.exists():
        if not (dataset_root / "meta" / "info.json").is_file():
            raise ValueError(f"保存目录已存在但不是 LeRobot 数据集：{dataset_root}")
        dataset = LeRobotDataset.resume(repo_id=repo_id, root=dataset_root)
        for key, feature in features.items():
            existing = dataset.meta.features.get(key)
            if existing is None or tuple(existing["shape"]) != tuple(feature["shape"]):
                raise ValueError(f"现有数据集的字段 {key} 与本条 episode 不匹配")
        if dataset.meta.fps != FPS:
            raise ValueError("现有数据集帧率与当前采集帧率不匹配")
    else:
        dataset = LeRobotDataset.create(
            repo_id=repo_id, fps=FPS, features=features,
            root=dataset_root, robot_type="NRC_LinkerO6", use_videos=True,
        )
    try:
        for path in files:
            with np.load(path) as frame:
                data = {
                    "task": TASK,
                    "observation.state": frame["state"].copy(),
                    "action": frame["action"].copy(),
                    "observation.master_joints": frame["master"].copy(),
                    "observation.slave_tcp": frame["tcp"].copy(),
                    "observation.source_ages_ms": frame["source_ages_ms"].copy(),
                }
                for name in CAMERAS:
                    # RealSense returns BGR; LeRobot videos expect RGB.
                    data[f"observation.images.{name}"] = frame[f"image_{name}"][:, :, ::-1].copy()
                dataset.add_frame(data)
        dataset.save_episode()
    finally:
        dataset.finalize()
    return len(files)


class EpisodeRecorder(QObject):
    """协调 20 FPS 数据对齐、后台暂存和 episode 导出。"""

    capture_finished = Signal(int, str)
    save_finished = Signal(bool, str)

    def __init__(self, synchronizer: DataSynchronizer):
        """保存对齐器引用，并初始化录制状态、线程和完成信号。"""
        super().__init__()
        self.synchronizer = synchronizer
        self.synchronizer.sig_error.connect(self._on_sync_error)
        self.state = "idle"
        self.output_dir: Path | None = None
        self.staging_dir: Path | None = None
        self.frame_count = 0
        self.capture_error = ""
        self._stop_event = Event()
        self._worker: Thread | None = None
        self._save_worker: Thread | None = None

    def start(self, output_dir: Path) -> None:
        """创建本条 episode 的暂存目录，启动写盘线程和对齐器。"""
        if self.state != "idle":
            raise RuntimeError("请先保存或丢弃上一条 episode")
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir
        self.staging_dir = Path(tempfile.mkdtemp(prefix=".episode_", dir=output_dir))
        self.frame_count = 0
        self.capture_error = ""
        self._stop_event.clear()
        self._worker = Thread(target=self._capture_loop, daemon=True)
        self._worker.start()
        if not self.synchronizer.start():
            self._stop_event.set()
            self._worker.join()
            shutil.rmtree(self.staging_dir)
            self.staging_dir = None
            raise RuntimeError("对齐器未能启动")
        self.state = "recording"

    def _capture_loop(self) -> None:
        """持续取出对齐帧写盘；出现缺帧或写盘错误时停止并报告。"""
        previous_tick = None
        while not self._stop_event.is_set() or not self.synchronizer.output_queue.empty():
            try:
                frame = self.synchronizer.output_queue.get(timeout=0.1)
            except Empty:
                continue
            try:
                if previous_tick is not None and frame.tick_index != previous_tick + 1:
                    raise ValueError("录制中出现缺帧，不能作为固定帧率 episode 保存")
                _write_frame(self.staging_dir / f"frame_{self.frame_count:06d}.npz", frame)
                previous_tick = frame.tick_index
                self.frame_count += 1
            except Exception as error:
                self.capture_error = str(error)
                self._stop_event.set()
                self.synchronizer.sig_error.emit(self.capture_error)
                break
        if self.capture_error:
            while True:
                try:
                    self.synchronizer.output_queue.get_nowait()
                except Empty:
                    break

    def _on_sync_error(self, message: str) -> None:
        """收到对齐器错误后记录原因，并结束当前采集。"""
        if self.state == "recording":
            self.capture_error = message
            self.stop()

    def stop(self) -> None:
        """停止生成新帧，并等待暂存线程处理完队列中的帧。"""
        if self.state != "recording":
            return
        self.state = "stopping"
        self.synchronizer.stop()
        self._stop_event.set()
        Thread(target=self._wait_for_capture, daemon=True).start()

    def _wait_for_capture(self) -> None:
        """在后台等待写盘线程结束，再发出采集完成信号。"""
        self._worker.join()
        self.capture_finished.emit(self.frame_count, self.capture_error)

    def mark_stopped(self) -> None:
        """在界面收到采集完成信号后，把状态切换为待保存。"""
        if self.state == "stopping":
            self.state = "stopped"

    def save(self) -> None:
        """检查本条 episode 是否完整，然后启动后台导出线程。"""
        if self.state != "stopped" or self.frame_count == 0 or self.capture_error:
            raise RuntimeError("没有可保存的完整 episode")
        self.state = "saving"
        self._save_worker = Thread(target=self._save_loop, daemon=True)
        self._save_worker.start()

    def _save_loop(self) -> None:
        """执行 LeRobot 写入；成功后清理暂存文件，失败时保留它们。"""
        try:
            count = export_episode(self.staging_dir, self.output_dir)
            shutil.rmtree(self.staging_dir, ignore_errors=True)
            self.save_finished.emit(True, f"已保存 {count} 帧到 {self.output_dir / DATASET_DIR}")
        except Exception as error:
            self.save_finished.emit(False, f"保存失败：{error}；临时采集数据保留在 {self.staging_dir}")

    def mark_saved(self, success: bool) -> None:
        """根据后台导出结果更新状态，失败时允许再次保存或丢弃。"""
        if self.state == "saving":
            if success:
                self.staging_dir = None
                self.state = "idle"
            else:
                self.state = "stopped"

    def discard(self) -> None:
        """删除已停止但尚未保存的 episode 暂存目录。"""
        if self.state != "stopped":
            raise RuntimeError("请先停止录制")
        if self.staging_dir is not None:
            shutil.rmtree(self.staging_dir)
        self.staging_dir = None
        self.frame_count = 0
        self.capture_error = ""
        self.state = "idle"

    def wait_for_background_work(self) -> None:
        """退出程序前等待后台线程；未保存的暂存数据留在磁盘。"""
        if self.state == "recording":
            self.synchronizer.stop()
            self._stop_event.set()
        if self._worker is not None and self._worker.is_alive():
            self._worker.join()
        if self._save_worker is not None and self._save_worker.is_alive():
            self._save_worker.join()
