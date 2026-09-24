import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QThread, Signal

from src.ui.main_window import Ui_MainWindow
from src.devices.drivers.nrc_arm import NrcArm
from src.threads.master_robot_thread import MasterRobotThread

class MainWindow(QMainWindow):
    # 1. 在 MainWindow 中定义“请求”信号
    sig_request_connect = Signal()
    sig_request_disconnect = Signal()
    sig_request_enable = Signal()
    sig_request_disable = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 2. 私有状态变量
        self.if_master_connected = False
        self.if_slave_power_on = False

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



        # 6. 绑定 UI 按钮点击 -> 触发本地逻辑（判断发哪个请求信号）
        self.ui.Btn_robot_connect.clicked.connect(self.on_Btn_robot_connect_clicked)
        self.ui.pushButton_robot_PowerOn.clicked.connect(self.on_pushButton_robot_PowerOn_clicked)

    # ================= UI 按钮点击事件（判断状态，发射请求信号） =================

    def on_Btn_robot_connect_clicked(self):
        # UI 自己维护状态，决定是请求连接还是请求断开
        if self.if_master_connected:
            self.ui.label.setText("正在断开连接...")
            self.sig_request_disconnect.emit()  # 发射请求断开信号
        else:
            self.ui.label.setText("正在连接...")
            self.sig_request_connect.emit()     # 发射请求连接信号

    def on_pushButton_robot_PowerOn_clicked(self):
        if not self.if_master_connected:
            self.ui.label.setText("请先连接机器人")
            return

        if self.if_slave_power_on:
            self.ui.label.setText("正在下使能...")
            self.sig_request_disable.emit()     # 发射请求下使能信号
        else:
            self.ui.label.setText("正在上使能...")
            self.sig_request_enable.emit()      # 发射请求上使能信号

    # ================= 子线程执行完毕的回调（负责更新UI和状态） =================

    def on_connect_result(self, success, msg):
        if success:
            self.if_master_connected = True
            self.ui.Btn_robot_connect.setText("断开连接")
            self.ui.label.setText(f"状态: {msg}")
        else:
            self.if_master_connected = False
            self.ui.label.setText(f"状态: {msg}")

    def on_disconnect_result(self, success, msg):
        if success:
            self.if_master_connected = False
            self.if_slave_power_on = False
            self.ui.Btn_robot_connect.setText("连接机械臂")
            self.ui.label.setText(f"状态: {msg}")

    def on_enable_result(self, success, msg):
        if success:
            self.if_slave_power_on = True
            self.ui.pushButton_robot_PowerOn.setText("下使能")
            self.ui.label.setText(f"状态: {msg}")

    def on_disable_result(self, success, msg):
        if success:
            self.if_slave_power_on = False
            self.ui.pushButton_robot_PowerOn.setText("上使能")
            self.ui.label.setText(f"状态: {msg}")

    # ================= 安全退出 =================
    def closeEvent(self, event):
        print("正在关闭线程...")
        self.master_arm_thread.quit()
        self.master_arm_thread.wait()
        print("线程已安全退出")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())