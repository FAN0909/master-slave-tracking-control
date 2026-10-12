import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit
from PySide6.QtCore import QThread, Signal

from src.ui.main_window import Ui_MainWindow
from src.devices.drivers.nrc_arm import NrcArm
from src.threads.slave_robot_thread import SlaveRobotThread
from src.threads.master_robot_thread import MasterRobotThread
from src.devices.drivers.gello_arm import GelloArm
from src.controller.teleop_controller import TeleopController
from serial.tools import list_ports

class MainWindow(QMainWindow):

    #define signals to request actions in the worker thread slave_arm_worker
    sig_request_connect = Signal()
    sig_request_disconnect = Signal()
    sig_request_enable = Signal()
    sig_request_disable = Signal()
    sig_request_read_pos = Signal(int)
    sig_request_stop_read_pos = Signal()

    #define signals to request actions in the worker thread master_arm_worker
    sig_request_master_connect = Signal()
    sig_request_master_disconnect = Signal()
    sig_request_master_read_pos = Signal(int)
    sig_request_master_stop_read_pos = Signal()

    #test
    sig_request_open_servoj = Signal()
    sig_request_close_servoj = Signal()
    sig_request_move_servoj = Signal()
    sig_request_movej = Signal(list, float, float, float)  # target_positions, speed, acceleration, deceleration

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.if_master_connected = False
        self.if_slave_connected = False
        self.if_slave_power_on = False

        self.if_start_follow = False

        self.init_thread()
        self.init_ui_state()

        self.init_teleop_controller()


    def init_ui_state(self):
        #Bind button click command slave arm
        self.ui.Btn_robot_connect.clicked.connect(self.on_Btn_robot_connect_clicked)
        self.ui.pushButton_robot_PowerOn.clicked.connect(self.on_pushButton_robot_PowerOn_clicked)

        #master arm click command
        self.ui.pushButton_connect_master_arm.clicked.connect(self.on_pushButton_master_connect_clicked)
        self.ui.pushButton_refresh_master_port.clicked.connect(self.on_pushButton_refresh_master_port_clicked)

        #Bind button click command start/stop follow
        self.ui.pushButton_start_follow.clicked.connect(self.on_pushButton_start_follow_clicked)

        #test
        self.ui.pushButton_openServoj.clicked.connect(self.on_servoj_opened)
        self.ui.pushButton_Start.clicked.connect(self.on_start_servoj_move)
        self.ui.pushButton_closeServoj.clicked.connect(self.on_servoj_closed)


    def init_thread(self):
        #init slave arm thread
        self.init_slave_arm_thread() 

        #init master arm thread
        self.init_master_arm_thread()


# ================= 遥操作控制器 =================
    def init_teleop_controller(self):

        # 【新增 1】创建遥操作控制器
        self.teleop_controller = TeleopController(self)

        # 【新增 2】主手读取到关节数据后，发送给遥操作控制器
        # 原有的 on_master_arm_joint_positions_updated 连接保留，
        # 因为它负责更新 UI 显示。
        self.master_arm_worker.sig_joint_positions.connect(
            self.teleop_controller.UpdateMasterJointPositions
        )

        # 【新增 3】控制器状态变化时，更新 UI 状态
        self.teleop_controller.sig_teleop_state_changed.connect(
            self.on_teleop_state_changed
        )

        # 新增：控制器的累计关节增量 -> 从手线程
        self.teleop_controller.sig_set_slave_target.connect(
            self.slave_arm_worker.AddServoJDelta
        )

    def on_pushButton_start_follow_clicked(self):
        if self.if_start_follow:

            self.sig_request_close_servoj.emit()  # close ServoJ
            self.teleop_controller.StopTeleop()
            self.ui.pushButton_start_follow.setText("Start Follow")
            self.if_start_follow = False
        else:
            self.sig_request_open_servoj.emit()
            if not self.if_servoj_open:
                self.ui.label.setText(" OpenServoJ failed, please check the robot status")
                return
            self.teleop_controller.StartTeleop()
            self.ui.pushButton_start_follow.setText("Stop Follow")
            self.if_start_follow = True

    # 【新增】遥操作状态回调
    def on_teleop_state_changed(self, is_running):
        if is_running:
            self.ui.label.setText("Teleoperation: Running")
        else:
            self.ui.label.setText("Teleoperation: Stopped")


