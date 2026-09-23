import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from Src.Ui.main_window import Ui_MainWindow
from vendor.nrc import nrc_interface


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.Btn_robot_connect.clicked.connect(self.on_Btn_robot_connect_clicked)
        # wire the PowerOn button
        self.ui.pushButton_robot_PowerOn.clicked.connect(self.on_pushButton_robot_PowerOn_clicked)

        # 纳博特连接句柄
        self.Robot_Socket = None

        self.If_Connected = False
        self.If_PowerOn = False

    def on_Btn_robot_connect_clicked(self):
        
        try:
            if self.If_Connected:
                nrc_interface.disconnect_robot(self.Robot_Socket)
                self.Robot_Socket = None
                self.If_Connected = False
                self.ui.label.setText("已断开连接")
            else:
                # connect_robot returns a socketFd (or handle) used by other API calls
                self.Robot_Socket = nrc_interface.connect_robot("192.168.2.14", "6001")
                if self.Robot_Socket is -1:
                    self.ui.label.setText("连接失败: 返回的 socket 为 None")
                else:
                    self.ui.label.setText(f"已连接: {self.Robot_Socket}")
                    self.If_Connected = True
        except Exception as e:
            self.Robot_Socket = None
            self.ui.label.setText(f"连接失败: {e}")

    def on_pushButton_robot_PowerOn_clicked(self):
        if not self.Robot_Socket:
            self.ui.label.setText("请先连接机器人")
            return
        try:
            if self.If_PowerOn:
                nrc_interface.set_servo_poweroff(self.Robot_Socket)
                self.ui.label.setText("PowerOff 成功")
                self.If_PowerOn = False
            else:
                nrc_interface.set_servo_state(self.Robot_Socket, 1)
                res = nrc_interface.set_servo_poweron(self.Robot_Socket)
                # many C APIs return 0 on success
                if res == 0:
                    self.ui.label.setText("PowerOn 成功")
                    self.If_PowerOn = True
                else:
                    self.ui.label.setText(f"PowerOn 返回: {res}")
        except Exception as e:
            self.ui.label.setText(f"PowerOn 失败: {e}")


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())