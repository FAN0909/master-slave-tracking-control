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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(820, 535)
        SettingsDialog.setMinimumSize(QSize(480, 320))
        self.verticalLayout = QVBoxLayout(SettingsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget_settings = QTabWidget(SettingsDialog)
        self.tabWidget_settings.setObjectName(u"tabWidget_settings")
        self.tab_robotset = QWidget()
        self.tab_robotset.setObjectName(u"tab_robotset")
        self.verticalLayout_2 = QVBoxLayout(self.tab_robotset)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox = QGroupBox(self.tab_robotset)
        self.groupBox.setObjectName(u"groupBox")

        self.horizontalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.tab_robotset)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayoutWidget = QWidget(self.groupBox_2)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 30, 181, 89))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.formLayoutWidget)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.label_2 = QLabel(self.formLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.label_3 = QLabel(self.formLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.lineEdit_slave_arm_vel = QLineEdit(self.formLayoutWidget)
        self.lineEdit_slave_arm_vel.setObjectName(u"lineEdit_slave_arm_vel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit_slave_arm_vel)

        self.lineEdit_slave_arm_acc = QLineEdit(self.formLayoutWidget)
        self.lineEdit_slave_arm_acc.setObjectName(u"lineEdit_slave_arm_acc")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit_slave_arm_acc)

        self.lineEdit_slave_arm_jerk = QLineEdit(self.formLayoutWidget)
        self.lineEdit_slave_arm_jerk.setObjectName(u"lineEdit_slave_arm_jerk")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineEdit_slave_arm_jerk)


        self.horizontalLayout.addWidget(self.groupBox_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

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
        self.label_hand = QLabel(self.tab_handset)
        self.label_hand.setObjectName(u"label_hand")

        self.verticalLayout_hand.addWidget(self.label_hand)

        self.spacer_hand = QSpacerItem(20, 200, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_hand.addItem(self.spacer_hand)

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
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"\u8bbe\u7f6e", None))
        self.groupBox.setTitle(QCoreApplication.translate("SettingsDialog", u"MasterRobot", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SettingsDialog", u"SlaveRobot", None))
        self.label.setText(QCoreApplication.translate("SettingsDialog", u"Vel(\u00b0/s)", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDialog", u"Acc\u00b0/s^2", None))
        self.label_3.setText(QCoreApplication.translate("SettingsDialog", u"Jerk\u00b0/s^3", None))
        self.lineEdit_slave_arm_vel.setText(QCoreApplication.translate("SettingsDialog", u"80", None))
        self.lineEdit_slave_arm_acc.setText(QCoreApplication.translate("SettingsDialog", u"1000", None))
        self.lineEdit_slave_arm_jerk.setText(QCoreApplication.translate("SettingsDialog", u"1000", None))
        self.tabWidget_settings.setTabText(self.tabWidget_settings.indexOf(self.tab_robotset), QCoreApplication.translate("SettingsDialog", u"Robot Set", None))
        self.label_camera.setText(QCoreApplication.translate("SettingsDialog", u"\u76f8\u673a\u8bbe\u7f6e", None))
        self.tabWidget_settings.setTabText(self.tabWidget_settings.indexOf(self.tab_cameraset), QCoreApplication.translate("SettingsDialog", u"Camera Set", None))
        self.label_hand.setText(QCoreApplication.translate("SettingsDialog", u"\u7075\u5de7\u624b\u8bbe\u7f6e", None))
        self.tabWidget_settings.setTabText(self.tabWidget_settings.indexOf(self.tab_handset), QCoreApplication.translate("SettingsDialog", u"Hand Set", None))
    # retranslateUi

