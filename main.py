import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit
from PySide6.QtCore import QThread, Signal, QTimer

from src.ui.main_window import Ui_MainWindow
from src.ui.settings_dialog import SettingsDialog
from src.ui.log_stream import Logger
from src.devices.drivers_factory import create_master_arm
from src.devices.drivers_factory import create_camera
from src.threads.slave_robot_thread import SlaveRobotThread
from src.threads.master_robot_thread import MasterRobotThread
from src.threads.hand_thread import HandThread
from serial.tools import list_ports
from src.shared_data.robot_share_data import RobotSharedMemory
from src.devices.drivers.Link_hand import LinkHand

STYLE_PATH = Path(__file__).resolve().parent / "src" / "res" / "style" / "main_window.qss"

class MainWindow(QMainWindow):

    #define signals to request actions in the worker thread slave_arm_worker
    sig_request_connect = Signal(str, str)
    sig_request_disconnect = Signal()
    sig_request_enable = Signal()
    sig_request_disable = Signal()
    sig_request_read_pos = Signal(int)
    sig_request_stop_read_pos = Signal()
    sig_request_start_follow = Signal(int)
    sig_request_stop_follow = Signal()
    sig_request_sync_hand_trigger = Signal()

    #define signals to request actions in the worker thread master_arm_worker
    sig_request_master_connect = Signal()
    sig_request_master_disconnect = Signal()
    sig_request_master_read_pos = Signal(int)
    sig_request_master_stop_read_pos = Signal()

    #define signals to request actions in the hand thread
    sig_request_hand_connect = Signal(str, str, str, str)
    sig_request_hand_disconnect = Signal()
    sig_request_hand_set_joint_positions = Signal(list)
    sig_request_hand_set_speed = Signal(list)


    #test
    sig_request_open_servoj = Signal()
    sig_request_close_servoj = Signal()
    sig_request_move_servoj = Signal()
    sig_request_movej = Signal(list, float, float, float)  # target_positions, speed, acceleration, deceleration

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        for label in (self.ui.label_master_status, self.ui.label_slave_status):
            label.setProperty("uiRole", "armStatus")
        for index in range(1, 4):
            getattr(self.ui, f"label_camera_status_{index}").setProperty("uiRole", "cameraStatus")
            getattr(self.ui, f"label_camera_preview_{index}").setProperty("uiRole", "cameraPreview")
        style = STYLE_PATH.read_text(encoding="utf-8")
        self.setStyleSheet(style.replace("__STYLE_DIR__", STYLE_PATH.parent.as_posix()))
        self.shared_robot_data = RobotSharedMemory()
        self.settings_dialog = SettingsDialog(self.shared_robot_data, self)
        self.init_log_window()

        self.if_master_connected = False
        self.if_slave_connected = False
        self.if_slave_power_on = False
        self.if_hand_connected = False

        self.if_start_follow = False

        self.init_ui_state()
        self.init_camera_ui()

        self.init_thread()


    def init_log_window(self):
        self.logger = Logger.instance()
        self.ui.pushButton_clear_log.clicked.connect(self.clear_log)
        self._log_timer = QTimer(self)
        self._log_timer.timeout.connect(self.flush_log)
        self._log_timer.start(100)
        Logger.instance().info("Activity log is ready")

    def clear_log(self):
        self.logger.clear()
        self.ui.plainTextEdit_log.clear()

    def flush_log(self):
        lines = self.logger.take_messages()
        if not lines:
            return
        editor = self.ui.plainTextEdit_log
        scrollbar = editor.verticalScrollBar()
        old_position = scrollbar.value()
        editor.appendPlainText("\n".join(lines))
        if self.ui.checkBox_log_autoscroll.isChecked():
            scrollbar.setValue(scrollbar.maximum())
        else:
            scrollbar.setValue(old_position)


    def init_ui_state(self):
        self.ui.menuSet_Param.triggered.connect(self.show_settings)
        self._set_arm_status(self.ui.label_master_status, "disconnected")
        self._set_arm_status(self.ui.label_slave_status, "disconnected")
        #Bind button click command slave arm
        self.ui.Btn_robot_connect.clicked.connect(self.on_Btn_robot_connect_clicked)
        self.ui.pushButton_robot_PowerOn.clicked.connect(self.on_pushButton_robot_PowerOn_clicked)

        #master arm click command
        self.ui.pushButton_connect_master_arm.clicked.connect(self.on_pushButton_master_connect_clicked)
        self.ui.pushButton_refresh_master_port.clicked.connect(self.on_pushButton_refresh_master_port_clicked)

        #Bind button click command start/stop follow
        self.ui.pushButton_start_follow.clicked.connect(self.on_pushButton_start_follow_clicked)

        #Bind button click command hand
        self.ui.pushButton_refresh_hand_connect_info.clicked.connect(self.on_pushButton_refresh_hand_connect_info_clicked)
        self.ui.pushButton_connect_hand.clicked.connect(self.on_pushButton_hand_connect_clicked)
  
        #test
