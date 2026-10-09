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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1028, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 460, 781, 91))
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 180, 461, 244))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_master_read_pos_rate = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_read_pos_rate.setObjectName(u"lineEdit_master_read_pos_rate")

        self.gridLayout.addWidget(self.lineEdit_master_read_pos_rate, 0, 1, 1, 1)

        self.label_7 = QLabel(self.gridLayoutWidget)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)

        self.label_14 = QLabel(self.gridLayoutWidget)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout.addWidget(self.label_14, 5, 2, 1, 1)

        self.lineEdit_master_joint4 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_joint4.setObjectName(u"lineEdit_master_joint4")

        self.gridLayout.addWidget(self.lineEdit_master_joint4, 5, 1, 1, 1)

        self.label_9 = QLabel(self.gridLayoutWidget)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 7, 0, 1, 1)

        self.lineEdit_master_joint0 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_joint0.setObjectName(u"lineEdit_master_joint0")

        self.gridLayout.addWidget(self.lineEdit_master_joint0, 1, 1, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_6 = QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)

        self.lineEdit_master_joint2 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_joint2.setObjectName(u"lineEdit_master_joint2")

        self.gridLayout.addWidget(self.lineEdit_master_joint2, 3, 1, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.label_15 = QLabel(self.gridLayoutWidget)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout.addWidget(self.label_15, 6, 2, 1, 1)

        self.lineEdit_master_joint1 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_joint1.setObjectName(u"lineEdit_master_joint1")

        self.gridLayout.addWidget(self.lineEdit_master_joint1, 2, 1, 1, 1)

        self.label_10 = QLabel(self.gridLayoutWidget)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 1, 2, 1, 1)

        self.lineEdit_master_joint6 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_joint6.setObjectName(u"lineEdit_master_joint6")

        self.gridLayout.addWidget(self.lineEdit_master_joint6, 7, 1, 1, 1)

        self.lineEdit_master_joint5 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_joint5.setObjectName(u"lineEdit_master_joint5")

        self.gridLayout.addWidget(self.lineEdit_master_joint5, 6, 1, 1, 1)

        self.label_11 = QLabel(self.gridLayoutWidget)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout.addWidget(self.label_11, 2, 2, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.label_12 = QLabel(self.gridLayoutWidget)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout.addWidget(self.label_12, 3, 2, 1, 1)

        self.lineEdit_master_joint3 = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_joint3.setObjectName(u"lineEdit_master_joint3")

        self.gridLayout.addWidget(self.lineEdit_master_joint3, 4, 1, 1, 1)

        self.label_13 = QLabel(self.gridLayoutWidget)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout.addWidget(self.label_13, 4, 2, 1, 1)

        self.label_8 = QLabel(self.gridLayoutWidget)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 0, 0, 1, 1)

        self.lineEdit_master_x = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_x.setObjectName(u"lineEdit_master_x")

        self.gridLayout.addWidget(self.lineEdit_master_x, 1, 3, 1, 1)

        self.lineEdit_master_y = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_y.setObjectName(u"lineEdit_master_y")

        self.gridLayout.addWidget(self.lineEdit_master_y, 2, 3, 1, 1)

        self.lineEdit_master_z = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_z.setObjectName(u"lineEdit_master_z")

        self.gridLayout.addWidget(self.lineEdit_master_z, 3, 3, 1, 1)

        self.lineEdit_master_a = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_a.setObjectName(u"lineEdit_master_a")

        self.gridLayout.addWidget(self.lineEdit_master_a, 4, 3, 1, 1)

        self.lineEdit_master_b = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_b.setObjectName(u"lineEdit_master_b")

        self.gridLayout.addWidget(self.lineEdit_master_b, 5, 3, 1, 1)

        self.lineEdit_master_c = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_master_c.setObjectName(u"lineEdit_master_c")

        self.gridLayout.addWidget(self.lineEdit_master_c, 6, 3, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)
        self.gridLayout.setColumnStretch(2, 1)
        self.gridLayout.setColumnStretch(3, 2)
        self.pushButton_openServoj = QPushButton(self.centralwidget)
        self.pushButton_openServoj.setObjectName(u"pushButton_openServoj")
        self.pushButton_openServoj.setGeometry(QRect(490, 20, 111, 21))
        self.pushButton_Start = QPushButton(self.centralwidget)
        self.pushButton_Start.setObjectName(u"pushButton_Start")
        self.pushButton_Start.setGeometry(QRect(490, 50, 95, 25))
        self.pushButton_closeServoj = QPushButton(self.centralwidget)
        self.pushButton_closeServoj.setObjectName(u"pushButton_closeServoj")
        self.pushButton_closeServoj.setGeometry(QRect(490, 90, 95, 25))
        self.pushButton_test = QPushButton(self.centralwidget)
        self.pushButton_test.setObjectName(u"pushButton_test")
        self.pushButton_test.setGeometry(QRect(760, 70, 95, 25))
        self.gridLayoutWidget_2 = QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(30, 10, 421, 81))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_slave_ar_ip = QLineEdit(self.gridLayoutWidget_2)
        self.lineEdit_slave_ar_ip.setObjectName(u"lineEdit_slave_ar_ip")

        self.gridLayout_2.addWidget(self.lineEdit_slave_ar_ip, 0, 1, 1, 1)

        self.Btn_robot_connect = QPushButton(self.gridLayoutWidget_2)
        self.Btn_robot_connect.setObjectName(u"Btn_robot_connect")

        self.gridLayout_2.addWidget(self.Btn_robot_connect, 0, 2, 1, 1)

        self.label_16 = QLabel(self.gridLayoutWidget_2)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_2.addWidget(self.label_16, 0, 0, 1, 1)

        self.pushButton_robot_PowerOn = QPushButton(self.gridLayoutWidget_2)
        self.pushButton_robot_PowerOn.setObjectName(u"pushButton_robot_PowerOn")

        self.gridLayout_2.addWidget(self.pushButton_robot_PowerOn, 0, 3, 1, 1)

        self.gridLayoutWidget_3 = QWidget(self.centralwidget)
        self.gridLayoutWidget_3.setObjectName(u"gridLayoutWidget_3")
        self.gridLayoutWidget_3.setGeometry(QRect(500, 180, 461, 244))
        self.gridLayout_3 = QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_slave_read_pos_rate = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_read_pos_rate.setObjectName(u"lineEdit_slave_read_pos_rate")

        self.gridLayout_3.addWidget(self.lineEdit_slave_read_pos_rate, 0, 1, 1, 1)

        self.lineEdit_slave_y = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_y.setObjectName(u"lineEdit_slave_y")

        self.gridLayout_3.addWidget(self.lineEdit_slave_y, 2, 3, 1, 1)

        self.label_24 = QLabel(self.gridLayoutWidget_3)
        self.label_24.setObjectName(u"label_24")

        self.gridLayout_3.addWidget(self.label_24, 6, 2, 1, 1)

        self.label_25 = QLabel(self.gridLayoutWidget_3)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout_3.addWidget(self.label_25, 1, 2, 1, 1)

        self.label_27 = QLabel(self.gridLayoutWidget_3)
        self.label_27.setObjectName(u"label_27")

        self.gridLayout_3.addWidget(self.label_27, 2, 0, 1, 1)

        self.label_26 = QLabel(self.gridLayoutWidget_3)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout_3.addWidget(self.label_26, 2, 2, 1, 1)

        self.label_30 = QLabel(self.gridLayoutWidget_3)
        self.label_30.setObjectName(u"label_30")

        self.gridLayout_3.addWidget(self.label_30, 0, 0, 1, 1)

        self.lineEdit_slave_joint0 = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_joint0.setObjectName(u"lineEdit_slave_joint0")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint0, 1, 1, 1, 1)

        self.lineEdit_slave_joint1 = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_joint1.setObjectName(u"lineEdit_slave_joint1")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint1, 2, 1, 1, 1)

        self.lineEdit_slave_x = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_x.setObjectName(u"lineEdit_slave_x")

        self.gridLayout_3.addWidget(self.lineEdit_slave_x, 1, 3, 1, 1)

        self.lineEdit_slave_joint4 = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_joint4.setObjectName(u"lineEdit_slave_joint4")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint4, 5, 1, 1, 1)

        self.label_29 = QLabel(self.gridLayoutWidget_3)
        self.label_29.setObjectName(u"label_29")

        self.gridLayout_3.addWidget(self.label_29, 4, 2, 1, 1)

        self.label_17 = QLabel(self.gridLayoutWidget_3)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_3.addWidget(self.label_17, 6, 0, 1, 1)

        self.lineEdit_slave_c = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_c.setObjectName(u"lineEdit_slave_c")

        self.gridLayout_3.addWidget(self.lineEdit_slave_c, 6, 3, 1, 1)

        self.label_22 = QLabel(self.gridLayoutWidget_3)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_3.addWidget(self.label_22, 5, 0, 1, 1)

        self.label_23 = QLabel(self.gridLayoutWidget_3)
        self.label_23.setObjectName(u"label_23")

        self.gridLayout_3.addWidget(self.label_23, 4, 0, 1, 1)

        self.lineEdit_slave_joint5 = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_joint5.setObjectName(u"lineEdit_slave_joint5")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint5, 6, 1, 1, 1)

        self.lineEdit_slave_a = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_a.setObjectName(u"lineEdit_slave_a")

        self.gridLayout_3.addWidget(self.lineEdit_slave_a, 4, 3, 1, 1)

        self.label_20 = QLabel(self.gridLayoutWidget_3)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_3.addWidget(self.label_20, 3, 0, 1, 1)

        self.label_18 = QLabel(self.gridLayoutWidget_3)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_3.addWidget(self.label_18, 5, 2, 1, 1)

        self.label_21 = QLabel(self.gridLayoutWidget_3)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_3.addWidget(self.label_21, 1, 0, 1, 1)

        self.lineEdit_slave_joint2 = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_joint2.setObjectName(u"lineEdit_slave_joint2")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint2, 3, 1, 1, 1)

        self.lineEdit_slave_joint3 = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_joint3.setObjectName(u"lineEdit_slave_joint3")

        self.gridLayout_3.addWidget(self.lineEdit_slave_joint3, 4, 1, 1, 1)

        self.lineEdit_slave_b = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_b.setObjectName(u"lineEdit_slave_b")

        self.gridLayout_3.addWidget(self.lineEdit_slave_b, 5, 3, 1, 1)

        self.lineEdit_slave_z = QLineEdit(self.gridLayoutWidget_3)
        self.lineEdit_slave_z.setObjectName(u"lineEdit_slave_z")

        self.gridLayout_3.addWidget(self.lineEdit_slave_z, 3, 3, 1, 1)

        self.label_28 = QLabel(self.gridLayoutWidget_3)
        self.label_28.setObjectName(u"label_28")

        self.gridLayout_3.addWidget(self.label_28, 3, 2, 1, 1)

        self.gridLayout_3.setColumnStretch(0, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1028, 27))
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
        self.lineEdit_master_read_pos_rate.setText(QCoreApplication.translate("MainWindow", u"50", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"joint5(\u00b0)", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"b(rad)", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"joint6(\u00b0)", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"joint2(\u00b0)", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"joint0(\u00b0)", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"joint4(\u00b0)", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"joint3(\u00b0)", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"c(rad)", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"x(mm)", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"y(mm)", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"joint1(\u00b0)", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"z(mm)", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"a(rad)", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"refresh rate(ms)", None))
        self.pushButton_openServoj.setText(QCoreApplication.translate("MainWindow", u"OpenServoJ", None))
        self.pushButton_Start.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.pushButton_closeServoj.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.pushButton_test.setText(QCoreApplication.translate("MainWindow", u"test", None))
        self.Btn_robot_connect.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"IP", None))
        self.pushButton_robot_PowerOn.setText(QCoreApplication.translate("MainWindow", u"PowerOn", None))
        self.lineEdit_slave_read_pos_rate.setText(QCoreApplication.translate("MainWindow", u"50", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"c(rad)", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"x(mm)", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"joint1(\u00b0)", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"y(mm)", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"refresh rate(ms)", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"a(rad)", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"joint5(\u00b0)", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"joint4(\u00b0)", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"joint3(\u00b0)", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"joint2(\u00b0)", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"b(rad)", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"joint0(\u00b0)", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"z(mm)", None))
    # retranslateUi

