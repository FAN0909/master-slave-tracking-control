"""恢复已停止或进程中断后留下的暂存帧；保留原始暂存目录。"""

import argparse
from pathlib import Path

from src.recording.dataset_export import export_episode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("staging_dir", type=Path, help=".episode_* 目录")
    parser.add_argument("--output-dir", type=Path, help="数据集的上级目录，默认使用暂存目录的上级目录")
    args = parser.parse_args()
    staging = args.staging_dir.resolve()
    count = export_episode(staging, args.output_dir or staging.parent)
    print(f"已保存 {count} 帧；重复运行不会重复追加同一条 episode。原始暂存目录已保留。")


if __name__ == "__main__":
    main()