#region========================================camera====================================================
    def init_camera_ui(self):
        self.ui.pushButton_camera_refresh.clicked.connect(self.on_camera_refresh_clicked)

    def on_camera_refresh_clicked(self):
        model = self.ui.comboBox_camera_model.currentText().strip()
        camera_type = {"RealSenseD435": "D435"}.get(model, model)
        combos = (
            self.ui.comboBox_camera_device_side,
            self.ui.comboBox_camera_device_front,
            self.ui.comboBox_camera_device_hand,
        )
        selected_serials = [combo.currentData() for combo in combos]
        for combo in combos:
            combo.clear()

        try:
            devices = create_camera(camera_type).list_devices()
        except Exception as error:
            for combo in combos:
                combo.setPlaceholderText("Refresh failed")
            message = f"Failed to refresh {model} devices: {error}"
            Logger.instance().error(message)
            self.ui.statusbar.showMessage(message)
            return

        for index, (combo, selected_serial) in enumerate(zip(combos, selected_serials)):
            combo.setPlaceholderText("No devices found")
            for name, serial in devices:
                combo.addItem(f"{name} ({serial})", serial)
            previous_index = combo.findData(selected_serial) if selected_serial else -1
            if previous_index >= 0:
                combo.setCurrentIndex(previous_index)
            elif index < len(devices):
                combo.setCurrentIndex(index)

        message = f"Found {len(devices)} {model} device(s)"
        Logger.instance().info(message)
        self.ui.statusbar.showMessage(message)
        
#endregion========================================camera====================================================

    @staticmethod
    def _set_arm_status(label, state, message=""):
        labels = {
            "disconnected": "● Disconnected",
            "connecting": "● Connecting",
            "disconnecting": "● Disconnecting",
            "connected": "● Connected",
            "failed": "● Connection failed",
            "disconnect_failed": "● Disconnection failed",
        }
        label.setText(labels[state])
        label.setToolTip(message)
        label.setProperty("armState", state)
        label.style().unpolish(label)
        label.style().polish(label)
        label.update()


    def show_settings(self):
        self.settings_dialog.refresh_hand_actions(prefer_connected=True)
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def init_thread(self):
        #init slave arm thread
        self.init_slave_arm_thread() 

        #init master arm thread
        self.init_master_arm_thread()

        #init hand thread
        self.init_hand_thread()


