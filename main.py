import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit
from PySide6.QtCore import QThread, Signal

from src.ui.main_window import Ui_MainWindow
from src.devices.drivers.nrc_arm import NrcArm
from src.threads.master_robot_thread import MasterRobotThread

class MainWindow(QMainWindow):

    #define signals to request actions in the worker thread
    sig_request_connect = Signal()
    sig_request_disconnect = Signal()
    sig_request_enable = Signal()
    sig_request_disable = Signal()
    sig_request_read_pos = Signal(int)
    sig_request_stop_read_pos = Signal()

    sig_request_open_servoj = Signal()
    sig_request_close_servoj = Signal()
    sig_request_move_servoj = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.if_master_connected = False
        self.if_slave_power_on = False

        self.init_thread()
        self.init_ui_state()


    def init_ui_state(self):
        #Bind button click command
        self.ui.Btn_robot_connect.clicked.connect(self.on_Btn_robot_connect_clicked)
        self.ui.pushButton_robot_PowerOn.clicked.connect(self.on_pushButton_robot_PowerOn_clicked)

        #test
        self.ui.pushButton_openServoj.clicked.connect(self.on_servoj_opened)
        self.ui.pushButton_Start.clicked.connect(self.on_start_servoj_move)
        self.ui.pushButton_closeServoj.clicked.connect(self.on_servoj_closed)


    def init_thread(self):
        #init master arm thread
        self.init_master_arm_thread()       

    #================= master arm thread =====================
    def init_master_arm_thread(self):
        # 3. 实例化硬件
        self.nrc_arm = NrcArm(name="NrcArm", ip_address="192.168.2.14", command_port=6001, servo_port=7000)

        # ================= 核心：moveToThread 组装 =================
        self.master_arm_thread = QThread()
        self.master_arm_worker = MasterRobotThread(self.nrc_arm)
        self.master_arm_worker.moveToThread(self.master_arm_thread)
        # ==========================================================

        # 4. 将 MainWindow 的请求信号 -> 连接到 Worker 的槽函数
        self.sig_request_connect.connect(self.master_arm_worker.Connect)
        self.sig_request_disconnect.connect(self.master_arm_worker.Disconnect)
        self.sig_request_enable.connect(self.master_arm_worker.Enable)
        self.sig_request_disable.connect(self.master_arm_worker.Disable)
        self.sig_request_read_pos.connect(self.master_arm_worker.StartTimer)
        self.sig_request_stop_read_pos.connect(self.master_arm_worker.StopTimer)

        # 5. 将 Worker 的结果信号 -> 连接到 MainWindow 的更新回调
        self.master_arm_worker.sig_connect_result.connect(self.on_connect_result)
        self.master_arm_worker.sig_disconnect_result.connect(self.on_disconnect_result)
        self.master_arm_worker.sig_enable_result.connect(self.on_enable_result)
        self.master_arm_worker.sig_disable_result.connect(self.on_disable_result)
        self.master_arm_worker.sig_joint_positions.connect(self.on_joint_positions_updated)
        self.master_arm_worker.sig_tcp_positions.connect(self.on_tcp_positions_updated)

        #test
        self.sig_request_open_servoj.connect(self.master_arm_worker.OpenServoJ)
        self.sig_request_close_servoj.connect(self.master_arm_worker.CloseServoJ)
        self.sig_request_move_servoj.connect(self.master_arm_worker.testservoj)

        self.master_arm_thread.start()


    def on_Btn_robot_connect_clicked(self):
        if self.if_master_connected:
            self.ui.label.setText("Disconnecting...")
            self.sig_request_disconnect.emit() 
            self.sig_request_stop_read_pos.emit()  # Stop reading positions when connecting   

        else:
            self.ui.label.setText("Connecting...")
            self.sig_request_connect.emit() 

    def on_pushButton_robot_PowerOn_clicked(self):
        if not self.if_master_connected:
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
            interval_ms = int(self.ui.lineEdit_read_pos_rate.text())
        except ValueError:
            interval_ms = 100

        if interval_ms <= 0:
            interval_ms = 100

        self.sig_request_read_pos.emit(interval_ms)

    def on_joint_positions_updated(self, positions):
        if len(positions) < 7:
                return
        self.ui.lineEdit_master_joint0.setText(f"{positions[0]:.3f}")
        self.ui.lineEdit_master_joint1.setText(f"{positions[1]:.3f}")
        self.ui.lineEdit_master_joint2.setText(f"{positions[2]:.3f}")
        self.ui.lineEdit_master_joint3.setText(f"{positions[3]:.3f}")
        self.ui.lineEdit_master_joint4.setText(f"{positions[4]:.3f}")
        self.ui.lineEdit_master_joint5.setText(f"{positions[5]:.3f}")
        self.ui.lineEdit_master_joint6.setText(f"{positions[6]:.3f}")

    def on_tcp_positions_updated(self, positions):
        if len(positions) < 6:
            return
        self.ui.lineEdit_master_x.setText(f"{positions[0]:.3f}")
        self.ui.lineEdit_master_y.setText(f"{positions[1]:.3f}")
        self.ui.lineEdit_master_z.setText(f"{positions[2]:.3f}")
        self.ui.lineEdit_master_a.setText(f"{positions[3]:.3f}")
        self.ui.lineEdit_master_b.setText(f"{positions[4]:.3f}")
        self.ui.lineEdit_master_c.setText(f"{positions[5]:.3f}")

    def on_servoj_opened(self):
        self.sig_request_open_servoj.emit()

    def on_servoj_closed(self):
        self.sig_request_close_servoj.emit()

    def on_start_servoj_move(self):
        self.sig_request_move_servoj.emit()


    # ================= master arm thread 执行完毕的回调（负责更新UI和状态） =================

    def on_connect_result(self, success, msg):
        if success:
            self.if_master_connected = True
            self.ui.Btn_robot_connect.setText("Disconnect")
            self.ui.label.setText(f"status: {msg}")
            self.on_pushButton_robot_ReadPos_clicked()
        else:
            self.if_master_connected = False
            self.ui.label.setText(f"status: {msg}")

    def on_disconnect_result(self, success, msg):
        if success:
            self.if_master_connected = False
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

    # ================= 安全退出 =================
    def closeEvent(self, event):
        print("Closing thread...")
        self.master_arm_thread.quit()
        self.master_arm_thread.wait()
        print("Thread has exited safely")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())