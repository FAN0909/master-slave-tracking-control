import json
import math
from pathlib import Path

from PySide6.QtCore import QIODevice, QSaveFile, QSignalBlocker, Qt
from PySide6.QtWidgets import QAbstractItemView, QDialog, QHeaderView, QInputDialog, QMessageBox, QTableWidgetItem

from src.ui.log_stream import Logger
from src.ui.settings_window import Ui_SettingsDialog
from src.shared_data.robot_share_data import RobotSharedMemory


class SettingsDialog(QDialog):
    CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "slave_arm.json"
    HAND_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "hand_control.json"

    def __init__(self, shared_data: RobotSharedMemory, parent=None):
        super().__init__(parent)
        self.shared_data = shared_data
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.slave_params = None
        self._displayed_hand_model = None
        self._loaded_action_names = ()
        self._default_hand_position = 0
        self._saved_table_snapshot = ()

        self.init_ui()

    def init_ui(self):
        self.ui.pushButton_save_slave_param.clicked.connect(self.save_slave_param)
        self.ui.pushButton_save_hand_actions.clicked.connect(self.save_hand_actions)
        self.ui.pushButton_add_hand_actions.clicked.connect(self.add_hand_action)
        self.ui.pushButton_delete_hand_actions.clicked.connect(self.delete_hand_actions)
        table = self.ui.tableWidget_hand_actions
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().hide()
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.itemSelectionChanged.connect(self.update_delete_hand_action_button)
        self.ui.comboBox_hand_model_settings.currentTextChanged.connect(self.on_hand_model_changed)
        self.refresh_hand_actions()

    def update_delete_hand_action_button(self):
        table = self.ui.tableWidget_hand_actions
        self.ui.pushButton_delete_hand_actions.setEnabled(
            self._displayed_hand_model is not None and bool(table.selectionModel().selectedRows())
        )

    def _read_hand_config(self):
        with self.HAND_CONFIG_PATH.open(encoding="utf-8") as file:
            config = json.load(file)
        if not isinstance(config, dict):
            raise ValueError("灵巧手配置必须是对象")
        return config

    def _table_snapshot(self):
        table = self.ui.tableWidget_hand_actions
        return tuple(
            tuple(table.item(row, column).text() if table.item(row, column) else ""
                  for column in range(table.columnCount()))
            for row in range(table.rowCount())
        )

    def _confirm_pending_hand_changes(self):
        if self._displayed_hand_model is None or self._table_snapshot() == self._saved_table_snapshot:
            return True
        choice = QMessageBox.question(
            self, "未保存的动作", "当前动作有未保存的修改，是否先保存？",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if choice == QMessageBox.StandardButton.Save:
            return self.save_hand_actions()
        return choice == QMessageBox.StandardButton.Discard

    def _load_hand_actions(self, hand_model, config):
        try:
            hand_config = config[hand_model]
            joint_names = hand_config["joint_names"]
            actions = hand_config["actions"]
            if not isinstance(joint_names, list) or not all(isinstance(name, str) for name in joint_names):
                raise ValueError("joint_names 必须是关节名称数组")
            if not isinstance(actions, dict):
                raise ValueError("actions 必须是对象")
            for action_name, action in actions.items():
                if not isinstance(action, dict) or not isinstance(action.get("positions"), list):
                    raise ValueError(f"动作 {action_name} 缺少 positions 数组")
                if len(action["positions"]) != len(joint_names):
                    raise ValueError(f"动作 {action_name} 的 positions 数量与关节数量不一致")
        except (OSError, ValueError, KeyError, TypeError) as error:
            Logger.instance().error(f"读取 {hand_model} 灵巧手动作失败: {error}")
            return False

        table = self.ui.tableWidget_hand_actions
        self._displayed_hand_model = None
        table.setRowCount(0)
        table.setColumnCount(len(joint_names) + 1)
        table.setHorizontalHeaderLabels(["动作名称", *joint_names])
        table.setRowCount(len(actions))
        for row, (name, action) in enumerate(actions.items()):
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 0, name_item)
            for column, position in enumerate(action["positions"], start=1):
                table.setItem(row, column, QTableWidgetItem(str(position)))
        self._displayed_hand_model = hand_model
        self._loaded_action_names = tuple(actions)
        self._default_hand_position = hand_config.get("position_range", {}).get("min", 0)
        self._saved_table_snapshot = self._table_snapshot()
        self.ui.pushButton_save_hand_actions.setEnabled(True)
        self.ui.pushButton_add_hand_actions.setEnabled(True)
        self.update_delete_hand_action_button()
        return True

    def refresh_hand_actions(self, prefer_connected=False):
        """从配置刷新型号及动作；没有连接设备也可以查看。"""
        if not self._confirm_pending_hand_changes():
            return
        try:
            config = self._read_hand_config()
        except (OSError, ValueError, TypeError) as error:
            Logger.instance().error(f"读取灵巧手配置失败: {error}")
            return

        combo = self.ui.comboBox_hand_model_settings
        connected_model = self.shared_data.hand.read().name
        selected_model = combo.currentText()
        hand_model = (
            connected_model if prefer_connected and connected_model in config
            else selected_model if selected_model in config
            else self._displayed_hand_model if self._displayed_hand_model in config
            else next(iter(config), None)
        )
        if hand_model is not None and not self._load_hand_actions(hand_model, config):
            return
        if hand_model is None:
            self._displayed_hand_model = None
            self._loaded_action_names = ()
            self._saved_table_snapshot = ()
            table = self.ui.tableWidget_hand_actions
            table.setRowCount(0)
            table.setColumnCount(1)
            table.setHorizontalHeaderLabels(["动作名称"])
            self.ui.pushButton_save_hand_actions.setEnabled(False)
            self.ui.pushButton_add_hand_actions.setEnabled(False)
            self.ui.pushButton_delete_hand_actions.setEnabled(False)
        with QSignalBlocker(combo):
            combo.clear()
            combo.addItems(config.keys())
            if hand_model is not None:
                combo.setCurrentText(hand_model)

    def on_hand_model_changed(self, hand_model):
        if not hand_model or hand_model == self._displayed_hand_model:
            return
        previous_model = self._displayed_hand_model
        if not self._confirm_pending_hand_changes():
            with QSignalBlocker(self.ui.comboBox_hand_model_settings):
                self.ui.comboBox_hand_model_settings.setCurrentText(previous_model or "")
            return
        try:
            config = self._read_hand_config()
        except (OSError, ValueError, TypeError) as error:
            Logger.instance().error(f"读取灵巧手配置失败: {error}")
            config = {}
        if not self._load_hand_actions(hand_model, config):
            with QSignalBlocker(self.ui.comboBox_hand_model_settings):
                self.ui.comboBox_hand_model_settings.setCurrentText(previous_model or "")

    def add_hand_action(self):
        """向表格添加一个动作，等待 Save Actions 写入配置。"""
        if self._displayed_hand_model is None:
            return
        name, accepted = QInputDialog.getText(self, "添加动作", "动作名称：")
        if not accepted:
            return
        name = name.strip()
        table = self.ui.tableWidget_hand_actions
        existing_names = {table.item(row, 0).text() for row in range(table.rowCount())}
        if not name or name in existing_names:
            Logger.instance().error("动作名称不能为空或与已有动作重复")
            return

        row = table.rowCount()
        table.insertRow(row)
        name_item = QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(row, 0, name_item)
        for column in range(1, table.columnCount()):
            table.setItem(row, column, QTableWidgetItem(str(self._default_hand_position)))
        table.selectRow(row)

    def delete_hand_actions(self):
        """从表格移除选中的动作，等待 Save Actions 写入配置。"""
        if self._displayed_hand_model is None:
            return
        table = self.ui.tableWidget_hand_actions
        for row in sorted((index.row() for index in table.selectionModel().selectedRows()), reverse=True):
            table.removeRow(row)

    def save_hand_actions(self):
        """把表格中的关节位置写回当前型号的动作配置。"""
        hand_model = self._displayed_hand_model
        if hand_model is None:
            Logger.instance().error("请先选择灵巧手型号")
            return False

        table = self.ui.tableWidget_hand_actions
        try:
            with self.HAND_CONFIG_PATH.open(encoding="utf-8") as file:
                config = json.load(file)
            hand_config = config[hand_model]
            joint_names = hand_config["joint_names"]
            actions = hand_config["actions"]
            if table.columnCount() != len(joint_names) + 1 or tuple(actions) != self._loaded_action_names:
                raise ValueError("配置中的动作或关节已变化，请重新打开设置")
            if [table.horizontalHeaderItem(i + 1).text() for i in range(len(joint_names))] != joint_names:
                raise ValueError("关节名称已变化，请重新打开设置")

            updated_actions = {}
            for row in range(table.rowCount()):
                name_item = table.item(row, 0)
                action_name = name_item.text().strip() if name_item else ""
                if not action_name or action_name in updated_actions:
                    raise ValueError("动作名称不能为空或重复")
                positions = []
                for column, joint_name in enumerate(joint_names, start=1):
                    item = table.item(row, column)
                    value = item.text().strip() if item else ""
                    try:
                        positions.append(int(value))
                    except ValueError as error:
                        raise ValueError(f"动作 {action_name} 的 {joint_name} 必须是整数") from error
                action = actions.get(action_name)
                if action is None:
                    action = {
                        "description": "",
                        "speed": hand_config.get("default_speed", 255),
                        "force": hand_config.get("default_force", 255),
                    }
                updated_actions[action_name] = {**action, "positions": positions}

            hand_config["actions"] = updated_actions
            content = (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            file = QSaveFile(str(self.HAND_CONFIG_PATH))
            if not file.open(QIODevice.OpenModeFlag.WriteOnly):
                raise OSError(file.errorString())
            if file.write(content) != len(content):
                message = file.errorString()
                file.cancelWriting()
                raise OSError(message)
            if not file.commit():
                raise OSError(file.errorString())
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            Logger.instance().error(f"灵巧手动作保存失败: {error}")
            return False

        self._loaded_action_names = tuple(updated_actions)
        self._saved_table_snapshot = self._table_snapshot()
        Logger.instance().info(f"{hand_model} 灵巧手动作已保存")
        return True

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
