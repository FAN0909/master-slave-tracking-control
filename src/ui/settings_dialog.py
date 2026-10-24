import json
import math
from pathlib import Path

from PySide6.QtCore import QIODevice, QSaveFile, QSignalBlocker, Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QDialog, QHeaderView, QInputDialog, QMessageBox, QTableWidgetItem

from src.ui.log_stream import Logger
from src.ui.settings_window import Ui_SettingsDialog
from src.shared_data.robot_share_data import RobotSharedMemory


class SettingsDialog(QDialog):
    sig_test_hand_action = Signal(str, str, list, int, int)

    CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "slave_arm.json"
    HAND_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "hand_control.json"

    def __init__(self, shared_data: RobotSharedMemory, parent=None):
        """创建界面并保存当前型号、动作列表和表格快照等编辑状态。"""
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
        self._saved_action_selection = ()

        self.init_ui()

    def init_ui(self):
        """连接动作设置按钮并初始化表格。"""
        self.ui.pushButton_save_slave_param.clicked.connect(self.save_slave_param)
        self.ui.pushButton_save_hand_actions.clicked.connect(self.save_hand_actions)
        self.ui.pushButton_add_hand_actions.clicked.connect(self.add_hand_action)
        self.ui.pushButton_delete_hand_actions.clicked.connect(self.delete_hand_actions)
        self.ui.pushButton_hand_test.clicked.connect(self.test_hand_action)
        self.ui.comboBox_hand_actions_test.currentTextChanged.connect(self.update_hand_test_button)
        table = self.ui.tableWidget_hand_actions
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().hide()
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.itemSelectionChanged.connect(self.update_delete_hand_action_button)
        self.load_slave_param()

    def _selected_slave_name(self, config):
        name = self.shared_data.slave.read().name
        if not name and self.parent() is not None:
            combo = getattr(getattr(self.parent(), "ui", None), "comboBox_robot_type", None)
            if combo is not None:
                name = combo.currentText().strip()
        if not name and len(config) == 1:
            name = next(iter(config))
        if name not in config:
            raise ValueError(f"配置文件中没有 {name or '当前从手'} 的配置")
        return name

    def load_slave_param(self):
        """Show the saved parameters and home joint angles."""
        try:
            with self.CONFIG_PATH.open(encoding="utf-8") as file:
                config = json.load(file)
            values = config[self._selected_slave_name(config)]
            for widget_name, key in (
                ("lineEdit_slave_arm_vel", "SERVO_J_VMAX"),
                ("lineEdit_slave_arm_acc", "SERVO_J_AVMAX"),
                ("lineEdit_slave_arm_jerk", "SERVO_J_JMAX"),
            ):
                getattr(self.ui, widget_name).setText(str(values[key]))
            home = values.get("HOME_JOINTS", [])
            for index in range(7):
                getattr(self.ui, f"lineEdit_slave_home_joint{index}").setText(
                    str(home[index]) if isinstance(home, list) and len(home) == 7 else ""
                )
        except (OSError, ValueError, KeyError, TypeError) as error:
            Logger.instance().error(f"读取从手设置失败: {error}")

    def update_delete_hand_action_button(self):
        """只有选中动作行且已有显示型号时才允许删除。"""
        table = self.ui.tableWidget_hand_actions
        self.ui.pushButton_delete_hand_actions.setEnabled(
            self._displayed_hand_model is not None and bool(table.selectionModel().selectedRows())
        )

    def refresh_hand_action_choices(self):
        """用当前表格的动作名称更新张开、闭合和测试选项。"""
        table = self.ui.tableWidget_hand_actions
        names = [table.item(row, 0).text() for row in range(table.rowCount())
                 if table.item(row, 0) is not None]
        for combo, default_name in (
            (self.ui.comboBox_hand_current_close, "close"),
            (self.ui.comboBox_hand_current_open, "open"),
            (self.ui.comboBox_hand_actions_test, "open"),
        ):
            selected_name = combo.currentText()
            with QSignalBlocker(combo):
                combo.clear()
                combo.addItems(names)
                if selected_name in names:
                    combo.setCurrentText(selected_name)
                elif default_name in names:
                    combo.setCurrentText(default_name)
        self.update_hand_test_button()

    def update_hand_test_button(self):
        """仅在当前型号的灵巧手已连接且选有动作时允许测试。"""
        connected_model = self.shared_data.hand.read().name
        self.ui.pushButton_hand_test.setEnabled(
            bool(connected_model)
            and connected_model == self._displayed_hand_model
            and bool(self.ui.comboBox_hand_actions_test.currentText())
            and not (self.parent() is not None and hasattr(self.parent(), "episode_recorder")
                     and self.parent().episode_recorder.state in ("recording", "stopping"))
        )

    def test_hand_action(self):
        """把表格中选中动作的当前数值交给手线程执行。"""
        hand_model = self._displayed_hand_model
        action_name = self.ui.comboBox_hand_actions_test.currentText()
        if not hand_model or hand_model != self.shared_data.hand.read().name:
            Logger.instance().error("请先连接当前型号的灵巧手")
            return
        table = self.ui.tableWidget_hand_actions
        row = next((i for i in range(table.rowCount())
                    if table.item(i, 0) and table.item(i, 0).text() == action_name), None)
        if row is None:
            Logger.instance().error("请选择有效的灵巧手动作")
            return
        try:
            values = [int(table.item(row, column).text().strip())
                      for column in range(1, table.columnCount())]
        except (AttributeError, ValueError) as error:
            Logger.instance().error(f"动作 {action_name} 含有无效的关节位置、速度或力矩: {error}")
            return
        self.sig_test_hand_action.emit(hand_model, action_name, values[:-2], values[-2], values[-1])

    def _read_hand_config(self):
        """读取灵巧手配置，并确认顶层结构可按型号查找。"""
        with self.HAND_CONFIG_PATH.open(encoding="utf-8") as file:
            config = json.load(file)
        if not isinstance(config, dict):
            raise ValueError("灵巧手配置必须是对象")
        return config

    def _table_snapshot(self):
        """记录表格全部单元格文字，用于识别尚未保存的编辑。"""
        table = self.ui.tableWidget_hand_actions
        return tuple(
            tuple(table.item(row, column).text() if table.item(row, column) else ""
                  for column in range(table.columnCount()))
            for row in range(table.rowCount())
        )

    def _action_selection(self):
        return (self.ui.comboBox_hand_current_close.currentText(),
                self.ui.comboBox_hand_current_open.currentText())

    def _confirm_pending_hand_changes(self):
        """切换或刷新前处理未保存修改；取消时保留当前表格。"""
        if (self._displayed_hand_model is None or
                (self._table_snapshot() == self._saved_table_snapshot
                 and self._action_selection() == self._saved_action_selection)):
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
        """校验指定型号的动作配置，再将位置、速度和力矩填入表格。"""
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

        # 配置有效后再清空旧表格，避免读取失败时丢失正在查看的内容。
        table = self.ui.tableWidget_hand_actions
        self._displayed_hand_model = None
        table.setRowCount(0)
        table.setColumnCount(len(joint_names) + 3)
        table.setHorizontalHeaderLabels(["动作名称", *joint_names, "速度", "力矩"])
        table.setRowCount(len(actions))
        for row, (name, action) in enumerate(actions.items()):
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 0, name_item)
            for column, position in enumerate(action["positions"], start=1):
                table.setItem(row, column, QTableWidgetItem(str(position)))
            table.setItem(row, len(joint_names) + 1, QTableWidgetItem(str(action.get("speed", hand_config.get("default_speed", 255)))))
            table.setItem(row, len(joint_names) + 2, QTableWidgetItem(str(action.get("force", hand_config.get("default_force", 255)))))
        # 保存加载时的动作名称和表格内容，后续用于检测外部修改和未保存编辑。
        self._displayed_hand_model = hand_model
        self.ui.label_hand_model_value.setText(hand_model)
        self._loaded_action_names = tuple(actions)
        self._default_hand_position = hand_config.get("position_range", {}).get("min", 0)
        self._default_hand_speed = hand_config.get("default_speed", 255)
        self._default_hand_force = hand_config.get("default_force", 255)
        self._saved_table_snapshot = self._table_snapshot()
        self.ui.pushButton_save_hand_actions.setEnabled(True)
        self.ui.pushButton_add_hand_actions.setEnabled(True)
        self.update_delete_hand_action_button()
        self.refresh_hand_action_choices()
        for combo, key in ((self.ui.comboBox_hand_current_close, "current_close"),
                           (self.ui.comboBox_hand_current_open, "current_open")):
            if hand_config.get(key) in actions:
                combo.setCurrentText(hand_config[key])
        self._saved_action_selection = self._action_selection()
        return True

    def refresh_hand_actions(self, hand_model):
        """显示主界面选中型号的动作配置。"""
        if not self._confirm_pending_hand_changes():
            return False
        try:
            config = self._read_hand_config()
        except (OSError, ValueError, TypeError) as error:
            Logger.instance().error(f"读取灵巧手配置失败: {error}")
            return False

        if hand_model in config:
            return self._load_hand_actions(hand_model, config)

        if hand_model:
            Logger.instance().error(f"配置文件中没有 {hand_model} 的灵巧手动作")
        self._displayed_hand_model = None
        self._loaded_action_names = ()
        self._saved_table_snapshot = ()
        self._saved_action_selection = ()
        self.ui.label_hand_model_value.setText(f"{hand_model}（未配置）" if hand_model else "未选择")
        table = self.ui.tableWidget_hand_actions
        table.setRowCount(0)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["动作名称"])
        self.ui.pushButton_save_hand_actions.setEnabled(False)
        self.ui.pushButton_add_hand_actions.setEnabled(False)
        self.ui.pushButton_delete_hand_actions.setEnabled(False)
        self.refresh_hand_action_choices()
        return True

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

        # 新动作的关节位置、速度和力矩取当前型号的默认值。
        row = table.rowCount()
        table.insertRow(row)
        name_item = QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(row, 0, name_item)
        for column in range(1, table.columnCount() - 2):
            table.setItem(row, column, QTableWidgetItem(str(self._default_hand_position)))
        table.setItem(row, table.columnCount() - 2, QTableWidgetItem(str(self._default_hand_speed)))
        table.setItem(row, table.columnCount() - 1, QTableWidgetItem(str(self._default_hand_force)))
        table.selectRow(row)
        self.refresh_hand_action_choices()

    def delete_hand_actions(self):
        """从表格移除选中的动作，等待 Save Actions 写入配置。"""
        if self._displayed_hand_model is None:
            return
        table = self.ui.tableWidget_hand_actions
        # 倒序删除，避免行号移动影响后续选中行。
        for row in sorted((index.row() for index in table.selectionModel().selectedRows()), reverse=True):
            table.removeRow(row)
        self.refresh_hand_action_choices()

    def save_hand_actions(self):
        """把表格中的关节位置、速度和力矩写回当前型号的动作配置。"""
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
            # 保存前确认配置结构未被外部改动，避免用旧表格覆盖新的动作列表。
            if table.columnCount() != len(joint_names) + 3 or tuple(actions) != self._loaded_action_names:
                raise ValueError("配置中的动作或关节已变化，请重新打开设置")
            if [table.horizontalHeaderItem(i + 1).text() for i in range(len(joint_names))] != joint_names:
                raise ValueError("关节名称已变化，请重新打开设置")

            # 先验证并组装所有动作，全部通过后再一次性写入文件。
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
                action_params = {}
                for offset, key, label in ((1, "speed", "速度"), (2, "force", "力矩")):
                    item = table.item(row, len(joint_names) + offset)
                    value = item.text().strip() if item else ""
                    try:
                        action_params[key] = int(value)
                    except ValueError as error:
                        raise ValueError(f"动作 {action_name} 的{label}必须是整数") from error
                action = actions.get(action_name)
                if action is None:
                    action = {
                        "description": "",
                        "speed": hand_config.get("default_speed", 255),
                        "force": hand_config.get("default_force", 255),
                    }
                updated_actions[action_name] = {**action, "positions": positions, **action_params}

            hand_config["actions"] = updated_actions
            close_name, open_name = self._action_selection()
            if close_name not in updated_actions or open_name not in updated_actions:
                raise ValueError("请为 Close 和 Open 选择动作")
            hand_config["current_close"] = close_name
            hand_config["current_open"] = open_name
            content = (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            # QSaveFile 先写临时文件，提交成功后才替换原配置。
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
        self._saved_action_selection = self._action_selection()
        Logger.instance().info(f"{hand_model} 灵巧手动作已保存")
        return True

    def save_slave_param(self):
        """Save seven home joints and motion parameters atomically."""
        try:
            velocity = float(self.ui.lineEdit_slave_arm_vel.text().strip())
            acceleration = float(self.ui.lineEdit_slave_arm_acc.text().strip())
            jerk = float(self.ui.lineEdit_slave_arm_jerk.text().strip())
            if not all(math.isfinite(value) and value > 0 for value in (velocity, acceleration, jerk)):
                raise ValueError
        except ValueError:
            Logger.instance().error("从手速度、加速度、加加速度必须是有限的正数")
            return False

        try:
            home_joints = [
                float(getattr(self.ui, f"lineEdit_slave_home_joint{index}").text().strip())
                for index in range(7)
            ]
            if not all(math.isfinite(value) for value in home_joints):
                raise ValueError
        except ValueError:
            Logger.instance().error("Home Pos 必须填写 7 个有限的关节角度（°）")
            return False

        params = {
            "SERVO_J_VMAX": velocity,
            "SERVO_J_AVMAX": acceleration,
            "SERVO_J_JMAX": jerk,
            "HOME_JOINTS": home_joints,
        }
        try:
            with self.CONFIG_PATH.open(encoding="utf-8") as file:
                config = json.load(file)
            slave_name = self._selected_slave_name(config)
            config[slave_name].update(params)
            content = (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            # 原子写入，避免写入失败时留下不完整的配置文件。
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
            return False

        self.slave_params = params
        Logger.instance().info(
            f"{slave_name} 从手参数及 7 个 Home Pos 角度已保存"
        )
        return True
