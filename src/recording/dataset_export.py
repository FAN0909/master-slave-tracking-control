"""在隔离目录完成 LeRobot 编码，再用可恢复的提交日志追加新文件。"""

import fcntl
import json
import os
import shutil
from pathlib import Path

import numpy as np

from src.recording.data_synchronizer import SOURCE_NAMES

DATASET_DIR = "lerobot_v3"
CAMERAS = ("side", "front", "hand")
REPO_ID = "local/master-slave-tracking-control"


def write_json(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".part")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary, path)


def _features(shapes):
    joints = [f"slave_joint_{i}" for i in range(7)] + [
        f"hand_{name}" for name in ("thumb", "palm", "index", "middle", "ring", "pinky")]
    features = {
        "observation.state": {"dtype": "float32", "shape": (13,), "names": joints},
        "action": {"dtype": "float32", "shape": (13,), "names": joints},
        "observation.master_joints": {"dtype": "float32", "shape": (7,),
                                      "names": [f"master_joint_{i}" for i in range(7)]},
        "observation.slave_tcp": {"dtype": "float32", "shape": (6,),
                                  "names": ["x", "y", "z", "a", "b", "c"]},
        "observation.source_ages_ms": {"dtype": "float32", "shape": (8,),
                                       "names": list(SOURCE_NAMES)},
    }
    for name, shape in shapes.items():
        features[f"observation.images.{name}"] = {
            "dtype": "video", "shape": shape, "names": ["height", "width", "channels"]}
    return features


def _finish_commit(transaction: Path, root: Path):
    """ready 日志之后只做可重入的文件移动；进程重启后可继续提交。"""
    plan = json.loads((transaction / "commit.json").read_text())
    work = transaction / "dataset"
    root.mkdir(exist_ok=True)
    receipt = root / "meta" / "capture" / f"{plan['episode_id']}.json"
    if not receipt.exists():
        for relative in plan["files"]:
            source, target = work / relative, root / relative
            if source.exists():
                if target.exists():
                    raise RuntimeError(f"提交目标已存在，拒绝覆盖：{target}")
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(source, target)
            elif not target.is_file():
                raise RuntimeError(f"提交文件缺失：{relative}")
        if (work / "meta").exists():
            if (root / "meta").exists():
                os.replace(root / "meta", transaction / "previous_meta")
            os.replace(work / "meta", root / "meta")
        if not receipt.exists():
            raise RuntimeError("提交元数据未完成，请保留 pending 目录后重试")
    shutil.rmtree(transaction)


def _validate_schema(info, features, fps):
    if info["fps"] != fps:
        raise ValueError("数据集帧率不匹配，请选择新目录或恢复原采集帧率")
    existing_keys = set(info["features"]) - {"timestamp", "frame_index", "episode_index", "index", "task_index"}
    if existing_keys != set(features):
        raise ValueError("数据集字段不匹配，请选择新的保存目录")
    for key, feature in features.items():
        existing = info["features"][key]
        if (existing["dtype"] != feature["dtype"]
                or tuple(existing["shape"]) != tuple(feature["shape"])
                or existing.get("names") != feature.get("names")):
            raise ValueError(f"数据集字段不匹配：{key}")


