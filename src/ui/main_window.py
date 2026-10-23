# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1349, 882)
        self.menuSet_Param = QAction(MainWindow)
        self.menuSet_Param.setObjectName(u"menuSet_Param")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_main = QVBoxLayout(self.centralwidget)
        self.verticalLayout_main.setSpacing(8)
        self.verticalLayout_main.setObjectName(u"verticalLayout_main")
        self.verticalLayout_main.setContentsMargins(10, 8, 10, 8)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.horizontalLayout_master_arm = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_master_arm.setSpacing(6)
        self.horizontalLayout_master_arm.setObjectName(u"horizontalLayout_master_arm")
        self.label_31 = QLabel(self.groupBox_2)
        self.label_31.setObjectName(u"label_31")

        self.horizontalLayout_master_arm.addWidget(self.label_31)

        self.comboBox_master_port = QComboBox(self.groupBox_2)
        self.comboBox_master_port.setObjectName(u"comboBox_master_port")

        self.horizontalLayout_master_arm.addWidget(self.comboBox_master_port)

        self.pushButton_refresh_master_port = QPushButton(self.groupBox_2)
        self.pushButton_refresh_master_port.setObjectName(u"pushButton_refresh_master_port")

        self.horizontalLayout_master_arm.addWidget(self.pushButton_refresh_master_port)

        self.label_38 = QLabel(self.groupBox_2)
        self.label_38.setObjectName(u"label_38")

        self.horizontalLayout_master_arm.addWidget(self.label_38)

        self.lineEdit_master_read_pos_rate = QLineEdit(self.groupBox_2)
        self.lineEdit_master_read_pos_rate.setObjectName(u"lineEdit_master_read_pos_rate")
        self.lineEdit_master_read_pos_rate.setMaximumSize(QSize(65, 16777215))

        self.horizontalLayout_master_arm.addWidget(self.lineEdit_master_read_pos_rate)

        self.pushButton_connect_master_arm = QPushButton(self.groupBox_2)
        self.pushButton_connect_master_arm.setObjectName(u"pushButton_connect_master_arm")

        self.horizontalLayout_master_arm.addWidget(self.pushButton_connect_master_arm)

        self.label_master_status = QLabel(self.groupBox_2)
        self.label_master_status.setObjectName(u"label_master_status")
        self.label_master_status.setMinimumSize(QSize(78, 0))

        self.horizontalLayout_master_arm.addWidget(self.label_master_status)

        self.horizontalLayout_master_arm.setStretch(1, 1)

        self.horizontalLayout.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_slave_arm = QHBoxLayout(self.groupBox)
        self.horizontalLayout_slave_arm.setSpacing(6)
        self.horizontalLayout_slave_arm.setObjectName(u"horizontalLayout_slave_arm")
        self.label_32 = QLabel(self.groupBox)
        self.label_32.setObjectName(u"label_32")

        self.horizontalLayout_slave_arm.addWidget(self.label_32)

        self.comboBox_robot_type = QComboBox(self.groupBox)
        self.comboBox_robot_type.addItem("")
        self.comboBox_robot_type.addItem("")
        self.comboBox_robot_type.setObjectName(u"comboBox_robot_type")

        self.horizontalLayout_slave_arm.addWidget(self.comboBox_robot_type)

        self.label_16 = QLabel(self.groupBox)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_slave_arm.addWidget(self.label_16)

        self.lineEdit_slave_arm_ip = QLineEdit(self.groupBox)
        self.lineEdit_slave_arm_ip.setObjectName(u"lineEdit_slave_arm_ip")

        self.horizontalLayout_slave_arm.addWidget(self.lineEdit_slave_arm_ip)

        self.label_30 = QLabel(self.groupBox)
        self.label_30.setObjectName(u"label_30")

        self.horizontalLayout_slave_arm.addWidget(self.label_30)

        self.lineEdit_slave_read_pos_rate = QLineEdit(self.groupBox)
        self.lineEdit_slave_read_pos_rate.setObjectName(u"lineEdit_slave_read_pos_rate")
        self.lineEdit_slave_read_pos_rate.setMaximumSize(QSize(65, 16777215))

        self.horizontalLayout_slave_arm.addWidget(self.lineEdit_slave_read_pos_rate)

        self.Btn_robot_connect = QPushButton(self.groupBox)
        self.Btn_robot_connect.setObjectName(u"Btn_robot_connect")

        self.horizontalLayout_slave_arm.addWidget(self.Btn_robot_connect)

        self.pushButton_robot_PowerOn = QPushButton(self.groupBox)
        self.pushButton_robot_PowerOn.setObjectName(u"pushButton_robot_PowerOn")

        self.horizontalLayout_slave_arm.addWidget(self.pushButton_robot_PowerOn)

        self.label_slave_status = QLabel(self.groupBox)
        self.label_slave_status.setObjectName(u"label_slave_status")
        self.label_slave_status.setMinimumSize(QSize(78, 0))

        self.horizontalLayout_slave_arm.addWidget(self.label_slave_status)

        self.horizontalLayout_slave_arm.setStretch(3, 1)

        self.horizontalLayout.addWidget(self.groupBox)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)

        self.verticalLayout_main.addLayout(self.horizontalLayout)

        self.horizontalLayout_control_panels = QHBoxLayout()
        self.horizontalLayout_control_panels.setSpacing(8)
        self.horizontalLayout_control_panels.setObjectName(u"horizontalLayout_control_panels")
        self.groupBox_hand_control = QGroupBox(self.centralwidget)
        self.groupBox_hand_control.setObjectName(u"groupBox_hand_control")
        self.verticalLayout_hand_control = QVBoxLayout(self.groupBox_hand_control)
        self.verticalLayout_hand_control.setSpacing(7)
        self.verticalLayout_hand_control.setObjectName(u"verticalLayout_hand_control")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.pushButton_connect_hand = QPushButton(self.groupBox_hand_control)
        self.pushButton_connect_hand.setObjectName(u"pushButton_connect_hand")

        self.gridLayout_5.addWidget(self.pushButton_connect_hand, 1, 4, 1, 1)

        self.label_34 = QLabel(self.groupBox_hand_control)
        self.label_34.setObjectName(u"label_34")

        self.gridLayout_5.addWidget(self.label_34, 1, 0, 1, 1)

        self.comboBox_hand_comm_type = QComboBox(self.groupBox_hand_control)
        self.comboBox_hand_comm_type.addItem("")
        self.comboBox_hand_comm_type.addItem("")
        self.comboBox_hand_comm_type.setObjectName(u"comboBox_hand_comm_type")

        self.gridLayout_5.addWidget(self.comboBox_hand_comm_type, 0, 3, 1, 1)

        self.label_35 = QLabel(self.groupBox_hand_control)
        self.label_35.setObjectName(u"label_35")

        self.gridLayout_5.addWidget(self.label_35, 0, 2, 1, 1)

        self.comboBox_hand_comm_info = QComboBox(self.groupBox_hand_control)
        self.comboBox_hand_comm_info.setObjectName(u"comboBox_hand_comm_info")

        self.gridLayout_5.addWidget(self.comboBox_hand_comm_info, 1, 3, 1, 1)

        self.label_36 = QLabel(self.groupBox_hand_control)
        self.label_36.setObjectName(u"label_36")

        self.gridLayout_5.addWidget(self.label_36, 1, 2, 1, 1)

        self.comboBox_hand_type = QComboBox(self.groupBox_hand_control)
        self.comboBox_hand_type.addItem("")
        self.comboBox_hand_type.addItem("")
        self.comboBox_hand_type.setObjectName(u"comboBox_hand_type")

        self.gridLayout_5.addWidget(self.comboBox_hand_type, 1, 1, 1, 1)

        self.pushButton_refresh_hand_connect_info = QPushButton(self.groupBox_hand_control)
        self.pushButton_refresh_hand_connect_info.setObjectName(u"pushButton_refresh_hand_connect_info")

        self.gridLayout_5.addWidget(self.pushButton_refresh_hand_connect_info, 0, 4, 1, 1)

        self.label_33 = QLabel(self.groupBox_hand_control)
        self.label_33.setObjectName(u"label_33")

        self.gridLayout_5.addWidget(self.label_33, 0, 0, 1, 1)

        self.comboBox_hand_model = QComboBox(self.groupBox_hand_control)
        self.comboBox_hand_model.addItem("")
        self.comboBox_hand_model.setObjectName(u"comboBox_hand_model")

        self.gridLayout_5.addWidget(self.comboBox_hand_model, 0, 1, 1, 1)


        self.verticalLayout_hand_control.addLayout(self.gridLayout_5)

        self.label_37 = QLabel(self.groupBox_hand_control)
        self.label_37.setObjectName(u"label_37")
        self.label_37.setWordWrap(True)

        self.verticalLayout_hand_control.addWidget(self.label_37)


        self.horizontalLayout_control_panels.addWidget(self.groupBox_hand_control)

        self.groupBox_follow_control = QGroupBox(self.centralwidget)
        self.groupBox_follow_control.setObjectName(u"groupBox_follow_control")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_follow_control)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_follow_hint = QLabel(self.groupBox_follow_control)
        self.label_follow_hint.setObjectName(u"label_follow_hint")
        self.label_follow_hint.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_follow_hint)

        self.horizontalLayout_follow_start = QHBoxLayout()
        self.horizontalLayout_follow_start.setObjectName(u"horizontalLayout_follow_start")
        self.pushButton_start_follow = QPushButton(self.groupBox_follow_control)
        self.pushButton_start_follow.setObjectName(u"pushButton_start_follow")

        self.horizontalLayout_follow_start.addWidget(self.pushButton_start_follow)

        self.label_follow_interval = QLabel(self.groupBox_follow_control)
        self.label_follow_interval.setObjectName(u"label_follow_interval")

        self.horizontalLayout_follow_start.addWidget(self.label_follow_interval)

        self.lineEdit_follow_rate = QLineEdit(self.groupBox_follow_control)
        self.lineEdit_follow_rate.setObjectName(u"lineEdit_follow_rate")

        self.horizontalLayout_follow_start.addWidget(self.lineEdit_follow_rate)

        self.pushButton_slave_home_pos = QPushButton(self.groupBox_follow_control)
        self.pushButton_slave_home_pos.setObjectName(u"pushButton_slave_home_pos")

        self.horizontalLayout_follow_start.addWidget(self.pushButton_slave_home_pos)


        self.verticalLayout.addLayout(self.horizontalLayout_follow_start)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_start_recod = QPushButton(self.groupBox_follow_control)
        self.pushButton_start_recod.setObjectName(u"pushButton_start_recod")

        self.gridLayout.addWidget(self.pushButton_start_recod, 1, 1, 1, 1)

        self.pushButton_stop_recod = QPushButton(self.groupBox_follow_control)
        self.pushButton_stop_recod.setObjectName(u"pushButton_stop_recod")

        self.gridLayout.addWidget(self.pushButton_stop_recod, 1, 2, 1, 1)

        self.pushButton_discard_episode = QPushButton(self.groupBox_follow_control)
        self.pushButton_discard_episode.setObjectName(u"pushButton_discard_episode")

        self.gridLayout.addWidget(self.pushButton_discard_episode, 1, 4, 1, 1)

        self.label_2 = QLabel(self.groupBox_follow_control)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.pushButton_save_episode = QPushButton(self.groupBox_follow_control)
        self.pushButton_save_episode.setObjectName(u"pushButton_save_episode")

        self.gridLayout.addWidget(self.pushButton_save_episode, 1, 3, 1, 1)

        self.lineEdit_save_file_path = QLineEdit(self.groupBox_follow_control)
        self.lineEdit_save_file_path.setObjectName(u"lineEdit_save_file_path")

        self.gridLayout.addWidget(self.lineEdit_save_file_path, 0, 1, 1, 3)

        self.pushButton_browse_save_path = QPushButton(self.groupBox_follow_control)
        self.pushButton_browse_save_path.setObjectName(u"pushButton_browse_save_path")

        self.gridLayout.addWidget(self.pushButton_browse_save_path, 0, 4, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)


        self.horizontalLayout_control_panels.addWidget(self.groupBox_follow_control)

        self.horizontalLayout_control_panels.setStretch(0, 1)
        self.horizontalLayout_control_panels.setStretch(1, 1)

        self.verticalLayout_main.addLayout(self.horizontalLayout_control_panels)

        self.groupBox_camera_monitor = QGroupBox(self.centralwidget)
        self.groupBox_camera_monitor.setObjectName(u"groupBox_camera_monitor")
        self.verticalLayout_camera_monitor = QVBoxLayout(self.groupBox_camera_monitor)
        self.verticalLayout_camera_monitor.setSpacing(6)
        self.verticalLayout_camera_monitor.setObjectName(u"verticalLayout_camera_monitor")
        self.horizontalLayout_camera_toolbar = QHBoxLayout()
        self.horizontalLayout_camera_toolbar.setObjectName(u"horizontalLayout_camera_toolbar")
        self.label_camera_monitor_hint = QLabel(self.groupBox_camera_monitor)
        self.label_camera_monitor_hint.setObjectName(u"label_camera_monitor_hint")

        self.horizontalLayout_camera_toolbar.addWidget(self.label_camera_monitor_hint)

        self.horizontalSpacer_camera_toolbar = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_camera_toolbar.addItem(self.horizontalSpacer_camera_toolbar)

        self.label = QLabel(self.groupBox_camera_monitor)
        self.label.setObjectName(u"label")

        self.horizontalLayout_camera_toolbar.addWidget(self.label)

        self.comboBox_camera_model = QComboBox(self.groupBox_camera_monitor)
        self.comboBox_camera_model.addItem("")
        self.comboBox_camera_model.setObjectName(u"comboBox_camera_model")

        self.horizontalLayout_camera_toolbar.addWidget(self.comboBox_camera_model)

        self.label_camera_frame_interval = QLabel(self.groupBox_camera_monitor)
        self.label_camera_frame_interval.setObjectName(u"label_camera_frame_interval")

        self.horizontalLayout_camera_toolbar.addWidget(self.label_camera_frame_interval)

        self.lineEdit_camera_frame_interval = QLineEdit(self.groupBox_camera_monitor)
        self.lineEdit_camera_frame_interval.setObjectName(u"lineEdit_camera_frame_interval")
        self.lineEdit_camera_frame_interval.setMaximumSize(QSize(65, 16777215))

        self.horizontalLayout_camera_toolbar.addWidget(self.lineEdit_camera_frame_interval)

        self.pushButton_camera_refresh = QPushButton(self.groupBox_camera_monitor)
        self.pushButton_camera_refresh.setObjectName(u"pushButton_camera_refresh")
        self.pushButton_camera_refresh.setEnabled(True)

        self.horizontalLayout_camera_toolbar.addWidget(self.pushButton_camera_refresh)

        self.pushButton_camera_connect_all = QPushButton(self.groupBox_camera_monitor)
        self.pushButton_camera_connect_all.setObjectName(u"pushButton_camera_connect_all")
        self.pushButton_camera_connect_all.setEnabled(True)

        self.horizontalLayout_camera_toolbar.addWidget(self.pushButton_camera_connect_all)

        self.pushButton_camera_disconnect_all = QPushButton(self.groupBox_camera_monitor)
        self.pushButton_camera_disconnect_all.setObjectName(u"pushButton_camera_disconnect_all")
        self.pushButton_camera_disconnect_all.setEnabled(True)

        self.horizontalLayout_camera_toolbar.addWidget(self.pushButton_camera_disconnect_all)


        self.verticalLayout_camera_monitor.addLayout(self.horizontalLayout_camera_toolbar)

        self.horizontalLayout_camera_cards = QHBoxLayout()
        self.horizontalLayout_camera_cards.setSpacing(8)
        self.horizontalLayout_camera_cards.setObjectName(u"horizontalLayout_camera_cards")
        self.groupBox_camera_1 = QGroupBox(self.groupBox_camera_monitor)
        self.groupBox_camera_1.setObjectName(u"groupBox_camera_1")
        self.verticalLayout_camera_1 = QVBoxLayout(self.groupBox_camera_1)
        self.verticalLayout_camera_1.setSpacing(5)
        self.verticalLayout_camera_1.setObjectName(u"verticalLayout_camera_1")
        self.horizontalLayout_camera_controls_1 = QHBoxLayout()
        self.horizontalLayout_camera_controls_1.setObjectName(u"horizontalLayout_camera_controls_1")
        self.label_camera_device_1 = QLabel(self.groupBox_camera_1)
        self.label_camera_device_1.setObjectName(u"label_camera_device_1")

        self.horizontalLayout_camera_controls_1.addWidget(self.label_camera_device_1)

        self.comboBox_camera_device_side = QComboBox(self.groupBox_camera_1)
        self.comboBox_camera_device_side.setObjectName(u"comboBox_camera_device_side")

        self.horizontalLayout_camera_controls_1.addWidget(self.comboBox_camera_device_side)

        self.pushButton_connect_side_camera = QPushButton(self.groupBox_camera_1)
        self.pushButton_connect_side_camera.setObjectName(u"pushButton_connect_side_camera")
        self.pushButton_connect_side_camera.setEnabled(True)

        self.horizontalLayout_camera_controls_1.addWidget(self.pushButton_connect_side_camera)

        self.label_camera_status_1 = QLabel(self.groupBox_camera_1)
        self.label_camera_status_1.setObjectName(u"label_camera_status_1")

        self.horizontalLayout_camera_controls_1.addWidget(self.label_camera_status_1)


        self.verticalLayout_camera_1.addLayout(self.horizontalLayout_camera_controls_1)

        self.label_camera_preview_1 = QLabel(self.groupBox_camera_1)
        self.label_camera_preview_1.setObjectName(u"label_camera_preview_1")
        self.label_camera_preview_1.setMinimumSize(QSize(0, 185))
        self.label_camera_preview_1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_camera_1.addWidget(self.label_camera_preview_1)

        self.verticalLayout_camera_1.setStretch(1, 1)

        self.horizontalLayout_camera_cards.addWidget(self.groupBox_camera_1)

        self.groupBox_camera_2 = QGroupBox(self.groupBox_camera_monitor)
        self.groupBox_camera_2.setObjectName(u"groupBox_camera_2")
        self.verticalLayout_camera_2 = QVBoxLayout(self.groupBox_camera_2)
        self.verticalLayout_camera_2.setSpacing(5)
        self.verticalLayout_camera_2.setObjectName(u"verticalLayout_camera_2")
        self.horizontalLayout_camera_controls_2 = QHBoxLayout()
        self.horizontalLayout_camera_controls_2.setObjectName(u"horizontalLayout_camera_controls_2")
        self.label_camera_device_2 = QLabel(self.groupBox_camera_2)
        self.label_camera_device_2.setObjectName(u"label_camera_device_2")

        self.horizontalLayout_camera_controls_2.addWidget(self.label_camera_device_2)

        self.comboBox_camera_device_front = QComboBox(self.groupBox_camera_2)
        self.comboBox_camera_device_front.setObjectName(u"comboBox_camera_device_front")

        self.horizontalLayout_camera_controls_2.addWidget(self.comboBox_camera_device_front)

        self.pushButton_connect__front_camera = QPushButton(self.groupBox_camera_2)
        self.pushButton_connect__front_camera.setObjectName(u"pushButton_connect__front_camera")
        self.pushButton_connect__front_camera.setEnabled(True)

        self.horizontalLayout_camera_controls_2.addWidget(self.pushButton_connect__front_camera)

        self.label_camera_status_2 = QLabel(self.groupBox_camera_2)
        self.label_camera_status_2.setObjectName(u"label_camera_status_2")

        self.horizontalLayout_camera_controls_2.addWidget(self.label_camera_status_2)


        self.verticalLayout_camera_2.addLayout(self.horizontalLayout_camera_controls_2)

        self.label_camera_preview_2 = QLabel(self.groupBox_camera_2)
        self.label_camera_preview_2.setObjectName(u"label_camera_preview_2")
        self.label_camera_preview_2.setMinimumSize(QSize(0, 185))
        self.label_camera_preview_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_camera_2.addWidget(self.label_camera_preview_2)

        self.verticalLayout_camera_2.setStretch(1, 1)

        self.horizontalLayout_camera_cards.addWidget(self.groupBox_camera_2)

        self.groupBox_camera_3 = QGroupBox(self.groupBox_camera_monitor)
        self.groupBox_camera_3.setObjectName(u"groupBox_camera_3")
        self.verticalLayout_camera_3 = QVBoxLayout(self.groupBox_camera_3)
        self.verticalLayout_camera_3.setSpacing(5)
        self.verticalLayout_camera_3.setObjectName(u"verticalLayout_camera_3")
        self.horizontalLayout_camera_controls_3 = QHBoxLayout()
        self.horizontalLayout_camera_controls_3.setObjectName(u"horizontalLayout_camera_controls_3")
        self.label_camera_device_3 = QLabel(self.groupBox_camera_3)
        self.label_camera_device_3.setObjectName(u"label_camera_device_3")

        self.horizontalLayout_camera_controls_3.addWidget(self.label_camera_device_3)

        self.comboBox_camera_device_hand = QComboBox(self.groupBox_camera_3)
        self.comboBox_camera_device_hand.setObjectName(u"comboBox_camera_device_hand")

        self.horizontalLayout_camera_controls_3.addWidget(self.comboBox_camera_device_hand)

        self.pushButton_connect_camera_hand = QPushButton(self.groupBox_camera_3)
        self.pushButton_connect_camera_hand.setObjectName(u"pushButton_connect_camera_hand")
        self.pushButton_connect_camera_hand.setEnabled(True)

        self.horizontalLayout_camera_controls_3.addWidget(self.pushButton_connect_camera_hand)

        self.label_camera_status_3 = QLabel(self.groupBox_camera_3)
        self.label_camera_status_3.setObjectName(u"label_camera_status_3")

        self.horizontalLayout_camera_controls_3.addWidget(self.label_camera_status_3)


        self.verticalLayout_camera_3.addLayout(self.horizontalLayout_camera_controls_3)

        self.label_camera_preview_3 = QLabel(self.groupBox_camera_3)
        self.label_camera_preview_3.setObjectName(u"label_camera_preview_3")
        self.label_camera_preview_3.setMinimumSize(QSize(0, 185))
        self.label_camera_preview_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_camera_3.addWidget(self.label_camera_preview_3)

        self.verticalLayout_camera_3.setStretch(1, 1)

        self.horizontalLayout_camera_cards.addWidget(self.groupBox_camera_3)


        self.verticalLayout_camera_monitor.addLayout(self.horizontalLayout_camera_cards)

        self.verticalLayout_camera_monitor.setStretch(1, 1)

        self.verticalLayout_main.addWidget(self.groupBox_camera_monitor)

        self.groupBox_log = QGroupBox(self.centralwidget)
        self.groupBox_log.setObjectName(u"groupBox_log")
        self.groupBox_log.setMinimumSize(QSize(0, 100))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_log)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_log_toolbar = QHBoxLayout()
        self.horizontalLayout_log_toolbar.setObjectName(u"horizontalLayout_log_toolbar")
        self.spacer_log = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_log_toolbar.addItem(self.spacer_log)

        self.checkBox_log_autoscroll = QCheckBox(self.groupBox_log)
        self.checkBox_log_autoscroll.setObjectName(u"checkBox_log_autoscroll")
        self.checkBox_log_autoscroll.setChecked(True)

        self.horizontalLayout_log_toolbar.addWidget(self.checkBox_log_autoscroll)

        self.pushButton_clear_log = QPushButton(self.groupBox_log)
        self.pushButton_clear_log.setObjectName(u"pushButton_clear_log")

        self.horizontalLayout_log_toolbar.addWidget(self.pushButton_clear_log)


        self.verticalLayout_4.addLayout(self.horizontalLayout_log_toolbar)

        self.plainTextEdit_log = QPlainTextEdit(self.groupBox_log)
        self.plainTextEdit_log.setObjectName(u"plainTextEdit_log")
        font = QFont()
        font.setFamilies([u"Monospace"])
        font.setPointSize(10)
        self.plainTextEdit_log.setFont(font)
        self.plainTextEdit_log.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.plainTextEdit_log.setReadOnly(True)
        self.plainTextEdit_log.setMaximumBlockCount(2000)

        self.verticalLayout_4.addWidget(self.plainTextEdit_log)


        self.verticalLayout_main.addWidget(self.groupBox_log)

        self.verticalLayout_main.setStretch(2, 2)
        self.verticalLayout_main.setStretch(3, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1349, 27))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuSet_Param)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.menuSet_Param.setText(QCoreApplication.translate("MainWindow", u"Set Param", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Master Arm", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"port", None))
        self.pushButton_refresh_master_port.setText(QCoreApplication.translate("MainWindow", u"Refresh Port", None))
        self.label_38.setText(QCoreApplication.translate("MainWindow", u"Hz(ms)", None))
        self.lineEdit_master_read_pos_rate.setText(QCoreApplication.translate("MainWindow", u"20", None))
        self.pushButton_connect_master_arm.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label_master_status.setText(QCoreApplication.translate("MainWindow", u"\u25cf Disconnected", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Slave Arm", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Model", None))
        self.comboBox_robot_type.setItemText(0, QCoreApplication.translate("MainWindow", u"NRC", None))
        self.comboBox_robot_type.setItemText(1, QCoreApplication.translate("MainWindow", u"Dobot_Cr3", None))

        self.label_16.setText(QCoreApplication.translate("MainWindow", u"IP", None))
        self.lineEdit_slave_arm_ip.setText(QCoreApplication.translate("MainWindow", u"192.168.2.14", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"Hz(ms)", None))
        self.lineEdit_slave_read_pos_rate.setText(QCoreApplication.translate("MainWindow", u"20", None))
        self.Btn_robot_connect.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.pushButton_robot_PowerOn.setText(QCoreApplication.translate("MainWindow", u"PowerOn", None))
        self.label_slave_status.setText(QCoreApplication.translate("MainWindow", u"\u25cf Disconnected", None))
        self.groupBox_hand_control.setTitle(QCoreApplication.translate("MainWindow", u"Dexterous Hand Control", None))
        self.pushButton_connect_hand.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"Type", None))
        self.comboBox_hand_comm_type.setItemText(0, QCoreApplication.translate("MainWindow", u"Modebus", None))
        self.comboBox_hand_comm_type.setItemText(1, QCoreApplication.translate("MainWindow", u"Can", None))

        self.label_35.setText(QCoreApplication.translate("MainWindow", u"Comm Type", None))
        self.label_36.setText(QCoreApplication.translate("MainWindow", u"Comm Info", None))
        self.comboBox_hand_type.setItemText(0, QCoreApplication.translate("MainWindow", u"Right Hand", None))
        self.comboBox_hand_type.setItemText(1, QCoreApplication.translate("MainWindow", u"Left Hand", None))

        self.pushButton_refresh_hand_connect_info.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"Model", None))
        self.comboBox_hand_model.setItemText(0, QCoreApplication.translate("MainWindow", u"LinkerO6", None))

        self.label_37.setText(QCoreApplication.translate("MainWindow", u"\u8fd9\u91cc\u6ce8\u610f \u5982\u679c\u662fubuntu\u4e0b\u7528can  \u9700\u8981\u5728\u914d\u7f6e\u6587\u4ef6\u4e2d\u5199\u5165root\u5bc6\u7801", None))
        self.groupBox_follow_control.setTitle(QCoreApplication.translate("MainWindow", u"Follow Control", None))
        self.label_follow_hint.setText(QCoreApplication.translate("MainWindow", u"\u8fde\u63a5\u4e3b\u624b\u3001\u4ece\u624b\u548c\u7075\u5de7\u624b\u540e\u53ef\u542f\u52a8\u8ddf\u968f", None))
        self.pushButton_start_follow.setText(QCoreApplication.translate("MainWindow", u"Start Follow", None))
        self.label_follow_interval.setText(QCoreApplication.translate("MainWindow", u"Interval (ms)", None))
        self.lineEdit_follow_rate.setText(QCoreApplication.translate("MainWindow", u"20", None))
        self.pushButton_slave_home_pos.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.pushButton_start_recod.setText(QCoreApplication.translate("MainWindow", u"StartRecod", None))
        self.pushButton_stop_recod.setText(QCoreApplication.translate("MainWindow", u"StopRecod", None))
        self.pushButton_discard_episode.setText(QCoreApplication.translate("MainWindow", u"Discard episode", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Save path", None))
        self.pushButton_save_episode.setText(QCoreApplication.translate("MainWindow", u"Save episode", None))
        self.pushButton_browse_save_path.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.groupBox_camera_monitor.setTitle(QCoreApplication.translate("MainWindow", u"Camera Monitoring (3 Live Feeds)", None))
        self.label_camera_monitor_hint.setText(QCoreApplication.translate("MainWindow", u"Device Connections and Preview", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Model", None))
        self.comboBox_camera_model.setItemText(0, QCoreApplication.translate("MainWindow", u"RealSenseD435", None))

        self.label_camera_frame_interval.setText(QCoreApplication.translate("MainWindow", u"Interval (ms)", None))
        self.lineEdit_camera_frame_interval.setText(QCoreApplication.translate("MainWindow", u"20", None))
        self.pushButton_camera_refresh.setText(QCoreApplication.translate("MainWindow", u"Refresh Devices List", None))
        self.pushButton_camera_connect_all.setText(QCoreApplication.translate("MainWindow", u"Connect All", None))
        self.pushButton_camera_disconnect_all.setText(QCoreApplication.translate("MainWindow", u"Disconnect All", None))
        self.groupBox_camera_1.setTitle(QCoreApplication.translate("MainWindow", u"Camera 1 (Side View)", None))
        self.label_camera_device_1.setText(QCoreApplication.translate("MainWindow", u"Device", None))
        self.pushButton_connect_side_camera.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label_camera_status_1.setText(QCoreApplication.translate("MainWindow", u"\u25cf Disconnected", None))
        self.label_camera_preview_1.setText("")
        self.groupBox_camera_2.setTitle(QCoreApplication.translate("MainWindow", u"Camera 2 (Front View)", None))
        self.label_camera_device_2.setText(QCoreApplication.translate("MainWindow", u"Device", None))
        self.pushButton_connect__front_camera.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label_camera_status_2.setText(QCoreApplication.translate("MainWindow", u"\u25cf Disconnected", None))
        self.label_camera_preview_2.setText("")
        self.groupBox_camera_3.setTitle(QCoreApplication.translate("MainWindow", u"Camera 3 (Hand)", None))
        self.label_camera_device_3.setText(QCoreApplication.translate("MainWindow", u"Device", None))
        self.pushButton_connect_camera_hand.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label_camera_status_3.setText(QCoreApplication.translate("MainWindow", u"\u25cf Disconnected", None))
        self.label_camera_preview_3.setText("")
        self.groupBox_log.setTitle(QCoreApplication.translate("MainWindow", u"Activity Log", None))
        self.checkBox_log_autoscroll.setText(QCoreApplication.translate("MainWindow", u"Auto Scroll", None))
        self.pushButton_clear_log.setText(QCoreApplication.translate("MainWindow", u"Clear Log", None))
        self.plainTextEdit_log.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Activity logs will appear here...", None))
    # retranslateUi

