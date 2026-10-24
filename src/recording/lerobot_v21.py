"""将官方编码器生成的单条 episode 整理为 LeRobot V2.1，可追加保存。

布局及元数据遵循 LeRobot v0.3.3；三路 MP4 直接移动，不重复编码。
https://github.com/huggingface/lerobot/tree/v0.3.3/src/lerobot/datasets
调用方负责数据集锁、保存失败标记以及新数据集的最终发布。
"""

from copy import deepcopy
import json
from pathlib import Path
import shutil

import numpy as np


DATA_PATH = "data/chunk-{episode_chunk:03d}/episode_{episode_index:06d}.parquet"
VIDEO_PATH = "videos/chunk-{episode_chunk:03d}/{video_key}/episode_{episode_index:06d}.mp4"
CHUNK_SIZE = 1000


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path, content):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _append_jsonl(path, content):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        if path.exists():
            with path.open(encoding="utf-8") as previous:
                shutil.copyfileobj(previous, stream)
        stream.write(json.dumps(content, ensure_ascii=False) + "\n")
    temporary.replace(path)


def write_episode_v21(source, root, manifest):
    """source 必须是仅含一条 episode 的 V3 数据集，root 是 V2.1 目标。"""
    import pyarrow as pa
    import pyarrow.parquet as pq
    from lerobot.datasets.compute_stats import aggregate_stats
    from lerobot.datasets.io_utils import cast_stats_to_numpy
    from lerobot.datasets.utils import serialize_dict

    source, root = Path(source), Path(root)
    source_info = _read_json(source / "meta/info.json")
    if source_info["total_episodes"] != 1 or source_info["total_frames"] != manifest["frame_count"]:
        raise RuntimeError("V2.1 导出要求完整的单条编码 episode")
    video_keys = [key for key, feature in source_info["features"].items() if feature["dtype"] == "video"]
    meta = root / "meta"
    existing = (meta / "info.json").exists()
    if existing:
        info = _read_json(meta / "info.json")
        if (info["codebase_version"] != "v2.1" or info["data_path"] != DATA_PATH
                or info["video_path"] != VIDEO_PATH or info["chunks_size"] != CHUNK_SIZE):
            raise RuntimeError("已有 V2.1 数据集的存储布局不一致")
        tasks = [json.loads(line) for line in (meta / "tasks.jsonl").read_text(encoding="utf-8").splitlines()]
        if [task["task_index"] for task in tasks] != list(range(info["total_tasks"])):
            raise RuntimeError("已有 V2.1 数据集的任务索引不连续")
    else:
        info = {
            "codebase_version": "v2.1", "robot_type": source_info["robot_type"],
            "total_episodes": 0, "total_frames": 0, "total_tasks": 0,
            "total_videos": 0, "total_chunks": 0, "chunks_size": CHUNK_SIZE,
            "fps": source_info["fps"], "splits": {}, "data_path": DATA_PATH,
            "video_path": VIDEO_PATH, "features": deepcopy(source_info["features"]),
        }
        # V2.1 的非视频字段没有独立 FPS 属性。
        for feature in info["features"].values():
            feature.pop("fps", None)
        tasks = []
    episode_index, offset = info["total_episodes"], info["total_frames"]
    task_index = next((task["task_index"] for task in tasks if task["task"] == manifest["task"]), len(tasks))
    indices = {"episode_chunk": episode_index // CHUNK_SIZE, "episode_index": episode_index}
    data_path = root / DATA_PATH.format(**indices)
    video_paths = {key: root / VIDEO_PATH.format(**indices, video_key=key) for key in video_keys}
    if any(path.exists() for path in (data_path, *video_paths.values())):
        raise RuntimeError("V2.1 目标 episode 文件已存在，拒绝覆盖")

    # 独立编码时索引均从零开始，追加时重映射全局帧、episode 和任务索引。
    data_files = list((source / "data").glob("*/*.parquet"))
    if len(data_files) != 1:
        raise RuntimeError("V2.1 导出的单条 episode 数据文件数量异常")
    table = pq.read_table(data_files[0])
    count = manifest["frame_count"]
    if table.num_rows != count:
        raise RuntimeError("V2.1 导出的数据帧数量不一致")
    for key, values in {
        "index": np.arange(offset, offset + count, dtype=np.int64),
        "episode_index": np.full(count, episode_index, dtype=np.int64),
        "task_index": np.full(count, task_index, dtype=np.int64),
    }.items():
        field = table.schema.field(key)
        table = table.set_column(table.schema.get_field_index(key), field, pa.array(values, type=field.type))

    stats = _read_json(source / "meta/stats.json")
    # 旧版统计只使用这五个字段；保持图像统计的 (C, 1, 1) 形状。
    stats = {key: {name: value for name, value in feature.items()
                   if name in ("min", "max", "mean", "std", "count")} for key, feature in stats.items()}
    for name in ("min", "max", "mean"):
        stats["index"][name] = (np.asarray(stats["index"][name]) + offset).tolist()
        stats["episode_index"][name] = [episode_index]
        stats["task_index"][name] = [task_index]
    all_stats = cast_stats_to_numpy(stats)
    if existing:
        all_stats = aggregate_stats([cast_stats_to_numpy(_read_json(meta / "stats.json")), all_stats])

    meta.mkdir(parents=True, exist_ok=True)
    data_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, data_path, compression="snappy")
    for key, destination in video_paths.items():
        video_files = list((source / "videos" / key).glob("*/*.mp4"))
        if len(video_files) != 1:
            raise RuntimeError(f"V2.1 导出的视频 {key} 文件数量异常")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(video_files[0]), str(destination))

    if task_index == len(tasks):
        _append_jsonl(meta / "tasks.jsonl", {"task_index": task_index, "task": manifest["task"]})
        info["total_tasks"] += 1
    _append_jsonl(meta / "episodes.jsonl", {"episode_index": episode_index,
                                          "tasks": [manifest["task"]], "length": count})
    _append_jsonl(meta / "episodes_stats.jsonl", {"episode_index": episode_index, "stats": stats})
    _write_json(meta / "stats.json", serialize_dict(all_stats))
    info.update(total_episodes=episode_index + 1, total_frames=offset + count,
                total_videos=(episode_index + 1) * len(video_keys), total_chunks=episode_index // CHUNK_SIZE + 1,
                splits={"train": f"0:{episode_index + 1}"})
    _write_json(meta / "info.json", info)
    return episode_index