#region===================hand thread=========================
    def init_hand_thread(self):
        self.hand_thread = QThread()
        self.hand_worker = HandThread(self.shared_robot_data)
        self.hand_worker.moveToThread(self.hand_thread)

        # Connect signals to the worker's slots
        self.sig_request_hand_connect.connect(self.hand_worker.ConnectHand)
        self.sig_request_hand_disconnect.connect(self.hand_worker.Disconnect)
        self.sig_request_hand_set_joint_positions.connect(self.hand_worker.Set_joint_positions)
        self.sig_request_hand_set_speed.connect(self.hand_worker.Set_speed)
        self.settings_dialog.sig_test_hand_action.connect(self.hand_worker.ExecuteTestAction)
        self.slave_arm_worker.sig_hand_closed_changed.connect(self.hand_worker.ExecuteFollowState)

        # Connect the worker's signals to the main window's slots
        self.hand_worker.sig_connect_result.connect(self.on_hand_connect_result)
        self.hand_worker.sig_disconnect_result.connect(self.on_hand_disconnect_result)

        self.hand_thread.start()

    def on_hand_connect_result(self, success, msg):
        self.ui.pushButton_connect_hand.setEnabled(True)
        self.ui.comboBox_hand_model.setEnabled(True)
        self.ui.comboBox_hand_type.setEnabled(True)
        self.ui.comboBox_hand_comm_type.setEnabled(True)
        self.ui.comboBox_hand_comm_info.setEnabled(True)
        if success:
            Logger.instance().info(msg)
            self.ui.pushButton_connect_hand.setText("Disconnect")
            self.if_hand_connected = True
            self.settings_dialog.refresh_hand_actions(prefer_connected=True)
            if self.if_start_follow:
                self.sig_request_sync_hand_trigger.emit()
        else:
            Logger.instance().error(msg)

    def on_hand_disconnect_result(self, success, msg):
        if success:
            Logger.instance().info(f"[LinkHand] disconnected successfully")
            self.ui.pushButton_connect_hand.setText("Connect")
            self.if_hand_connected = False
            self.settings_dialog.update_hand_test_button()
        else:
            Logger.instance().error(f"[LinkHand] failed to disconnect: {msg}")

    def on_pushButton_refresh_hand_connect_info_clicked(self):
        combo = self.ui.comboBox_hand_comm_info
        previous_port = combo.currentText()
        combo.clear()
        comm_type = self.ui.comboBox_hand_comm_type.currentText().strip().lower()

        try:
            if comm_type in ("modebus", "modbus"):
                ports = [
                    port.device for port in list_ports.comports()
                    if port.vid is not None
                    or port.device.startswith(("/dev/ttyUSB", "/dev/ttyACM"))
                ]
            elif comm_type == "can":
                ports = []
                # Linux ARPHRD_CAN = 280; also detects renamed CAN interfaces.
                for interface in Path("/sys/class/net").glob("*"):
                    try:
                        if (interface / "type").read_text().strip() == "280":
                            ports.append(interface.name)
                    except OSError:
                        # An interface may disappear while refreshing.
                        continue
            else:
                return

            combo.addItems(sorted(set(ports)))
            index = combo.findText(previous_port)
            if index >= 0:
                combo.setCurrentIndex(index)
        except Exception as e:
            Logger.instance().error(f"[LinkHand] Failed to refresh communication ports: {e}")

    def on_pushButton_hand_connect_clicked(self):
        if self.if_hand_connected:
            self.sig_request_hand_disconnect.emit()
        else:
            hand_model = self.ui.comboBox_hand_model.currentText().strip()
            hand_type_ = self.ui.comboBox_hand_type.currentText().strip()
            hand_comm_type = self.ui.comboBox_hand_comm_type.currentText().strip()
            hand_comm_info = self.ui.comboBox_hand_comm_info.currentText().strip()

            self.ui.pushButton_connect_hand.setEnabled(False)
            self.ui.comboBox_hand_model.setEnabled(False)
            self.ui.comboBox_hand_type.setEnabled(False)
            self.ui.comboBox_hand_comm_type.setEnabled(False)
            self.ui.comboBox_hand_comm_info.setEnabled(False)
            self.sig_request_hand_connect.emit(
                hand_model, hand_type_, hand_comm_type, hand_comm_info
            )



#endregion===================hand thread=========================


