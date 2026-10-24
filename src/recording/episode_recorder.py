"""后台采样与暂存；保存为本地 LeRobot V3 或 V2.1 数据集。"""

import fcntl
import importlib.util
import json
from importlib.metadata import version
from pathlib import Path
from queue import Empty, Full, Queue
import shutil
import tempfile
from threading import Event, Lock, Thread
from time import monotonic_ns

import numpy as np
from PySide6.QtCore import QObject, Signal

from src.recording.data_synchronizer import CAMERAS, FPS, SOURCE_NAMES


DEFAULT_FORMAT = "v3.0"
DATASET_FORMATS = {
    "v3.0": ("LeRobot V3", "lerobot_v3"),
    "v2.1": ("LeRobot V2.1", "lerobot_v2_1"),
}
REPO_ID = "local/master_slave_tracking"
POSITION_NAMES = [f"slave_joint_{i}_deg" for i in range(7)] + [
    "hand_thumb", "hand_palm", "hand_index", "hand_middle", "hand_ring", "hand_pinky",
]
SCHEMA = {
    "version": 1, "position_names": POSITION_NAMES, "arm_unit": "degree",
    "hand_unit": "SDK position 0..255", "action": "last successfully sent absolute target at or before tick",
    "observation": "latest valid feedback at or before tick", "camera_order": list(CAMERAS),
    "source_order": list(SOURCE_NAMES),
}


def dataset_directory(dataset_format):
    if dataset_format not in DATASET_FORMATS:
        raise ValueError(f"不支持的采集格式：{dataset_format}")
    return DATASET_FORMATS[dataset_format][1]


def check_dependencies():
    if any(importlib.util.find_spec(name) is None
           for name in ("lerobot", "torch", "datasets", "pyarrow", "av")):
        raise RuntimeError("缺少 LeRobot 数据集依赖，请运行 ./setup.sh 安装 requirements.txt")
    if version("lerobot") != "0.6.1":
        raise RuntimeError("当前采集模块要求 lerobot==0.6.1，请运行 ./setup.sh")


def _write_json(path, content):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def dataset_features(shapes):
    features = {
        "observation.state": {"dtype": "float32", "shape": (13,), "names": POSITION_NAMES},
        "action": {"dtype": "float32", "shape": (13,), "names": POSITION_NAMES},
        "observation.master": {"dtype": "float32", "shape": (7,),
                               "names": [f"master_joint_{i}_deg" for i in range(7)]},
        "observation.tcp": {"dtype": "float32", "shape": (6,),
                            "names": ["x", "y", "z", "rx", "ry", "rz"]},
        "capture.tick_index": {"dtype": "int64", "shape": (1,), "names": ["tick_index"]},
        "capture.timestamp_ns": {"dtype": "int64", "shape": (1,), "names": ["monotonic_ns"]},
        "capture.source_timestamps_ns": {"dtype": "int64", "shape": (9,), "names": list(SOURCE_NAMES)},
        "capture.source_ages_ms": {"dtype": "float32", "shape": (9,), "names": list(SOURCE_NAMES)},
        "capture.feedback_sequences": {"dtype": "int64", "shape": (3,), "names": ["master", "slave", "hand"]},
    }
    for name in CAMERAS:
        features[f"observation.images.{name}"] = {
            "dtype": "video", "shape": tuple(shapes[name]), "names": ["height", "width", "channels"],
        }
    return features


