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
    QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QSpacerItem, QTabWidget, QVBoxLayout,
    QWidget)

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

        self.pushButton_save_slave_param = QPushButton(self.groupBox_2)
        self.pushButton_save_slave_param.setObjectName(u"pushButton_save_slave_param")
        self.pushButton_save_slave_param.setGeometry(QRect(280, 400, 95, 25))

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
        self.groupBox_3 = QGroupBox(self.tab_handset)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.listWidget_hand_actions = QListWidget(self.groupBox_3)
        QListWidgetItem(self.listWidget_hand_actions)
        QListWidgetItem(self.listWidget_hand_actions)
        QListWidgetItem(self.listWidget_hand_actions)
        QListWidgetItem(self.listWidget_hand_actions)
        QListWidgetItem(self.listWidget_hand_actions)
        self.listWidget_hand_actions.setObjectName(u"listWidget_hand_actions")
        self.listWidget_hand_actions.setGeometry(QRect(10, 40, 621, 221))

        self.verticalLayout_hand.addWidget(self.groupBox_3)

        self.tabWidget_settings.addTab(self.tab_handset, "")

        self.verticalLayout.addWidget(self.tabWidget_settings)

        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(SettingsDialog)

        self.tabWidget_settings.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Setting", None))
        self.groupBox.setTitle(QCoreApplication.translate("SettingsDialog", u"MasterRobot", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SettingsDialog", u"SlaveRobot", None))
        self.label.setText(QCoreApplication.translate("SettingsDialog", u"Vel(\u00b0/s)", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDialog", u"Acc\u00b0/s^2", None))
        self.label_3.setText(QCoreApplication.translate("SettingsDialog", u"Jerk\u00b0/s^3", None))
        self.lineEdit_slave_arm_vel.setText(QCoreApplication.translate("SettingsDialog", u"80", None))
        self.lineEdit_slave_arm_acc.setText(QCoreApplication.translate("SettingsDialog", u"1000", None))
        self.lineEdit_slave_arm_jerk.setText(QCoreApplication.translate("SettingsDialog", u"1000", None))
        self.pushButton_save_slave_param.setText(QCoreApplication.translate("SettingsDialog", u"Save", None))
        self.tabWidget_settings.setTabText(self.tabWidget_settings.indexOf(self.tab_robotset), QCoreApplication.translate("SettingsDialog", u"Robot Set", None))
        self.label_camera.setText(QCoreApplication.translate("SettingsDialog", u"\u76f8\u673a\u8bbe\u7f6e", None))
        self.tabWidget_settings.setTabText(self.tabWidget_settings.indexOf(self.tab_cameraset), QCoreApplication.translate("SettingsDialog", u"Camera Set", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("SettingsDialog", u"Actions", None))

        __sortingEnabled = self.listWidget_hand_actions.isSortingEnabled()
        self.listWidget_hand_actions.setSortingEnabled(False)
        ___qlistwidgetitem = self.listWidget_hand_actions.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("SettingsDialog", u"1", None))
        ___qlistwidgetitem1 = self.listWidget_hand_actions.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("SettingsDialog", u"2", None))
        ___qlistwidgetitem2 = self.listWidget_hand_actions.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("SettingsDialog", u"3", None))
        ___qlistwidgetitem3 = self.listWidget_hand_actions.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("SettingsDialog", u"4", None))
        ___qlistwidgetitem4 = self.listWidget_hand_actions.item(4)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("SettingsDialog", u"5", None))
        self.listWidget_hand_actions.setSortingEnabled(__sortingEnabled)

        self.tabWidget_settings.setTabText(self.tabWidget_settings.indexOf(self.tab_handset), QCoreApplication.translate("SettingsDialog", u"Hand Set", None))
    # retranslateUi

