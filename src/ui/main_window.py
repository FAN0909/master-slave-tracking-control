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
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1054, 769)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 530, 781, 91))
        self.pushButton_start_follow = QPushButton(self.centralwidget)
        self.pushButton_start_follow.setObjectName(u"pushButton_start_follow")
        self.pushButton_start_follow.setGeometry(QRect(10, 390, 95, 25))
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 10, 1051, 361))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox_2 = QGroupBox(self.layoutWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_31 = QLabel(self.groupBox_2)
        self.label_31.setObjectName(u"label_31")

        self.gridLayout_4.addWidget(self.label_31, 0, 0, 1, 1)

        self.comboBox_master_port = QComboBox(self.groupBox_2)
        self.comboBox_master_port.setObjectName(u"comboBox_master_port")

        self.gridLayout_4.addWidget(self.comboBox_master_port, 0, 1, 1, 1)

        self.pushButton_connect_master_arm = QPushButton(self.groupBox_2)
        self.pushButton_connect_master_arm.setObjectName(u"pushButton_connect_master_arm")

        self.gridLayout_4.addWidget(self.pushButton_connect_master_arm, 0, 3, 1, 1)

        self.pushButton_refresh_master_port = QPushButton(self.groupBox_2)
        self.pushButton_refresh_master_port.setObjectName(u"pushButton_refresh_master_port")

        self.gridLayout_4.addWidget(self.pushButton_refresh_master_port, 0, 2, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_4)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineEdit_master_y = QLineEdit(self.groupBox_2)
        self.lineEdit_master_y.setObjectName(u"lineEdit_master_y")

        self.gridLayout.addWidget(self.lineEdit_master_y, 2, 3, 1, 1)

        self.lineEdit_master_joint2 = QLineEdit(self.groupBox_2)
        self.lineEdit_master_joint2.setObjectName(u"lineEdit_master_joint2")

        self.gridLayout.addWidget(self.lineEdit_master_joint2, 3, 1, 1, 1)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)

        self.lineEdit_master_joint1 = QLineEdit(self.groupBox_2)
        self.lineEdit_master_joint1.setObjectName(u"lineEdit_master_joint1")

        self.gridLayout.addWidget(self.lineEdit_master_joint1, 2, 1, 1, 1)

        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.lineEdit_master_a = QLineEdit(self.groupBox_2)
        self.lineEdit_master_a.setObjectName(u"lineEdit_master_a")

        self.gridLayout.addWidget(self.lineEdit_master_a, 4, 3, 1, 1)

        self.label_12 = QLabel(self.groupBox_2)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout.addWidget(self.label_12, 3, 2, 1, 1)

        self.lineEdit_master_b = QLineEdit(self.groupBox_2)
        self.lineEdit_master_b.setObjectName(u"lineEdit_master_b")

        self.gridLayout.addWidget(self.lineEdit_master_b, 5, 3, 1, 1)

        self.label_15 = QLabel(self.groupBox_2)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout.addWidget(self.label_15, 6, 2, 1, 1)

        self.label_11 = QLabel(self.groupBox_2)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout.addWidget(self.label_11, 2, 2, 1, 1)

        self.lineEdit_master_z = QLineEdit(self.groupBox_2)
        self.lineEdit_master_z.setObjectName(u"lineEdit_master_z")

        self.gridLayout.addWidget(self.lineEdit_master_z, 3, 3, 1, 1)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 1, 2, 1, 1)

        self.lineEdit_master_read_pos_rate = QLineEdit(self.groupBox_2)
        self.lineEdit_master_read_pos_rate.setObjectName(u"lineEdit_master_read_pos_rate")

        self.gridLayout.addWidget(self.lineEdit_master_read_pos_rate, 0, 1, 1, 1)

        self.label_14 = QLabel(self.groupBox_2)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout.addWidget(self.label_14, 5, 2, 1, 1)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.lineEdit_master_joint0 = QLineEdit(self.groupBox_2)
        self.lineEdit_master_joint0.setObjectName(u"lineEdit_master_joint0")

        self.gridLayout.addWidget(self.lineEdit_master_joint0, 1, 1, 1, 1)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.lineEdit_master_joint5 = QLineEdit(self.groupBox_2)
        self.lineEdit_master_joint5.setObjectName(u"lineEdit_master_joint5")

        self.gridLayout.addWidget(self.lineEdit_master_joint5, 6, 1, 1, 1)

        self.lineEdit_master_c = QLineEdit(self.groupBox_2)
        self.lineEdit_master_c.setObjectName(u"lineEdit_master_c")

        self.gridLayout.addWidget(self.lineEdit_master_c, 6, 3, 1, 1)

        self.lineEdit_master_joint4 = QLineEdit(self.groupBox_2)
        self.lineEdit_master_joint4.setObjectName(u"lineEdit_master_joint4")

        self.gridLayout.addWidget(self.lineEdit_master_joint4, 5, 1, 1, 1)

        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout.addWidget(self.label_13, 4, 2, 1, 1)

        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 0, 0, 1, 1)

        self.lineEdit_master_x = QLineEdit(self.groupBox_2)
        self.lineEdit_master_x.setObjectName(u"lineEdit_master_x")

        self.gridLayout.addWidget(self.lineEdit_master_x, 1, 3, 1, 1)

        self.lineEdit_master_joint3 = QLineEdit(self.groupBox_2)
        self.lineEdit_master_joint3.setObjectName(u"lineEdit_master_joint3")

        self.gridLayout.addWidget(self.lineEdit_master_joint3, 4, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 7, 0, 1, 1)

        self.lineEdit_master_joint6 = QLineEdit(self.groupBox_2)
        self.lineEdit_master_joint6.setObjectName(u"lineEdit_master_joint6")

        self.gridLayout.addWidget(self.lineEdit_master_joint6, 7, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)

        self.verticalLayout_3.addLayout(self.gridLayout)


        self.verticalLayout_4.addLayout(self.verticalLayout_3)


        self.horizontalLayout.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.layoutWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_16 = QLabel(self.groupBox)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_2.addWidget(self.label_16, 0, 0, 1, 1)

        self.pushButton_openServoj = QPushButton(self.groupBox)
        self.pushButton_openServoj.setObjectName(u"pushButton_openServoj")

        self.gridLayout_2.addWidget(self.pushButton_openServoj, 0, 4, 1, 1)

        self.pushButton_robot_PowerOn = QPushButton(self.groupBox)
        self.pushButton_robot_PowerOn.setObjectName(u"pushButton_robot_PowerOn")

        self.gridLayout_2.addWidget(self.pushButton_robot_PowerOn, 0, 3, 1, 1)

        self.Btn_robot_connect = QPushButton(self.groupBox)
        self.Btn_robot_connect.setObjectName(u"Btn_robot_connect")

        self.gridLayout_2.addWidget(self.Btn_robot_connect, 0, 2, 1, 1)

        self.pushButton_Start = QPushButton(self.groupBox)
        self.pushButton_Start.setObjectName(u"pushButton_Start")

        self.gridLayout_2.addWidget(self.pushButton_Start, 0, 5, 1, 1)

        self.lineEdit_slave_arm_ip = QLineEdit(self.groupBox)
        self.lineEdit_slave_arm_ip.setObjectName(u"lineEdit_slave_arm_ip")

        self.gridLayout_2.addWidget(self.lineEdit_slave_arm_ip, 0, 1, 1, 1)

        self.pushButton_closeServoj = QPushButton(self.groupBox)
        self.pushButton_closeServoj.setObjectName(u"pushButton_closeServoj")

        self.gridLayout_2.addWidget(self.pushButton_closeServoj, 0, 6, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.lineEdit_slave_read_pos_rate = QLineEdit(self.groupBox)
        self.lineEdit_slave_read_pos_rate.setObjectName(u"lineEdit_slave_read_pos_rate")

        self.gridLayout_3.addWidget(self.lineEdit_slave_read_pos_rate, 0, 1, 1, 1)

        self.lineEdit_slave_y = QLineEdit(self.groupBox)
        self.lineEdit_slave_y.setObjectName(u"lineEdit_slave_y")

        self.gridLayout_3.addWidget(self.lineEdit_slave_y, 2, 3, 1, 1)

        self.label_24 = QLabel(self.groupBox)
        self.label_24.setObjectName(u"label_24")

        self.gridLayout_3.addWidget(self.label_24, 6, 2, 1, 1)

        self.label_25 = QLabel(self.groupBox)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout_3.addWidget(self.label_25, 1, 2, 1, 1)

        self.label_27 = QLabel(self.groupBox)
        self.label_27.setObjectName(u"label_27")

        self.gridLayout_3.addWidget(self.label_27, 2, 0, 1, 1)

        self.label_26 = QLabel(self.groupBox)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout_3.addWidget(self.label_26, 2, 2, 1, 1)

        self.label_30 = QLabel(self.groupBox)
        self.label_30.setObjectName(u"label_30")

        self.gridLayout_3.addWidget(self.label_30, 0, 0, 1, 1)

        self.lineEdit_slave_joint0 = QLineEdit(self.groupBox)
        self.lineEdit_slave_joint0.setObjectName(u"lineEdit_slave_joint0")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint0, 1, 1, 1, 1)

        self.lineEdit_slave_joint1 = QLineEdit(self.groupBox)
        self.lineEdit_slave_joint1.setObjectName(u"lineEdit_slave_joint1")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint1, 2, 1, 1, 1)

        self.lineEdit_slave_x = QLineEdit(self.groupBox)
        self.lineEdit_slave_x.setObjectName(u"lineEdit_slave_x")

        self.gridLayout_3.addWidget(self.lineEdit_slave_x, 1, 3, 1, 1)

        self.lineEdit_slave_joint4 = QLineEdit(self.groupBox)
        self.lineEdit_slave_joint4.setObjectName(u"lineEdit_slave_joint4")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint4, 5, 1, 1, 1)

        self.label_29 = QLabel(self.groupBox)
        self.label_29.setObjectName(u"label_29")

        self.gridLayout_3.addWidget(self.label_29, 4, 2, 1, 1)

        self.label_17 = QLabel(self.groupBox)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_3.addWidget(self.label_17, 6, 0, 1, 1)

        self.lineEdit_slave_c = QLineEdit(self.groupBox)
        self.lineEdit_slave_c.setObjectName(u"lineEdit_slave_c")

        self.gridLayout_3.addWidget(self.lineEdit_slave_c, 6, 3, 1, 1)

        self.label_22 = QLabel(self.groupBox)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_3.addWidget(self.label_22, 5, 0, 1, 1)

        self.label_23 = QLabel(self.groupBox)
        self.label_23.setObjectName(u"label_23")

        self.gridLayout_3.addWidget(self.label_23, 4, 0, 1, 1)

        self.lineEdit_slave_joint5 = QLineEdit(self.groupBox)
        self.lineEdit_slave_joint5.setObjectName(u"lineEdit_slave_joint5")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint5, 6, 1, 1, 1)

        self.lineEdit_slave_a = QLineEdit(self.groupBox)
        self.lineEdit_slave_a.setObjectName(u"lineEdit_slave_a")

        self.gridLayout_3.addWidget(self.lineEdit_slave_a, 4, 3, 1, 1)

        self.label_20 = QLabel(self.groupBox)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_3.addWidget(self.label_20, 3, 0, 1, 1)

        self.label_18 = QLabel(self.groupBox)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_3.addWidget(self.label_18, 5, 2, 1, 1)

        self.label_21 = QLabel(self.groupBox)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_3.addWidget(self.label_21, 1, 0, 1, 1)

        self.lineEdit_slave_joint2 = QLineEdit(self.groupBox)
        self.lineEdit_slave_joint2.setObjectName(u"lineEdit_slave_joint2")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint2, 3, 1, 1, 1)

        self.lineEdit_slave_joint3 = QLineEdit(self.groupBox)
        self.lineEdit_slave_joint3.setObjectName(u"lineEdit_slave_joint3")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint3, 4, 1, 1, 1)

        self.lineEdit_slave_b = QLineEdit(self.groupBox)
        self.lineEdit_slave_b.setObjectName(u"lineEdit_slave_b")

        self.gridLayout_3.addWidget(self.lineEdit_slave_b, 5, 3, 1, 1)

        self.lineEdit_slave_z = QLineEdit(self.groupBox)
        self.lineEdit_slave_z.setObjectName(u"lineEdit_slave_z")

        self.gridLayout_3.addWidget(self.lineEdit_slave_z, 3, 3, 1, 1)

        self.label_28 = QLabel(self.groupBox)
        self.label_28.setObjectName(u"label_28")

        self.gridLayout_3.addWidget(self.label_28, 3, 2, 1, 1)

        self.label_19 = QLabel(self.groupBox)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_3.addWidget(self.label_19, 7, 0, 1, 1)

        self.lineEdit_slave_joint6 = QLineEdit(self.groupBox)
        self.lineEdit_slave_joint6.setObjectName(u"lineEdit_slave_joint6")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint6, 7, 1, 1, 1)

        self.gridLayout_3.setColumnStretch(0, 1)

        self.verticalLayout.addLayout(self.gridLayout_3)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.horizontalLayout.addWidget(self.groupBox)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.lineEdit_follow_rate = QLineEdit(self.centralwidget)
        self.lineEdit_follow_rate.setObjectName(u"lineEdit_follow_rate")
        self.lineEdit_follow_rate.setGeometry(QRect(140, 400, 113, 25))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1054, 27))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"hello pysid6", None))
        self.pushButton_start_follow.setText(QCoreApplication.translate("MainWindow", u"Start follow", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Master Arm", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"port", None))
        self.pushButton_connect_master_arm.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.pushButton_refresh_master_port.setText(QCoreApplication.translate("MainWindow", u"Refresh Port", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"joint5(\u00b0)", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"joint4(\u00b0)", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"joint0(\u00b0)", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"z(mm)", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"c(rad)", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"y(mm)", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"x(mm)", None))
        self.lineEdit_master_read_pos_rate.setText(QCoreApplication.translate("MainWindow", u"50", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"b(rad)", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"joint3(\u00b0)", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"joint2(\u00b0)", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"a(rad)", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Hz(ms)", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"joint1(\u00b0)", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"joint6(\u00b0)", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Slave Arm", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"IP", None))
        self.pushButton_openServoj.setText(QCoreApplication.translate("MainWindow", u"OpenServoJ", None))
        self.pushButton_robot_PowerOn.setText(QCoreApplication.translate("MainWindow", u"PowerOn", None))
        self.Btn_robot_connect.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.pushButton_Start.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.lineEdit_slave_arm_ip.setText(QCoreApplication.translate("MainWindow", u"192.168.2.14", None))
        self.pushButton_closeServoj.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.lineEdit_slave_read_pos_rate.setText(QCoreApplication.translate("MainWindow", u"50", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"c(rad)", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"x(mm)", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"joint1(\u00b0)", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"y(mm)", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"Hz(ms)", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"a(rad)", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"joint5(\u00b0)", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"joint4(\u00b0)", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"joint3(\u00b0)", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"joint2(\u00b0)", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"b(rad)", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"joint0(\u00b0)", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"z(mm)", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"joint6(\u00b0)", None))
        self.lineEdit_follow_rate.setText(QCoreApplication.translate("MainWindow", u"50", None))
    # retranslateUi