def _dataset_frame(path, index, manifest):
    with np.load(path, allow_pickle=False) as data:
        if (data["tick_index"].item() != index
                or data["timestamp_ns"].item() != manifest["start_timestamp_ns"]
                + index * (1_000_000_000 // manifest["fps"])):
            raise RuntimeError(f"暂存帧 {index} 的采样时间不连续")
        return {
            "observation.state": data["state"], "action": data["action"],
            "observation.master": data["master"], "observation.tcp": data["tcp"],
            **{f"capture.{key}": data[key] for key in (
                "tick_index", "timestamp_ns", "source_timestamps_ns", "source_ages_ms", "feedback_sequences",
            )},
            **{f"observation.images.{name}": data[f"image_{name}"] for name in CAMERAS},
            "task": manifest["task"],
        }


def export_episode(staging_dir, output_parent):
    """完成一条 episode 后关闭所有写入器。已有数据集串行追加，不上传 Hub。

    新数据集先在暂存目录生成；已有数据集发生写入异常时留下保存标记，
    拒绝盲目重试，防止重复追加或继续修改未完成的元数据。
    """
    check_dependencies()
    from lerobot.configs import RGBEncoderConfig
    from lerobot.datasets import LeRobotDataset

    staging_dir, output_parent = Path(staging_dir), Path(output_parent)
    manifest = json.loads((staging_dir / "session.json").read_text(encoding="utf-8"))
    dataset_format = manifest.get("dataset_format", DEFAULT_FORMAT)
    directory = dataset_directory(dataset_format)
    if manifest.get("saved_to"):
        raise RuntimeError(f"这条 episode 已保存到 {manifest['saved_to']}")
    if manifest.get("capture_error") or not manifest.get("frame_count"):
        raise RuntimeError("采集异常或没有有效帧，不能保存为正常 episode")
    count = manifest["frame_count"]
    paths = [staging_dir / f"frame_{index:06d}.npz" for index in range(count)]
    if any(not path.is_file() for path in paths):
        raise RuntimeError("暂存 episode 缺少帧文件")
    features = dataset_features(manifest["image_shapes"])
    output_parent.mkdir(parents=True, exist_ok=True)
    root = output_parent / directory
    marker = output_parent / f".{directory}.saving.json"
    with (output_parent / f".{directory}.lock").open("a") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("另一个进程正在保存这个数据集") from error
        if marker.exists():
            raise RuntimeError(f"上次保存未完成，请先检查 {marker}；本条暂存数据已保留，可改选保存目录")
        existing = root.exists()
        if existing:
            schema_path = root / "meta" / "recording_schema.json"
            if (not schema_path.exists()
                    or json.loads(schema_path.read_text(encoding="utf-8")) != SCHEMA):
                raise RuntimeError("已有数据集与当前采集定义不一致，请选择新的保存目录")
            info = json.loads((root / "meta" / "info.json").read_text(encoding="utf-8"))
            if info.get("codebase_version") != dataset_format:
                raise RuntimeError("已有数据集的格式版本与所选格式不一致，请选择新的保存目录")
            if info["fps"] != manifest["fps"]:
                raise RuntimeError("已有数据集的 FPS 不一致")
            for name, feature in features.items():
                stored = info["features"].get(name, {})
                if any(stored.get(key) != value for key, value in feature.items() if key != "shape") \
                        or tuple(stored.get("shape", ())) != feature["shape"]:
                    raise RuntimeError(f"已有数据集字段 {name} 的定义不一致")
        export_root = root if existing else staging_dir / "export"
        if not existing and export_root.exists():
            shutil.rmtree(export_root)
        _write_json(marker, {"staging_dir": str(staging_dir.resolve()), "existing_dataset": existing})
        dataset = None
        try:
            # V2.1 复用官方流式编码器，每条 episode 独立编码后按旧版规范整理。
            encoding_root = export_root if dataset_format == "v3.0" else staging_dir / "encoding_v3"
            if dataset_format == "v2.1" and encoding_root.exists():
                shutil.rmtree(encoding_root)
            options = dict(repo_id=REPO_ID, root=encoding_root, encoder_threads=2,
                           rgb_encoder=RGBEncoderConfig(vcodec="h264", crf=20, preset="fast"),
                           video_backend="pyav", streaming_encoding=True, encoder_queue_maxsize=10)
            if existing and dataset_format == "v3.0":
                dataset = LeRobotDataset.resume(**options)
            else:
                dataset = LeRobotDataset.create(**options, fps=manifest["fps"], features=features,
                                               robot_type="nrc_linker_o6", use_videos=True)
            episode_index = dataset.meta.total_episodes
            for index, path in enumerate(paths):
                dataset.add_frame(_dataset_frame(path, index, manifest))
            dataset.save_episode()
            dataset.finalize()
            if dataset_format == "v2.1":
                from src.recording.lerobot_v21 import write_episode_v21
                episode_index = write_episode_v21(encoding_root, export_root, manifest)
                shutil.rmtree(encoding_root)
            _write_json(export_root / "meta" / "recording_schema.json", SCHEMA)
            manifest["dataset_format"] = dataset_format
            manifest["saved_to"] = str(root.resolve())
            manifest["episode_index"] = episode_index
            sessions = export_root / "meta" / "recording_sessions"
            sessions.mkdir(parents=True, exist_ok=True)
            _write_json(sessions / f"episode_{episode_index:06d}.json", manifest)
            if not existing:
                # 保存路径可在停止后更改；不同磁盘使用 shutil.move 回退。
                shutil.move(str(export_root), str(root))
            _write_json(staging_dir / "session.json", manifest)
            marker.unlink()
            return episode_index
        except Exception:
            if dataset is not None:
                try:
                    dataset.finalize()
                except Exception:
                    pass
            if not existing and not root.exists():
                marker.unlink(missing_ok=True)
            raise


class EpisodeRecorder(QObject):
    state_changed = Signal(str)
    progress = Signal(int)
    capture_finished = Signal(int, str)
    save_finished = Signal(bool, str)

    def __init__(self, synchronizer, parent=None, queue_capacity=16):
        super().__init__(parent)
        if type(queue_capacity) is not int or queue_capacity <= 0:
            raise ValueError("写盘队列容量必须为正整数")
        self.synchronizer = synchronizer
        self.queue_capacity = queue_capacity
        self._lock = Lock()
        self._state = "idle"
        self.frame_count = 0
        self.capture_error = ""
        self.staging_dir = None
        self.dataset_format = DEFAULT_FORMAT
        self._threads = []
        self._stop = Event()
        self._capture_done = Event()

    @property
    def state(self):
        with self._lock:
            return self._state

    def _set_state(self, state):
        with self._lock:
            self._state = state
        self.state_changed.emit(state)

    def _fail(self, error):
        with self._lock:
            if not self.capture_error:
                self.capture_error = str(error)
        self._stop.set()

    def start(self, output_parent, task, metadata=None, *, dataset_format=DEFAULT_FORMAT):
        if self.state != "idle":
            raise RuntimeError("请先保存或丢弃上一条 episode")
        if not task.strip():
            raise ValueError("任务描述不能为空")
        dataset_directory(dataset_format)
        check_dependencies()
        self.synchronizer.reset()
        self.synchronizer.align_at(monotonic_ns(), 0)  # 启动前检查，不进入正式 episode。
        output_parent = Path(output_parent).expanduser().resolve()
        output_parent.mkdir(parents=True, exist_ok=True)
        self.staging_dir = Path(tempfile.mkdtemp(prefix=".episode_", dir=output_parent))
        self.frame_count, self.capture_error = 0, ""
        self.dataset_format = dataset_format
        self._manifest = {"fps": self.synchronizer.fps, "task": task.strip(),
                          "dataset_format": dataset_format,
                          "frame_count": 0, "capture_error": "", "start_timestamp_ns": None,
                          "image_shapes": {}, "schema": SCHEMA, "device_config": metadata or {}}
        _write_json(self.staging_dir / "session.json", self._manifest)
        self._queue = Queue(maxsize=self.queue_capacity)
        self._stop.clear()
        self._capture_done.clear()
        self._threads = [Thread(target=self._capture_loop, name="episode-sampler"),
                         Thread(target=self._write_loop, name="episode-writer")]
        self._set_state("recording")
        for thread in self._threads:
            thread.start()

    def _capture_loop(self):
        start_ns = monotonic_ns()
        self._manifest["start_timestamp_ns"] = start_ns
        tick_index = 0
        try:
            while not self._stop.is_set():
                tick_ns = start_ns + tick_index * self.synchronizer.period_ns
                delay_s = (tick_ns - monotonic_ns()) / 1e9
                if delay_s > 0 and self._stop.wait(delay_s):
                    break
                if self._stop.is_set():
                    break
                if monotonic_ns() - tick_ns >= self.synchronizer.period_ns:
                    raise RuntimeError("采样线程超时，已缺失固定 FPS 时间点")
                frame = self.synchronizer.align_at(tick_ns, tick_index)
                if monotonic_ns() - tick_ns >= self.synchronizer.period_ns:
                    raise RuntimeError("采样线程超时，组帧耗时超过采样周期")
                try:
                    self._queue.put_nowait(frame)
                except Full as error:
                    raise RuntimeError("写盘队列已满，磁盘无法跟上采集速度") from error
                tick_index += 1
        except Exception as error:
            self._fail(error)
        finally:
            self._capture_done.set()

    def _write_loop(self):
        try:
            while not self._capture_done.is_set() or not self._queue.empty():
                try:
                    frame = self._queue.get(timeout=0.05)
                except Empty:
                    continue
                path = self.staging_dir / f"frame_{frame.tick_index:06d}.npz"
                temporary = path.with_suffix(".tmp")
                with temporary.open("wb") as stream:
                    np.savez(stream, **frame.arrays())
                temporary.replace(path)
                self.frame_count += 1
                if self.frame_count == 1 or self.frame_count % self.synchronizer.fps == 0:
                    self.progress.emit(self.frame_count)
        except Exception as error:
            self._fail(f"暂存写盘失败：{error}")
        finally:
            self._capture_done.wait()
            self._manifest.update(frame_count=self.frame_count, capture_error=self.capture_error,
                                  image_shapes=self.synchronizer.image_shapes)
            try:
                _write_json(self.staging_dir / "session.json", self._manifest)
            except Exception as error:
                self._fail(f"写入采集清单失败：{error}")
            self._set_state("stopped")
            self.capture_finished.emit(self.frame_count, self.capture_error)

    def stop(self):
        if self.state == "recording":
            self._set_state("stopping")
            self._stop.set()

    def save(self, output_parent=None):
        if self.state != "stopped" or not self.frame_count or self.capture_error:
            raise RuntimeError("请先停止一条正常且非空的 episode")
        self._set_state("saving")
        thread = Thread(target=self._save_loop,
                        args=(Path(output_parent) if output_parent else self.staging_dir.parent,),
                        name="episode-exporter")
        self._threads.append(thread)
        thread.start()

    def _save_loop(self, output_parent):
        try:
            index = export_episode(self.staging_dir, output_parent)
        except Exception as error:
            self._set_state("stopped")
            self.save_finished.emit(False, f"保存失败：{error}；暂存数据：{self.staging_dir}")
            return
        message = f"已保存 episode {index} 到 {output_parent / dataset_directory(self.dataset_format)}"
        try:
            shutil.rmtree(self.staging_dir)
            self.staging_dir = None
        except OSError as error:
            message += f"；暂存目录清理失败：{error}"
        self.frame_count = 0
        self._set_state("idle")
        self.save_finished.emit(True, message)

    def discard(self):
        if self.state != "stopped":
            raise RuntimeError("请先停止采集，再丢弃 episode")
        self._set_state("discarding")
        thread = Thread(target=self._discard_loop, name="episode-discarder")
        self._threads.append(thread)
        thread.start()

    def _discard_loop(self):
        try:
            shutil.rmtree(self.staging_dir)
        except OSError as error:
            self._set_state("stopped")
            self.save_finished.emit(False, f"丢弃失败：{error}")
            return
        self.staging_dir = None
        self.frame_count, self.capture_error = 0, ""
        self._set_state("idle")
        self.save_finished.emit(True, "已丢弃本条 episode")

    def shutdown(self):
        """退出前排空后台工作；没有按 Save 的 episode 保留在临时目录。"""
        self.stop()
        for thread in self._threads:
            thread.join()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="将已停止且完整的暂存 episode 保存为 LeRobot 数据集")
    parser.add_argument("staging_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="数据集的上级目录")
    arguments = parser.parse_args()
    print(f"Saved episode {export_episode(arguments.staging_dir, arguments.output)}")
