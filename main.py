import sys

from PySide6.QtWidgets import QApplication, QMainWindow
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

    def init_thread(self):
        #init master arm thread
        self.init_master_arm_thread()       

    #================= 主臂 =====================
    def init_master_arm_thread(self):
        # 3. 实例化硬件
        self.nrc_arm = NrcArm(name="NrcArm", ip_address="192.168.2.14", port=6001)

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

        # 5. 将 Worker 的结果信号 -> 连接到 MainWindow 的更新回调
        self.master_arm_worker.sig_connect_result.connect(self.on_connect_result)
        self.master_arm_worker.sig_disconnect_result.connect(self.on_disconnect_result)
        self.master_arm_worker.sig_enable_result.connect(self.on_enable_result)
        self.master_arm_worker.sig_disable_result.connect(self.on_disable_result)

        self.master_arm_thread.start()

    def on_Btn_robot_connect_clicked(self):
        if self.if_master_connected:
            self.ui.label.setText("Disconnecting...")
            self.sig_request_disconnect.emit() 
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

    # ================= 子线程执行完毕的回调（负责更新UI和状态） =================

    def on_connect_result(self, success, msg):
        if success:
            self.if_master_connected = True
            self.ui.Btn_robot_connect.setText("Disconnect")
            self.ui.label.setText(f"status: {msg}")
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