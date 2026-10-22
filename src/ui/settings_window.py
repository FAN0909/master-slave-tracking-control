# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_window.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QTabWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(1063, 612)
        SettingsDialog.setMinimumSize(QSize(800, 535))
        self.verticalLayout = QVBoxLayout(SettingsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget_settings = QTabWidget(SettingsDialog)
        self.tabWidget_settings.setObjectName(u"tabWidget_settings")
        self.tab_robotset = QWidget()
        self.tab_robotset.setObjectName(u"tab_robotset")
        self.horizontalLayout_robotset = QHBoxLayout(self.tab_robotset)
        self.horizontalLayout_robotset.setObjectName(u"horizontalLayout_robotset")
        self.groupBox = QGroupBox(self.tab_robotset)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_6 = QVBoxLayout(self.groupBox)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBox_6 = QGroupBox(self.groupBox)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.gridLayout_master_telemetry = QGridLayout()
        self.gridLayout_master_telemetry.setObjectName(u"gridLayout_master_telemetry")
        self.label_master_joint_header = QLabel(self.groupBox_6)
        self.label_master_joint_header.setObjectName(u"label_master_joint_header")

        self.gridLayout_master_telemetry.addWidget(self.label_master_joint_header, 0, 0, 1, 1)

        self.label_master_tcp_header = QLabel(self.groupBox_6)
        self.label_master_tcp_header.setObjectName(u"label_master_tcp_header")

        self.gridLayout_master_telemetry.addWidget(self.label_master_tcp_header, 0, 2, 1, 1)

        self.label_master_joint0 = QLabel(self.groupBox_6)
        self.label_master_joint0.setObjectName(u"label_master_joint0")

        self.gridLayout_master_telemetry.addWidget(self.label_master_joint0, 1, 0, 1, 1)

        self.lineEdit_master_joint0 = QLineEdit(self.groupBox_6)
        self.lineEdit_master_joint0.setObjectName(u"lineEdit_master_joint0")
        self.lineEdit_master_joint0.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_joint0, 1, 1, 1, 1)

        self.label_master_joint1 = QLabel(self.groupBox_6)
        self.label_master_joint1.setObjectName(u"label_master_joint1")

        self.gridLayout_master_telemetry.addWidget(self.label_master_joint1, 2, 0, 1, 1)

        self.lineEdit_master_joint1 = QLineEdit(self.groupBox_6)
        self.lineEdit_master_joint1.setObjectName(u"lineEdit_master_joint1")
        self.lineEdit_master_joint1.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_joint1, 2, 1, 1, 1)

        self.label_master_joint2 = QLabel(self.groupBox_6)
        self.label_master_joint2.setObjectName(u"label_master_joint2")

        self.gridLayout_master_telemetry.addWidget(self.label_master_joint2, 3, 0, 1, 1)

        self.lineEdit_master_joint2 = QLineEdit(self.groupBox_6)
        self.lineEdit_master_joint2.setObjectName(u"lineEdit_master_joint2")
        self.lineEdit_master_joint2.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_joint2, 3, 1, 1, 1)

        self.label_master_joint3 = QLabel(self.groupBox_6)
        self.label_master_joint3.setObjectName(u"label_master_joint3")

        self.gridLayout_master_telemetry.addWidget(self.label_master_joint3, 4, 0, 1, 1)

        self.lineEdit_master_joint3 = QLineEdit(self.groupBox_6)
        self.lineEdit_master_joint3.setObjectName(u"lineEdit_master_joint3")
        self.lineEdit_master_joint3.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_joint3, 4, 1, 1, 1)

        self.label_master_joint4 = QLabel(self.groupBox_6)
        self.label_master_joint4.setObjectName(u"label_master_joint4")

        self.gridLayout_master_telemetry.addWidget(self.label_master_joint4, 5, 0, 1, 1)

        self.lineEdit_master_joint4 = QLineEdit(self.groupBox_6)
        self.lineEdit_master_joint4.setObjectName(u"lineEdit_master_joint4")
        self.lineEdit_master_joint4.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_joint4, 5, 1, 1, 1)

        self.label_master_joint5 = QLabel(self.groupBox_6)
        self.label_master_joint5.setObjectName(u"label_master_joint5")

        self.gridLayout_master_telemetry.addWidget(self.label_master_joint5, 6, 0, 1, 1)

        self.lineEdit_master_joint5 = QLineEdit(self.groupBox_6)
        self.lineEdit_master_joint5.setObjectName(u"lineEdit_master_joint5")
        self.lineEdit_master_joint5.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_joint5, 6, 1, 1, 1)

        self.label_master_joint6 = QLabel(self.groupBox_6)
        self.label_master_joint6.setObjectName(u"label_master_joint6")

        self.gridLayout_master_telemetry.addWidget(self.label_master_joint6, 7, 0, 1, 1)

        self.lineEdit_master_joint6 = QLineEdit(self.groupBox_6)
        self.lineEdit_master_joint6.setObjectName(u"lineEdit_master_joint6")
        self.lineEdit_master_joint6.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_joint6, 7, 1, 1, 1)

        self.label_master_x = QLabel(self.groupBox_6)
        self.label_master_x.setObjectName(u"label_master_x")

        self.gridLayout_master_telemetry.addWidget(self.label_master_x, 1, 2, 1, 1)

        self.lineEdit_master_x = QLineEdit(self.groupBox_6)
        self.lineEdit_master_x.setObjectName(u"lineEdit_master_x")
        self.lineEdit_master_x.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_x, 1, 3, 1, 1)

        self.label_master_y = QLabel(self.groupBox_6)
        self.label_master_y.setObjectName(u"label_master_y")

        self.gridLayout_master_telemetry.addWidget(self.label_master_y, 2, 2, 1, 1)

        self.lineEdit_master_y = QLineEdit(self.groupBox_6)
        self.lineEdit_master_y.setObjectName(u"lineEdit_master_y")
        self.lineEdit_master_y.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_y, 2, 3, 1, 1)

        self.label_master_z = QLabel(self.groupBox_6)
        self.label_master_z.setObjectName(u"label_master_z")

        self.gridLayout_master_telemetry.addWidget(self.label_master_z, 3, 2, 1, 1)

        self.lineEdit_master_z = QLineEdit(self.groupBox_6)
        self.lineEdit_master_z.setObjectName(u"lineEdit_master_z")
        self.lineEdit_master_z.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_z, 3, 3, 1, 1)

        self.label_master_a = QLabel(self.groupBox_6)
        self.label_master_a.setObjectName(u"label_master_a")

        self.gridLayout_master_telemetry.addWidget(self.label_master_a, 4, 2, 1, 1)

        self.lineEdit_master_a = QLineEdit(self.groupBox_6)
        self.lineEdit_master_a.setObjectName(u"lineEdit_master_a")
        self.lineEdit_master_a.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_a, 4, 3, 1, 1)

        self.label_master_b = QLabel(self.groupBox_6)
        self.label_master_b.setObjectName(u"label_master_b")

        self.gridLayout_master_telemetry.addWidget(self.label_master_b, 5, 2, 1, 1)

        self.lineEdit_master_b = QLineEdit(self.groupBox_6)
        self.lineEdit_master_b.setObjectName(u"lineEdit_master_b")
        self.lineEdit_master_b.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_b, 5, 3, 1, 1)

        self.label_master_c = QLabel(self.groupBox_6)
        self.label_master_c.setObjectName(u"label_master_c")

        self.gridLayout_master_telemetry.addWidget(self.label_master_c, 6, 2, 1, 1)

        self.lineEdit_master_c = QLineEdit(self.groupBox_6)
        self.lineEdit_master_c.setObjectName(u"lineEdit_master_c")
        self.lineEdit_master_c.setReadOnly(True)

        self.gridLayout_master_telemetry.addWidget(self.lineEdit_master_c, 6, 3, 1, 1)

        self.gridLayout_master_telemetry.setColumnStretch(1, 1)
        self.gridLayout_master_telemetry.setColumnStretch(3, 1)

        self.verticalLayout_4.addLayout(self.gridLayout_master_telemetry)


        self.verticalLayout_6.addWidget(self.groupBox_6)

        self.verticalSpacer = QSpacerItem(20, 171, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)


        self.horizontalLayout_robotset.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.tab_robotset)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_slave_section = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_slave_section.setSpacing(10)
        self.verticalLayout_slave_section.setObjectName(u"verticalLayout_slave_section")
        self.groupBox_4 = QGroupBox(self.groupBox_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout_slave_telemetry = QGridLayout()
        self.gridLayout_slave_telemetry.setObjectName(u"gridLayout_slave_telemetry")
        self.label_slave_joint_header = QLabel(self.groupBox_4)
        self.label_slave_joint_header.setObjectName(u"label_slave_joint_header")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_joint_header, 0, 0, 1, 1)

        self.label_slave_tcp_header = QLabel(self.groupBox_4)
        self.label_slave_tcp_header.setObjectName(u"label_slave_tcp_header")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_tcp_header, 0, 2, 1, 1)

        self.label_slave_joint0 = QLabel(self.groupBox_4)
        self.label_slave_joint0.setObjectName(u"label_slave_joint0")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_joint0, 1, 0, 1, 1)

        self.lineEdit_slave_joint0 = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_joint0.setObjectName(u"lineEdit_slave_joint0")
        self.lineEdit_slave_joint0.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_joint0, 1, 1, 1, 1)

        self.label_slave_joint1 = QLabel(self.groupBox_4)
        self.label_slave_joint1.setObjectName(u"label_slave_joint1")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_joint1, 2, 0, 1, 1)

        self.lineEdit_slave_joint1 = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_joint1.setObjectName(u"lineEdit_slave_joint1")
        self.lineEdit_slave_joint1.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_joint1, 2, 1, 1, 1)

        self.label_slave_joint2 = QLabel(self.groupBox_4)
        self.label_slave_joint2.setObjectName(u"label_slave_joint2")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_joint2, 3, 0, 1, 1)

        self.lineEdit_slave_joint2 = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_joint2.setObjectName(u"lineEdit_slave_joint2")
        self.lineEdit_slave_joint2.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_joint2, 3, 1, 1, 1)

        self.label_slave_joint3 = QLabel(self.groupBox_4)
        self.label_slave_joint3.setObjectName(u"label_slave_joint3")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_joint3, 4, 0, 1, 1)

        self.lineEdit_slave_joint3 = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_joint3.setObjectName(u"lineEdit_slave_joint3")
        self.lineEdit_slave_joint3.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_joint3, 4, 1, 1, 1)

        self.label_slave_joint4 = QLabel(self.groupBox_4)
        self.label_slave_joint4.setObjectName(u"label_slave_joint4")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_joint4, 5, 0, 1, 1)

        self.lineEdit_slave_joint4 = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_joint4.setObjectName(u"lineEdit_slave_joint4")
        self.lineEdit_slave_joint4.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_joint4, 5, 1, 1, 1)

        self.label_slave_joint5 = QLabel(self.groupBox_4)
        self.label_slave_joint5.setObjectName(u"label_slave_joint5")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_joint5, 6, 0, 1, 1)

        self.lineEdit_slave_joint5 = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_joint5.setObjectName(u"lineEdit_slave_joint5")
        self.lineEdit_slave_joint5.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_joint5, 6, 1, 1, 1)

        self.label_slave_joint6 = QLabel(self.groupBox_4)
        self.label_slave_joint6.setObjectName(u"label_slave_joint6")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_joint6, 7, 0, 1, 1)

        self.lineEdit_slave_joint6 = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_joint6.setObjectName(u"lineEdit_slave_joint6")
        self.lineEdit_slave_joint6.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_joint6, 7, 1, 1, 1)

        self.label_slave_x = QLabel(self.groupBox_4)
        self.label_slave_x.setObjectName(u"label_slave_x")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_x, 1, 2, 1, 1)

        self.lineEdit_slave_x = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_x.setObjectName(u"lineEdit_slave_x")
        self.lineEdit_slave_x.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_x, 1, 3, 1, 1)

        self.label_slave_y = QLabel(self.groupBox_4)
        self.label_slave_y.setObjectName(u"label_slave_y")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_y, 2, 2, 1, 1)

        self.lineEdit_slave_y = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_y.setObjectName(u"lineEdit_slave_y")
        self.lineEdit_slave_y.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_y, 2, 3, 1, 1)

        self.label_slave_z = QLabel(self.groupBox_4)
        self.label_slave_z.setObjectName(u"label_slave_z")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_z, 3, 2, 1, 1)

        self.lineEdit_slave_z = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_z.setObjectName(u"lineEdit_slave_z")
        self.lineEdit_slave_z.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_z, 3, 3, 1, 1)

        self.label_slave_a = QLabel(self.groupBox_4)
        self.label_slave_a.setObjectName(u"label_slave_a")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_a, 4, 2, 1, 1)

        self.lineEdit_slave_a = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_a.setObjectName(u"lineEdit_slave_a")
        self.lineEdit_slave_a.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_a, 4, 3, 1, 1)

        self.label_slave_b = QLabel(self.groupBox_4)
        self.label_slave_b.setObjectName(u"label_slave_b")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_b, 5, 2, 1, 1)

        self.lineEdit_slave_b = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_b.setObjectName(u"lineEdit_slave_b")
        self.lineEdit_slave_b.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_b, 5, 3, 1, 1)

        self.label_slave_c = QLabel(self.groupBox_4)
        self.label_slave_c.setObjectName(u"label_slave_c")

        self.gridLayout_slave_telemetry.addWidget(self.label_slave_c, 6, 2, 1, 1)

        self.lineEdit_slave_c = QLineEdit(self.groupBox_4)
        self.lineEdit_slave_c.setObjectName(u"lineEdit_slave_c")
        self.lineEdit_slave_c.setReadOnly(True)

        self.gridLayout_slave_telemetry.addWidget(self.lineEdit_slave_c, 6, 3, 1, 1)

        self.gridLayout_slave_telemetry.setColumnStretch(1, 1)
        self.gridLayout_slave_telemetry.setColumnStretch(3, 1)

        self.verticalLayout_2.addLayout(self.gridLayout_slave_telemetry)


        self.verticalLayout_slave_section.addWidget(self.groupBox_4)

        self.groupBox_5 = QGroupBox(self.groupBox_2)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.horizontalLayout_slave_settings = QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_slave_settings.setSpacing(12)
        self.horizontalLayout_slave_settings.setObjectName(u"horizontalLayout_slave_settings")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.groupBox_5)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_8 = QLabel(self.groupBox_5)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)

        self.lineEdit_slave_home_joint5 = QLineEdit(self.groupBox_5)
        self.lineEdit_slave_home_joint5.setObjectName(u"lineEdit_slave_home_joint5")

        self.gridLayout.addWidget(self.lineEdit_slave_home_joint5, 3, 3, 1, 1)

        self.lineEdit_slave_home_joint0 = QLineEdit(self.groupBox_5)
        self.lineEdit_slave_home_joint0.setObjectName(u"lineEdit_slave_home_joint0")

        self.gridLayout.addWidget(self.lineEdit_slave_home_joint0, 1, 1, 1, 1)

        self.lineEdit_slave_home_joint4 = QLineEdit(self.groupBox_5)
        self.lineEdit_slave_home_joint4.setObjectName(u"lineEdit_slave_home_joint4")

        self.gridLayout.addWidget(self.lineEdit_slave_home_joint4, 3, 1, 1, 1)

        self.label_9 = QLabel(self.groupBox_5)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 2, 2, 1, 1)

        self.label_11 = QLabel(self.groupBox_5)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout.addWidget(self.label_11, 3, 2, 1, 1)

        self.lineEdit_slave_home_joint1 = QLineEdit(self.groupBox_5)
        self.lineEdit_slave_home_joint1.setObjectName(u"lineEdit_slave_home_joint1")

        self.gridLayout.addWidget(self.lineEdit_slave_home_joint1, 1, 3, 1, 1)

        self.lineEdit_slave_home_joint2 = QLineEdit(self.groupBox_5)
        self.lineEdit_slave_home_joint2.setObjectName(u"lineEdit_slave_home_joint2")

        self.gridLayout.addWidget(self.lineEdit_slave_home_joint2, 2, 1, 1, 1)

        self.lineEdit_slave_home_joint3 = QLineEdit(self.groupBox_5)
        self.lineEdit_slave_home_joint3.setObjectName(u"lineEdit_slave_home_joint3")

        self.gridLayout.addWidget(self.lineEdit_slave_home_joint3, 2, 3, 1, 1)

        self.label_3 = QLabel(self.groupBox_5)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 2, 1, 1)

        self.label_10 = QLabel(self.groupBox_5)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 3, 0, 1, 1)

        self.label_slave_home_joint6 = QLabel(self.groupBox_5)
        self.label_slave_home_joint6.setObjectName(u"label_slave_home_joint6")

        self.gridLayout.addWidget(self.label_slave_home_joint6, 4, 0, 1, 1)

        self.lineEdit_slave_home_joint6 = QLineEdit(self.groupBox_5)
        self.lineEdit_slave_home_joint6.setObjectName(u"lineEdit_slave_home_joint6")

        self.gridLayout.addWidget(self.lineEdit_slave_home_joint6, 4, 1, 1, 1)

        self.label = QLabel(self.groupBox_5)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 4)


        self.horizontalLayout_slave_settings.addLayout(self.gridLayout)

        self.gridLayout_slave_params = QGridLayout()
        self.gridLayout_slave_params.setObjectName(u"gridLayout_slave_params")
        self.label_slave_arm_vel = QLabel(self.groupBox_5)
        self.label_slave_arm_vel.setObjectName(u"label_slave_arm_vel")

        self.gridLayout_slave_params.addWidget(self.label_slave_arm_vel, 0, 0, 1, 1)

        self.lineEdit_slave_arm_vel = QLineEdit(self.groupBox_5)
        self.lineEdit_slave_arm_vel.setObjectName(u"lineEdit_slave_arm_vel")

        self.gridLayout_slave_params.addWidget(self.lineEdit_slave_arm_vel, 0, 1, 1, 1)

        self.label_slave_arm_acc = QLabel(self.groupBox_5)
        self.label_slave_arm_acc.setObjectName(u"label_slave_arm_acc")

        self.gridLayout_slave_params.addWidget(self.label_slave_arm_acc, 1, 0, 1, 1)

        self.lineEdit_slave_arm_acc = QLineEdit(self.groupBox_5)
        self.lineEdit_slave_arm_acc.setObjectName(u"lineEdit_slave_arm_acc")

        self.gridLayout_slave_params.addWidget(self.lineEdit_slave_arm_acc, 1, 1, 1, 1)

        self.label_slave_arm_jerk = QLabel(self.groupBox_5)
        self.label_slave_arm_jerk.setObjectName(u"label_slave_arm_jerk")

        self.gridLayout_slave_params.addWidget(self.label_slave_arm_jerk, 2, 0, 1, 1)

        self.lineEdit_slave_arm_jerk = QLineEdit(self.groupBox_5)
        self.lineEdit_slave_arm_jerk.setObjectName(u"lineEdit_slave_arm_jerk")

        self.gridLayout_slave_params.addWidget(self.lineEdit_slave_arm_jerk, 2, 1, 1, 1)

        self.pushButton_save_slave_param = QPushButton(self.groupBox_5)
        self.pushButton_save_slave_param.setObjectName(u"pushButton_save_slave_param")

        self.gridLayout_slave_params.addWidget(self.pushButton_save_slave_param, 3, 0, 1, 2)


        self.horizontalLayout_slave_settings.addLayout(self.gridLayout_slave_params)

        self.horizontalLayout_slave_settings.setStretch(0, 3)
        self.horizontalLayout_slave_settings.setStretch(1, 2)

        self.verticalLayout_slave_section.addWidget(self.groupBox_5)


        self.horizontalLayout_robotset.addWidget(self.groupBox_2)

        self.horizontalLayout_robotset.setStretch(0, 1)
        self.horizontalLayout_robotset.setStretch(1, 1)
        self.tabWidget_settings.addTab(self.tab_robotset, "")
        self.tab_cameraset = QWidget()
        self.tab_cameraset.setObjectName(u"tab_cameraset")
        self.verticalLayout_camera = QVBoxLayout(self.tab_cameraset)
        self.verticalLayout_camera.setObjectName(u"verticalLayout_camera")
        self.label_camera = QLabel(self.tab_cameraset)
        self.label_camera.setObjectName(u"label_camera")

        self.verticalLayout_camera.addWidget(self.label_camera)

        self.spacer_camera = QSpacerItem(20, 200, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_camera.addItem(self.spacer_camera)

        self.tabWidget_settings.addTab(self.tab_cameraset, "")
        self.tab_handset = QWidget()
        self.tab_handset.setObjectName(u"tab_handset")
        self.verticalLayout_hand = QVBoxLayout(self.tab_handset)
        self.verticalLayout_hand.setObjectName(u"verticalLayout_hand")
        self.groupBox_3 = QGroupBox(self.tab_handset)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_hand_model = QHBoxLayout()
        self.horizontalLayout_hand_model.setObjectName(u"horizontalLayout_hand_model")
        self.label_hand_model_settings = QLabel(self.groupBox_3)
        self.label_hand_model_settings.setObjectName(u"label_hand_model_settings")

        self.horizontalLayout_hand_model.addWidget(self.label_hand_model_settings)

        self.comboBox_hand_model_settings = QComboBox(self.groupBox_3)
        self.comboBox_hand_model_settings.setObjectName(u"comboBox_hand_model_settings")

        self.horizontalLayout_hand_model.addWidget(self.comboBox_hand_model_settings)


        self.verticalLayout_3.addLayout(self.horizontalLayout_hand_model)

        self.tableWidget_hand_actions = QTableWidget(self.groupBox_3)
        if (self.tableWidget_hand_actions.columnCount() < 1):
            self.tableWidget_hand_actions.setColumnCount(1)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_hand_actions.setHorizontalHeaderItem(0, __qtablewidgetitem)
        self.tableWidget_hand_actions.setObjectName(u"tableWidget_hand_actions")

        self.verticalLayout_3.addWidget(self.tableWidget_hand_actions)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_2.addWidget(self.label_6)

        self.label_4 = QLabel(self.groupBox_3)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_2.addWidget(self.label_4)

        self.comboBox_hand_current_close = QComboBox(self.groupBox_3)
        self.comboBox_hand_current_close.setObjectName(u"comboBox_hand_current_close")

        self.horizontalLayout_2.addWidget(self.comboBox_hand_current_close)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_2.addWidget(self.label_5)

        self.comboBox_hand_current_open = QComboBox(self.groupBox_3)
        self.comboBox_hand_current_open.setObjectName(u"comboBox_hand_current_open")

        self.horizontalLayout_2.addWidget(self.comboBox_hand_current_open)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.label_7 = QLabel(self.groupBox_3)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_2.addWidget(self.label_7)

        self.comboBox_hand_actions_test = QComboBox(self.groupBox_3)
        self.comboBox_hand_actions_test.setObjectName(u"comboBox_hand_actions_test")

        self.horizontalLayout_2.addWidget(self.comboBox_hand_actions_test)

        self.pushButton_hand_test = QPushButton(self.groupBox_3)
        self.pushButton_hand_test.setObjectName(u"pushButton_hand_test")

        self.horizontalLayout_2.addWidget(self.pushButton_hand_test)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_hand_actions = QHBoxLayout()
        self.horizontalLayout_hand_actions.setObjectName(u"horizontalLayout_hand_actions")
        self.pushButton_add_hand_actions = QPushButton(self.groupBox_3)
        self.pushButton_add_hand_actions.setObjectName(u"pushButton_add_hand_actions")

        self.horizontalLayout_hand_actions.addWidget(self.pushButton_add_hand_actions)

        self.pushButton_delete_hand_actions = QPushButton(self.groupBox_3)
        self.pushButton_delete_hand_actions.setObjectName(u"pushButton_delete_hand_actions")

        self.horizontalLayout_hand_actions.addWidget(self.pushButton_delete_hand_actions)

        self.horizontalSpacer_hand_actions = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_hand_actions.addItem(self.horizontalSpacer_hand_actions)

        self.pushButton_save_hand_actions = QPushButton(self.groupBox_3)
        self.pushButton_save_hand_actions.setObjectName(u"pushButton_save_hand_actions")

        self.horizontalLayout_hand_actions.addWidget(self.pushButton_save_hand_actions)


        self.verticalLayout_3.addLayout(self.horizontalLayout_hand_actions)


        self.verticalLayout_5.addLayout(self.verticalLayout_3)


        self.verticalLayout_hand.addWidget(self.groupBox_3)

        self.tabWidget_settings.addTab(self.tab_handset, "")

        self.verticalLayout.addWidget(self.tabWidget_settings)

        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(SettingsDialog)

        self.tabWidget_settings.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Setting", None))
        self.groupBox.setTitle(QCoreApplication.translate("SettingsDialog", u"MasterRobot", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("SettingsDialog", u"Current Pos", None))
        self.label_master_joint_header.setText(QCoreApplication.translate("SettingsDialog", u"\u5173\u8282\u89d2\u5ea6 (\u00b0)", None))
        self.label_master_tcp_header.setText(QCoreApplication.translate("SettingsDialog", u"TCP \u4f4d\u59ff", None))
        self.label_master_joint0.setText(QCoreApplication.translate("SettingsDialog", u"joint0", None))
        self.label_master_joint1.setText(QCoreApplication.translate("SettingsDialog", u"joint1", None))
        self.label_master_joint2.setText(QCoreApplication.translate("SettingsDialog", u"joint2", None))
        self.label_master_joint3.setText(QCoreApplication.translate("SettingsDialog", u"joint3", None))
        self.label_master_joint4.setText(QCoreApplication.translate("SettingsDialog", u"joint4", None))
        self.label_master_joint5.setText(QCoreApplication.translate("SettingsDialog", u"joint5", None))
        self.label_master_joint6.setText(QCoreApplication.translate("SettingsDialog", u"joint6", None))
        self.label_master_x.setText(QCoreApplication.translate("SettingsDialog", u"x (mm)", None))
        self.lineEdit_master_x.setText(QCoreApplication.translate("SettingsDialog", u"\u2014", None))
        self.label_master_y.setText(QCoreApplication.translate("SettingsDialog", u"y (mm)", None))
        self.lineEdit_master_y.setText(QCoreApplication.translate("SettingsDialog", u"\u2014", None))
        self.label_master_z.setText(QCoreApplication.translate("SettingsDialog", u"z (mm)", None))
        self.lineEdit_master_z.setText(QCoreApplication.translate("SettingsDialog", u"\u2014", None))
        self.label_master_a.setText(QCoreApplication.translate("SettingsDialog", u"a (rad)", None))
        self.lineEdit_master_a.setText(QCoreApplication.translate("SettingsDialog", u"\u2014", None))
        self.label_master_b.setText(QCoreApplication.translate("SettingsDialog", u"b (rad)", None))
        self.lineEdit_master_b.setText(QCoreApplication.translate("SettingsDialog", u"\u2014", None))
        self.label_master_c.setText(QCoreApplication.translate("SettingsDialog", u"c (rad)", None))
        self.lineEdit_master_c.setText(QCoreApplication.translate("SettingsDialog", u"\u2014", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SettingsDialog", u"SlaveRobot", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("SettingsDialog", u"Current Pos", None))
        self.label_slave_joint_header.setText(QCoreApplication.translate("SettingsDialog", u"\u5173\u8282\u89d2\u5ea6 (\u00b0)", None))
        self.label_slave_tcp_header.setText(QCoreApplication.translate("SettingsDialog", u"TCP \u4f4d\u59ff", None))
        self.label_slave_joint0.setText(QCoreApplication.translate("SettingsDialog", u"joint0", None))
        self.label_slave_joint1.setText(QCoreApplication.translate("SettingsDialog", u"joint1", None))
        self.label_slave_joint2.setText(QCoreApplication.translate("SettingsDialog", u"joint2", None))
        self.label_slave_joint3.setText(QCoreApplication.translate("SettingsDialog", u"joint3", None))
        self.label_slave_joint4.setText(QCoreApplication.translate("SettingsDialog", u"joint4", None))
        self.label_slave_joint5.setText(QCoreApplication.translate("SettingsDialog", u"joint5", None))
        self.label_slave_joint6.setText(QCoreApplication.translate("SettingsDialog", u"joint6", None))
        self.label_slave_x.setText(QCoreApplication.translate("SettingsDialog", u"x (mm)", None))
        self.label_slave_y.setText(QCoreApplication.translate("SettingsDialog", u"y (mm)", None))
        self.label_slave_z.setText(QCoreApplication.translate("SettingsDialog", u"z (mm)", None))
        self.label_slave_a.setText(QCoreApplication.translate("SettingsDialog", u"a (rad)", None))
        self.label_slave_b.setText(QCoreApplication.translate("SettingsDialog", u"b (rad)", None))
        self.label_slave_c.setText(QCoreApplication.translate("SettingsDialog", u"c (rad)", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("SettingsDialog", u"Home Pos / Motion Limits", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDialog", u"Joint0", None))
        self.label_8.setText(QCoreApplication.translate("SettingsDialog", u"Joint2", None))
        self.label_9.setText(QCoreApplication.translate("SettingsDialog", u"Joint3", None))
        self.label_11.setText(QCoreApplication.translate("SettingsDialog", u"Joint5", None))
        self.label_3.setText(QCoreApplication.translate("SettingsDialog", u"Joint1", None))
        self.label_10.setText(QCoreApplication.translate("SettingsDialog", u"Joint4", None))
        self.label_slave_home_joint6.setText(QCoreApplication.translate("SettingsDialog", u"Joint6", None))
        self.label.setText(QCoreApplication.translate("SettingsDialog", u"Home Pos (\u00b0)", None))
        self.label_slave_arm_vel.setText(QCoreApplication.translate("SettingsDialog", u"Vel (\u00b0/s)", None))
        self.lineEdit_slave_arm_vel.setText(QCoreApplication.translate("SettingsDialog", u"80", None))
        self.label_slave_arm_acc.setText(QCoreApplication.translate("SettingsDialog", u"Acc (\u00b0/s\u00b2)", None))
        self.lineEdit_slave_arm_acc.setText(QCoreApplication.translate("SettingsDialog", u"1000", None))
        self.label_slave_arm_jerk.setText(QCoreApplication.translate("SettingsDialog", u"Jerk (\u00b0/s\u00b3)", None))
        self.lineEdit_slave_arm_jerk.setText(QCoreApplication.translate("SettingsDialog", u"1000", None))
        self.pushButton_save_slave_param.setText(QCoreApplication.translate("SettingsDialog", u"Save", None))
        self.tabWidget_settings.setTabText(self.tabWidget_settings.indexOf(self.tab_robotset), QCoreApplication.translate("SettingsDialog", u"Robot Set", None))
        self.label_camera.setText(QCoreApplication.translate("SettingsDialog", u"\u76f8\u673a\u8bbe\u7f6e", None))
        self.tabWidget_settings.setTabText(self.tabWidget_settings.indexOf(self.tab_cameraset), QCoreApplication.translate("SettingsDialog", u"Camera Set", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("SettingsDialog", u"Actions", None))
        self.label_hand_model_settings.setText(QCoreApplication.translate("SettingsDialog", u"\u578b\u53f7", None))
        ___qtablewidgetitem = self.tableWidget_hand_actions.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("SettingsDialog", u"\u52a8\u4f5c\u540d\u79f0", None))
        self.label_6.setText(QCoreApplication.translate("SettingsDialog", u"Set Current Actions", None))
        self.label_4.setText(QCoreApplication.translate("SettingsDialog", u"Close", None))
        self.label_5.setText(QCoreApplication.translate("SettingsDialog", u"Open", None))
        self.label_7.setText(QCoreApplication.translate("SettingsDialog", u"Action test", None))
        self.pushButton_hand_test.setText(QCoreApplication.translate("SettingsDialog", u"test", None))
        self.pushButton_add_hand_actions.setText(QCoreApplication.translate("SettingsDialog", u"Add", None))
        self.pushButton_delete_hand_actions.setText(QCoreApplication.translate("SettingsDialog", u"Delete", None))
        self.pushButton_save_hand_actions.setText(QCoreApplication.translate("SettingsDialog", u"Save Actions", None))
        self.tabWidget_settings.setTabText(self.tabWidget_settings.indexOf(self.tab_handset), QCoreApplication.translate("SettingsDialog", u"Hand Set", None))
    # retranslateUi

