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
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.Btn_robot_connect = QPushButton(self.centralwidget)
        self.Btn_robot_connect.setObjectName(u"Btn_robot_connect")
        self.Btn_robot_connect.setGeometry(QRect(20, 10, 95, 25))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 460, 781, 91))
        self.pushButton_robot_PowerOn = QPushButton(self.centralwidget)
        self.pushButton_robot_PowerOn.setObjectName(u"pushButton_robot_PowerOn")
        self.pushButton_robot_PowerOn.setGeometry(QRect(130, 10, 95, 25))
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 60, 461, 244))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_read_pos_rate = QLineEdit(self.gridLayoutWidget)
        self.lineEdit_read_pos_rate.setObjectName(u"lineEdit_read_pos_rate")

        self.gridLayout.addWidget(self.lineEdit_read_pos_rate, 0, 1, 1, 1)

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
        self.pushButton_openServoj.setGeometry(QRect(560, 30, 111, 21))
        self.pushButton_Start = QPushButton(self.centralwidget)
        self.pushButton_Start.setObjectName(u"pushButton_Start")
        self.pushButton_Start.setGeometry(QRect(550, 90, 95, 25))
        self.pushButton_closeServoj = QPushButton(self.centralwidget)
        self.pushButton_closeServoj.setObjectName(u"pushButton_closeServoj")
        self.pushButton_closeServoj.setGeometry(QRect(690, 60, 95, 25))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 27))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Btn_robot_connect.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"hello pysid6", None))
        self.pushButton_robot_PowerOn.setText(QCoreApplication.translate("MainWindow", u"PowerOn", None))
        self.lineEdit_read_pos_rate.setText(QCoreApplication.translate("MainWindow", u"50", None))
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
    # retranslateUi

