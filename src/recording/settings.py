"""采集参数；时间窗口以毫秒配置，启动程序时读取。"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecordingSettings:
    fps: int = 20
    task: str = "Teleoperated manipulation"
    alignment_delay_ms: int = 50
    max_camera_age_ms: int = 80
    max_robot_age_ms: int = 150
    max_slave_action_age_ms: int = 100
    max_catchup_ms: int = 250
    queue_capacity: int = 40

    def __post_init__(self):
        for key in ("fps", "alignment_delay_ms", "max_camera_age_ms", "max_robot_age_ms",
                    "max_slave_action_age_ms", "max_catchup_ms", "queue_capacity"):
            value = getattr(self, key)
            if type(value) is not int or value <= 0:
                raise ValueError(f"recording.{key} 必须是正整数")
        if self.fps > 120 or not isinstance(self.task, str) or not self.task.strip():
            raise ValueError("采集帧率应为 1～120，任务描述不能为空")

    @classmethod
    def load(cls):
        path = Path(__file__).resolve().parents[2] / "config" / "recording.json"
        return cls(**json.loads(path.read_text(encoding="utf-8")))


SETTINGS = RecordingSettings.load()