#region================= 遥操作控制器 =================

    def on_pushButton_start_follow_clicked(self):
        if self.if_master_connected is False or self.if_slave_connected is False:
            Logger.instance().info("Connect the master and slave arms first")
            return
        if self.if_slave_power_on is False:
            Logger.instance().info("Enable the slave arm first")
            return
        if self.if_hand_connected is False:
            Logger.instance().info("Connect the hand first")
            return

        if self.if_start_follow:
            self.sig_request_stop_follow.emit()
        else:
            time_interval_ms = int(self.ui.lineEdit_follow_rate.text())
            self.sig_request_start_follow.emit(time_interval_ms)


    # 遥操作状态回调
    def on_teleop_state_changed(self, is_running):
        if is_running:
            self.ui.statusbar.showMessage("Teleoperation: Running")
        else:
            self.ui.statusbar.showMessage("Teleoperation: Stopped")

    def on_follow_result(self, success):
        if success:
            self.ui.pushButton_start_follow.setText("Stop Follow")
            self.if_start_follow = True
        else:
            self.if_start_follow = False
            self.ui.pushButton_start_follow.setText("Start Follow")

# endregion================= 遥操作控制器 =================


 #region================= master arm thread =====================
    def init_master_arm_thread(self):
        self.master_arm = create_master_arm("Gello", name="GelloArm", port="/dev/ttyUSB0")

        self.master_arm_thread = QThread()
        self.master_arm_worker = MasterRobotThread(self.master_arm, self.shared_robot_data)
        self.master_arm_worker.moveToThread(self.master_arm_thread)

        self.sig_request_master_connect.connect(self.master_arm_worker.Connect)
        self.sig_request_master_disconnect.connect(self.master_arm_worker.Disconnect)
        self.sig_request_master_read_pos.connect(self.master_arm_worker.StartTimer)
        self.sig_request_master_stop_read_pos.connect(self.master_arm_worker.StopTimer)

        self.master_arm_worker.sig_connect_result.connect(self.on_master_arm_connect_result)
        self.master_arm_worker.sig_disconnect_result.connect(self.on_master_arm_disconnect_result)
        self.master_arm_worker.sig_joint_positions.connect(self.on_master_arm_joint_positions_updated)

        self.master_arm_thread.start()

    #region================= master arm thread 执行完毕的回调（负责更新UI和状态） =================
    def on_master_arm_joint_positions_updated(self, positions):
        if len(positions) < len(self.master_arm.ids):
                return
        for i in range(min(len(positions), 7)):
            getattr(self.settings_dialog.ui, f"lineEdit_master_joint{i}").setText(f"{positions[i]:.3f}")

    def on_master_arm_connect_result(self, success, msg):
        if success:
            self.if_master_connected = True
            self.ui.pushButton_connect_master_arm.setText("Disconnect")
            self._set_arm_status(self.ui.label_master_status, "connected", msg)
            self.ui.statusbar.showMessage(f"status: {msg}")
            self.on_master_robot_ReadPos()
        else:
            self.if_master_connected = False
            self.ui.pushButton_connect_master_arm.setText("Connect")
            self._set_arm_status(self.ui.label_master_status, "failed", msg)
            self.ui.statusbar.showMessage(f"status: {msg}")

    def on_master_arm_disconnect_result(self, success, msg):
        if success:
            self.if_master_connected = False
            self.ui.pushButton_connect_master_arm.setText("Connect")
            self._set_arm_status(self.ui.label_master_status, "disconnected", msg)
            self.ui.statusbar.showMessage(f"status: {msg}")
        else:
            self._set_arm_status(self.ui.label_master_status, "disconnect_failed", msg)
            self.ui.statusbar.showMessage(f"status: {msg}")

    #endregion================= master arm thread 执行完毕的回调（负责更新UI和状态） =================

    #region================= master arm thread button click =====================
    def on_pushButton_master_connect_clicked(self):
        if self.if_master_connected:
            self._set_arm_status(self.ui.label_master_status, "disconnecting")
            self.ui.statusbar.showMessage("Disconnecting...")
            self.sig_request_master_disconnect.emit() 
            self.sig_request_master_stop_read_pos.emit()  # Stop reading positions when connecting   
        else:
            self._set_arm_status(self.ui.label_master_status, "connecting")
            self.ui.statusbar.showMessage("Connecting...")
            self.sig_request_master_connect.emit()

    def on_pushButton_refresh_master_port_clicked(self):
        self.ui.comboBox_master_port.clear()
        for port in list_ports.comports():
            if port.device.startswith(("/dev/ttyUSB", "/dev/ttyACM")):
                self.ui.comboBox_master_port.addItem(port.device)

    def on_master_robot_ReadPos(self):
        try:
            interval_ms = int(self.ui.lineEdit_master_read_pos_rate.text())
        except ValueError:
            interval_ms = 100

        if interval_ms <= 0:
            interval_ms = 100

        self.sig_request_master_read_pos.emit(interval_ms)


    #endregion================= master arm thread button click =====================


 #endregion================= master arm thread =====================

 #region================= slave arm thread =====================
    def init_slave_arm_thread(self):
        # ================= 核心：moveToThread 组装 =================
        self.slave_arm_thread = QThread()
        self.slave_arm_worker = SlaveRobotThread(self.shared_robot_data)
        self.slave_arm_worker.moveToThread(self.slave_arm_thread)
        # ==========================================================

        # 4. 将 MainWindow 的请求信号 -> 连接到 Worker 的槽函数
        self.sig_request_connect.connect(self.slave_arm_worker.ConnectRobot)
        self.sig_request_disconnect.connect(self.slave_arm_worker.Disconnect)
        self.sig_request_enable.connect(self.slave_arm_worker.Enable)
        self.sig_request_disable.connect(self.slave_arm_worker.Disable)
        self.sig_request_read_pos.connect(self.slave_arm_worker.StartTimer)
        self.sig_request_stop_read_pos.connect(self.slave_arm_worker.StopTimer)
        self.sig_request_start_follow.connect(self.slave_arm_worker.StartFollow)
        self.sig_request_stop_follow.connect(self.slave_arm_worker.StopFollow)
        self.sig_request_sync_hand_trigger.connect(self.slave_arm_worker.SyncHandTriggerState)

        # 5. 将 Worker 的结果信号 -> 连接到 MainWindow 的更新回调
        self.slave_arm_worker.sig_connect_result.connect(self.on_connect_result)
        self.slave_arm_worker.sig_disconnect_result.connect(self.on_disconnect_result)
        self.slave_arm_worker.sig_enable_result.connect(self.on_enable_result)
        self.slave_arm_worker.sig_disable_result.connect(self.on_disable_result)
        self.slave_arm_worker.sig_joint_positions.connect(self.on_joint_positions_updated)
        self.slave_arm_worker.sig_tcp_positions.connect(self.on_tcp_positions_updated)
        self.slave_arm_worker.sig_follow_result.connect(self.on_follow_result)

        #test
        self.sig_request_open_servoj.connect(self.slave_arm_worker.OpenServoJ)
        self.sig_request_close_servoj.connect(self.slave_arm_worker.CloseServoJ)
        self.sig_request_move_servoj.connect(self.slave_arm_worker.testservoj)
        self.sig_request_movej.connect(self.slave_arm_worker.MoveJ)

        self.slave_arm_thread.start()

    def on_Btn_robot_connect_clicked(self):
        if self.if_slave_connected:
            self._set_arm_status(self.ui.label_slave_status, "disconnecting")
            self.ui.statusbar.showMessage("Disconnecting...")
            self.sig_request_disconnect.emit() 
            self.sig_request_stop_read_pos.emit()  # Stop reading positions when connecting   

        else:
            self._set_arm_status(self.ui.label_slave_status, "connecting")
            self.ui.statusbar.showMessage("Connecting...")
            IP_address = self.ui.lineEdit_slave_arm_ip.text().strip()
            if not IP_address:
                self._set_arm_status(self.ui.label_slave_status, "failed", "Please enter a valid IP address")
                self.ui.statusbar.showMessage("Please enter a valid IP address")
                return
            robot_type = self.ui.comboBox_robot_type.currentText().strip()
            self.ui.Btn_robot_connect.setEnabled(False)
            self.ui.comboBox_robot_type.setEnabled(False)
            self.sig_request_connect.emit(robot_type, IP_address)

    def on_pushButton_robot_PowerOn_clicked(self):
        if not self.if_slave_connected:
            self.ui.statusbar.showMessage("Please connect the robot first")
            return

        if self.if_slave_power_on:
            self.ui.statusbar.showMessage("Disabling...")
            self.sig_request_disable.emit()    
        else:
            self.ui.statusbar.showMessage("Enabling...")
            self.sig_request_enable.emit()      


    def on_pushButton_robot_ReadPos_clicked(self):
        try:
            interval_ms = int(self.ui.lineEdit_slave_read_pos_rate.text())
        except ValueError:
            interval_ms = 100

        if interval_ms <= 0:
            interval_ms = 100

        self.sig_request_read_pos.emit(interval_ms)

    def on_joint_positions_updated(self, positions):
        if len(positions) < 7:
                return
        for i, position in enumerate(positions[:7]):
            getattr(self.settings_dialog.ui, f"lineEdit_slave_joint{i}").setText(f"{position:.3f}")

    def on_tcp_positions_updated(self, positions):
        if len(positions) < 6:
            return
        for axis, position in zip("xyzabc", positions[:6]):
            getattr(self.settings_dialog.ui, f"lineEdit_slave_{axis}").setText(f"{position:.3f}")

    # region ================= slave arm thread 执行完毕的回调（负责更新UI和状态） =================

    def on_connect_result(self, success, msg):
        self.ui.Btn_robot_connect.setEnabled(True)
        self.ui.comboBox_robot_type.setEnabled(True)
        if success:
            self.if_slave_connected = True
            self.ui.Btn_robot_connect.setText("Disconnect")
            self._set_arm_status(self.ui.label_slave_status, "connected", msg)
            self.ui.statusbar.showMessage(f"status: {msg}")
            self.on_pushButton_robot_ReadPos_clicked()
        else:
            self.if_slave_connected = False
            self.ui.Btn_robot_connect.setText("Connect")
            self._set_arm_status(self.ui.label_slave_status, "failed", msg)
            self.ui.statusbar.showMessage(f"status: {msg}")

    def on_disconnect_result(self, success, msg):
        self.if_start_follow = False
        self.ui.pushButton_start_follow.setText("Start Follow")
        if success:
            self.if_slave_connected = False
            self.if_slave_power_on = False
            self.ui.Btn_robot_connect.setText("Connect")
            self.ui.pushButton_robot_PowerOn.setText("PowerOn")
            self._set_arm_status(self.ui.label_slave_status, "disconnected", msg)
            self.ui.statusbar.showMessage(f"status: {msg}")
        else:
            self._set_arm_status(self.ui.label_slave_status, "disconnect_failed", msg)
            self.ui.statusbar.showMessage(f"status: {msg}")

    def on_enable_result(self, success, msg):
        if success:
            self.if_slave_power_on = True
            self.ui.pushButton_robot_PowerOn.setText("Disable")
            self.ui.statusbar.showMessage(f"status: {msg}")

    def on_disable_result(self, success, msg):
        if success:
            self.if_slave_power_on = False
            self.ui.pushButton_robot_PowerOn.setText("Enable")
            self.ui.statusbar.showMessage(f"status: {msg}")

    # endregion ================= slave arm thread 执行完毕的回调（负责更新UI和状态） =================


#endregion================= slave arm thread =====================


    # region ================= 安全退出 =================
    def closeEvent(self, event):
        # Stop the hand worker before its QThread is destroyed.
        Logger.instance().info("Closing hand thread...")
        self.hand_thread.quit()
        self.hand_thread.wait()

        # Stop the slave arm thread
        Logger.instance().info("Closing slave arm thread...")
        self.slave_arm_thread.quit()
        self.slave_arm_thread.wait()

        # Stop the master arm thread
        Logger.instance().info("Closing master arm thread...")
        self.master_arm_thread.quit()
        self.master_arm_thread.wait()

        Logger.instance().info("Thread has exited safely")
        self.flush_log()
        self._log_timer.stop()
        event.accept()
    # endregion ================= 安全退出 =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