# ================= 遥操作控制器 =================


 #region================= master arm thread =====================
    def init_master_arm_thread(self):
        self.master_arm = GelloArm(name="GelloArm", ids=[1, 2, 3, 4, 5, 6], port="/dev/ttyUSB0")

        self.master_arm_thread = QThread()
        self.master_arm_worker = MasterRobotThread(self.master_arm)
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
        for i in range(len(self.master_arm.ids)):
            getattr(self.ui, f"lineEdit_master_joint{i}").setText(f"{positions[i]:.3f}")

    def on_master_arm_connect_result(self, success, msg):
        if success:
            self.if_master_connected = True
            self.ui.pushButton_connect_master_arm.setText("Disconnect")
            self.ui.label.setText(f"status: {msg}")
            self.on_master_robot_ReadPos()
        else:
            self.if_master_connected = False
            self.ui.label.setText(f"status: {msg}")

    def on_master_arm_disconnect_result(self, success, msg):
        if success:
            self.if_master_connected = False
            self.ui.pushButton_connect_master_arm.setText("Connect")
            self.ui.label.setText(f"status: {msg}")

    #endregion================= master arm thread 执行完毕的回调（负责更新UI和状态） =================

    #region================= master arm thread button click =====================
    def on_pushButton_master_connect_clicked(self):
        if self.if_master_connected:
            self.ui.label.setText("Disconnecting...")
            self.sig_request_master_disconnect.emit() 
            self.sig_request_master_stop_read_pos.emit()  # Stop reading positions when connecting   
        else:
            self.ui.label.setText("Connecting...")
            self.master_arm.ids = [1, 2, 3, 4, 5, 6, 7] # Update the IDs in the arm
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
        # 3. 实例化硬件
        self.nrc_arm = NrcArm(name="NrcArm")

        # ================= 核心：moveToThread 组装 =================
        self.slave_arm_thread = QThread()
        self.slave_arm_worker = SlaveRobotThread(self.nrc_arm)
        self.slave_arm_worker.moveToThread(self.slave_arm_thread)
        # ==========================================================

        # 4. 将 MainWindow 的请求信号 -> 连接到 Worker 的槽函数
        self.sig_request_connect.connect(self.slave_arm_worker.Connect)
        self.sig_request_disconnect.connect(self.slave_arm_worker.Disconnect)
        self.sig_request_enable.connect(self.slave_arm_worker.Enable)
        self.sig_request_disable.connect(self.slave_arm_worker.Disable)
        self.sig_request_read_pos.connect(self.slave_arm_worker.StartTimer)
        self.sig_request_stop_read_pos.connect(self.slave_arm_worker.StopTimer)

        # 5. 将 Worker 的结果信号 -> 连接到 MainWindow 的更新回调
        self.slave_arm_worker.sig_connect_result.connect(self.on_connect_result)
        self.slave_arm_worker.sig_disconnect_result.connect(self.on_disconnect_result)
        self.slave_arm_worker.sig_enable_result.connect(self.on_enable_result)
        self.slave_arm_worker.sig_disable_result.connect(self.on_disable_result)
        self.slave_arm_worker.sig_joint_positions.connect(self.on_joint_positions_updated)
        self.slave_arm_worker.sig_tcp_positions.connect(self.on_tcp_positions_updated)

        #test
        self.sig_request_open_servoj.connect(self.slave_arm_worker.OpenServoJ)
        self.sig_request_close_servoj.connect(self.slave_arm_worker.CloseServoJ)
        self.sig_request_move_servoj.connect(self.slave_arm_worker.testservoj)
        self.sig_request_movej.connect(self.slave_arm_worker.MoveJ)

        self.slave_arm_thread.start()


    def on_Btn_robot_connect_clicked(self):
        if self.if_slave_connected:
            self.ui.label.setText("Disconnecting...")
            self.sig_request_disconnect.emit() 
            self.sig_request_stop_read_pos.emit()  # Stop reading positions when connecting   

        else:
            self.ui.label.setText("Connecting...")
            IP_address = self.ui.lineEdit_slave_arm_ip.text().strip()
            if not IP_address:
                self.ui.label.setText("Please enter a valid IP address")
                return
            self.nrc_arm.ip_address = IP_address  # Update the IP address in the arm
            self.sig_request_connect.emit() 

    def on_pushButton_robot_PowerOn_clicked(self):
        if not self.if_slave_connected:
            self.ui.label.setText("Please connect the robot first")
            return

        if self.if_slave_power_on:
            self.ui.label.setText("Disabling...")
            self.sig_request_disable.emit()    
        else:
            self.ui.label.setText("Enabling...")
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
        self.ui.lineEdit_slave_joint0.setText(f"{positions[0]:.3f}")
        self.ui.lineEdit_slave_joint1.setText(f"{positions[1]:.3f}")
        self.ui.lineEdit_slave_joint2.setText(f"{positions[2]:.3f}")
        self.ui.lineEdit_slave_joint3.setText(f"{positions[3]:.3f}")
        self.ui.lineEdit_slave_joint4.setText(f"{positions[4]:.3f}")
        self.ui.lineEdit_slave_joint5.setText(f"{positions[5]:.3f}")
        self.ui.lineEdit_slave_joint6.setText(f"{positions[6]:.3f}")

    def on_tcp_positions_updated(self, positions):
        if len(positions) < 6:
            return
        self.ui.lineEdit_slave_x.setText(f"{positions[0]:.3f}")
        self.ui.lineEdit_slave_y.setText(f"{positions[1]:.3f}")
        self.ui.lineEdit_slave_z.setText(f"{positions[2]:.3f}")
        self.ui.lineEdit_slave_a.setText(f"{positions[3]:.3f}")
        self.ui.lineEdit_slave_b.setText(f"{positions[4]:.3f}")
        self.ui.lineEdit_slave_c.setText(f"{positions[5]:.3f}")

    def on_servoj_opened(self):
        self.sig_request_open_servoj.emit()

    def on_servoj_closed(self):
        self.sig_request_close_servoj.emit()

    #test servoJ
    def on_start_servoj_move(self):
        self.sig_request_move_servoj.emit()
        #self.sig_request_movej.emit([0.0, -2.20, 0.440, 2.20, -0.50, 0.793, 0.0], 5.0, 50.0, 50.0)

    # region ================= slave arm thread 执行完毕的回调（负责更新UI和状态） =================

    def on_connect_result(self, success, msg):
        if success:
            self.if_slave_connected = True
            self.ui.Btn_robot_connect.setText("Disconnect")
            self.ui.label.setText(f"status: {msg}")
            self.on_pushButton_robot_ReadPos_clicked()
        else:
            self.if_slave_connected = False
            self.ui.label.setText(f"status: {msg}")

    def on_disconnect_result(self, success, msg):
        if success:
            self.if_slave_connected = False
            self.if_slave_power_on = False
            self.ui.Btn_robot_connect.setText("Connect")
            self.ui.label.setText(f"status: {msg}")

    def on_enable_result(self, success, msg):
        if success:
            self.if_slave_power_on = True
            self.ui.pushButton_robot_PowerOn.setText("Disable")
            self.ui.label.setText(f"status: {msg}")

    def on_disable_result(self, success, msg):
        if success:
            self.if_slave_power_on = False
            self.ui.pushButton_robot_PowerOn.setText("Enable")
            self.ui.label.setText(f"status: {msg}")

    # endregion ================= slave arm thread 执行完毕的回调（负责更新UI和状态） =================


#endregion================= slave arm thread =====================


    # region ================= 安全退出 =================
    def closeEvent(self, event):
        # Stop the slave arm thread
        print("Closing slave arm thread...")
        self.slave_arm_thread.quit()
        self.slave_arm_thread.wait()

        # Stop the master arm thread
        print("Closing master arm thread...")
        self.master_arm_thread.quit()
        self.master_arm_thread.wait()

        print("Thread has exited safely")
        event.accept()
    # endregion ================= 安全退出 =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())