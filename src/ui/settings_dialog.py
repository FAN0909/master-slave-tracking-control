import json
import math
from pathlib import Path

from PySide6.QtCore import QIODevice, QSaveFile
from PySide6.QtWidgets import QDialog

from src.ui.log_stream import Logger
from src.ui.settings_window import Ui_SettingsDialog
from src.shared_data.robot_share_data import RobotSharedMemory


class SettingsDialog(QDialog):
    CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "slave_arm.json"

    def __init__(self, shared_data: RobotSharedMemory, parent=None):
        super().__init__(parent)
        self.shared_data = shared_data
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.slave_params = None

        self.init_ui()

    def init_ui(self):
        self.ui.pushButton_save_slave_param.clicked.connect(self.save_slave_param)

        #init hand actions list
        

    def save_slave_param(self):
        """读取当前从手参数并保存到配置文件。"""
        slave_name = self.shared_data.slave.read().name
        if not slave_name:
            Logger.instance().error("从手设备名称为空，请先连接从手再保存参数")
            return
        try:
            velocity = float(self.ui.lineEdit_slave_arm_vel.text().strip())
            acceleration = float(self.ui.lineEdit_slave_arm_acc.text().strip())
            jerk = float(self.ui.lineEdit_slave_arm_jerk.text().strip())
            if not all(math.isfinite(value) and value > 0 for value in (velocity, acceleration, jerk)):
                raise ValueError
        except ValueError:
            Logger.instance().error("从手速度、加速度、加加速度必须是有限的正数")
            return

        params = {
            "SERVO_J_VMAX": velocity,
            "SERVO_J_AVMAX": acceleration,
            "SERVO_J_JMAX": jerk,
        }
        try:
            with self.CONFIG_PATH.open(encoding="utf-8") as file:
                config = json.load(file)
            if slave_name not in config:
                raise ValueError(f"配置文件中没有 {slave_name} 的从手配置")
            config[slave_name].update(params)
            content = (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            file = QSaveFile(str(self.CONFIG_PATH))
            if not file.open(QIODevice.OpenModeFlag.WriteOnly):
                raise OSError(file.errorString())
            if file.write(content) != len(content):
                message = file.errorString()
                file.cancelWriting()
                raise OSError(message)
            if not file.commit():
                raise OSError(file.errorString())
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            Logger.instance().error(f"从手参数保存失败: {error}")
            return

        self.slave_params = params
        Logger.instance().info(
            f"{slave_name} 从手参数已保存：速度={velocity}，加速度={acceleration}，加加速度={jerk}"
        )