def _encode(staging: Path, work: Path, root: Path, manifest: dict, files: list[Path]):
    from lerobot.configs.video import RGBEncoderConfig
    from lerobot.datasets import LeRobotDataset

    fps = manifest["fps"]
    with np.load(files[0], allow_pickle=False) as first:
        shapes = {name: tuple(first[f"image_{name}"].shape) for name in CAMERAS}
    features = _features(shapes)
    episode_index = 0
    if root.exists():
        info_path = root / "meta" / "info.json"
        if not info_path.is_file():
            raise ValueError(f"目标目录不是完整的 LeRobot 数据集：{root}")
        info = json.loads(info_path.read_text())
        _validate_schema(info, features, fps)
        episode_index = info["total_episodes"]
        # 0.6.1 resume 的首条 episode 写新 data/video/episode 文件，只需复制元数据。
        # 既有视频完全不参与写入，编码失败不会触碰正式数据集。
        shutil.copytree(root / "meta", work / "meta")
        encoder = RGBEncoderConfig.from_video_info(info["features"]["observation.images.side"].get("info"))
        dataset = LeRobotDataset.resume(repo_id=REPO_ID, root=work, video_backend="pyav",
                                        rgb_encoder=encoder,
                                        encoder_threads=2)
    else:
        dataset = LeRobotDataset.create(
            repo_id=REPO_ID, fps=fps, features=features, root=work,
            robot_type="NRC_LinkerO6", use_videos=True, video_backend="pyav",
            rgb_encoder=RGBEncoderConfig(vcodec="h264", crf=18, preset="fast"), encoder_threads=2)
    timestamps, source_times, clocks = [], [], []
    previous_tick = previous_time = None
    try:
        for index, path in enumerate(files):
            if path.name != f"frame_{index:06d}.npz":
                raise ValueError("暂存帧编号不连续，拒绝压缩时间轴")
            with np.load(path, allow_pickle=False) as frame:
                tick, timestamp = int(frame["tick_index"]), int(frame["timestamp_ns"])
                if previous_tick is not None and (tick != previous_tick + 1
                        or timestamp - previous_time != 1_000_000_000 // fps):
                    raise ValueError("暂存时间轴不连续，拒绝保存缺帧 episode")
                data = {"task": manifest["task"]}
                for key, source, length in (("observation.state", "state", 13), ("action", "action", 13),
                                            ("observation.master_joints", "master", 7),
                                            ("observation.slave_tcp", "tcp", 6),
                                            ("observation.source_ages_ms", "source_ages_ms", 8)):
                    values = frame[source].copy()
                    if values.shape != (length,) or values.dtype != np.float32 or not np.isfinite(values).all():
                        raise ValueError(f"暂存数据无效：{source}")
                    data[key] = values
                for name in CAMERAS:
                    image = frame[f"image_{name}"]
                    if image.shape != shapes[name] or image.dtype != np.uint8 or image.shape[-1] != 3:
                        raise ValueError(f"相机 {name} 的图像尺寸或类型不一致")
                    data[f"observation.images.{name}"] = image[:, :, ::-1].copy()
                times = frame["source_timestamp_ns"].copy()
                if times.shape != (8,) or np.any(times > timestamp) or np.any(times < 0):
                    raise ValueError("设备时间戳无效或取到了未来样本")
                timestamps.append(timestamp)
                source_times.append(times)
                clocks.append(frame["timestamp_sources"].copy())
                dataset.add_frame(data)
                previous_tick, previous_time = tick, timestamp
        # 顺序编码避免在已有 Qt/SDK 线程的进程中 fork；保存位于后台线程。
        dataset.save_episode(parallel_encoding=False)
    finally:
        dataset.finalize()
    capture = work / "meta" / "capture"
    capture.mkdir(exist_ok=True)
    np.savez_compressed(capture / f"{manifest['episode_id']}.npz",
                        timestamp_ns=np.asarray(timestamps, dtype=np.int64),
                        source_timestamp_ns=np.asarray(source_times, dtype=np.int64),
                        timestamp_sources=np.asarray(clocks), source_names=np.asarray(SOURCE_NAMES))
    receipt = {**manifest, "episode_index": episode_index, "frame_count": len(files),
               "arm_joint_unit": "degree", "hand_position_unit": "0..255",
               "action_semantics": "absolute joint targets successfully sent at or before sample time"}
    write_json(capture / f"{manifest['episode_id']}.json", receipt)


def export_episode(staging_dir: Path, output_dir: Path) -> int:
    """可重试、可恢复地追加一条 episode，使用 UUID 防止重复提交。"""
    staging_dir, output_dir = Path(staging_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = staging_dir / "episode.json"
    manifest = json.loads(manifest_path.read_text())
    if type(manifest["fps"]) is not int or not 1 <= manifest["fps"] <= 120 or not manifest["task"].strip():
        raise ValueError("episode 帧率或任务描述无效")
    # UUID 来自本地采集 manifest；解析后再用作路径。
    from uuid import UUID
    episode_id = str(UUID(manifest["episode_id"]))
    manifest["episode_id"] = episode_id
    root = output_dir / DATASET_DIR
    transaction = output_dir / f".{DATASET_DIR}.pending"
    with (staging_dir / ".capture.lock").open("a") as capture_lock, \
            (output_dir / f".{DATASET_DIR}.lock").open("a") as lock:
        try:
            fcntl.flock(capture_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("该 episode 仍在采集中，请先停止录制") from error
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("另一个进程正在保存该数据集") from error
        if (transaction / "commit.json").exists():
            _finish_commit(transaction, root)
        elif transaction.exists():
            shutil.rmtree(transaction)
        receipt = root / "meta" / "capture" / f"{episode_id}.json"
        if receipt.is_file():
            return json.loads(receipt.read_text())["frame_count"]
        files = sorted(staging_dir.glob("frame_*.npz"))
        if not files:
            raise ValueError("本条 episode 没有有效帧")
        transaction.mkdir()
        work = transaction / "dataset"
        try:
            _encode(staging_dir, work, root, manifest, files)
            new_files = [path.relative_to(work).as_posix() for directory in ("data", "videos")
                         for path in (work / directory).rglob("*") if path.is_file()]
            for relative in new_files:
                if (root / relative).exists():
                    raise RuntimeError(f"LeRobot 输出路径冲突，拒绝覆盖已有数据：{relative}")
            write_json(transaction / "commit.json", {"episode_id": episode_id, "files": new_files})
            _finish_commit(transaction, root)
        except Exception:
            # ready 之后保留日志，下次继续提交；此前正式数据集完全未动。
            if transaction.exists() and not (transaction / "commit.json").exists():
                shutil.rmtree(transaction)
            raise
    return len(files)
