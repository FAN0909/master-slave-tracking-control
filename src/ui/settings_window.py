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
    QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QTabWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

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

        self.groupBox_4 = QGroupBox(self.groupBox_3)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_4 = QLabel(self.groupBox_4)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_2.addWidget(self.label_4)

        self.comboBox_hand_current_close = QComboBox(self.groupBox_4)
        self.comboBox_hand_current_close.setObjectName(u"comboBox_hand_current_close")

        self.horizontalLayout_2.addWidget(self.comboBox_hand_current_close)

        self.label_5 = QLabel(self.groupBox_4)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_2.addWidget(self.label_5)

        self.comboBox_hand_current_open = QComboBox(self.groupBox_4)
        self.comboBox_hand_current_open.setObjectName(u"comboBox_hand_current_open")

        self.horizontalLayout_2.addWidget(self.comboBox_hand_current_open)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)


        self.verticalLayout_5.addWidget(self.groupBox_4)


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
        self.label_hand_model_settings.setText(QCoreApplication.translate("SettingsDialog", u"\u578b\u53f7", None))
        ___qtablewidgetitem = self.tableWidget_hand_actions.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("SettingsDialog", u"\u52a8\u4f5c\u540d\u79f0", None))
        self.pushButton_add_hand_actions.setText(QCoreApplication.translate("SettingsDialog", u"Add", None))
        self.pushButton_delete_hand_actions.setText(QCoreApplication.translate("SettingsDialog", u"Delete", None))
        self.pushButton_save_hand_actions.setText(QCoreApplication.translate("SettingsDialog", u"Save Actions", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("SettingsDialog", u"Set Actions", None))
        self.label_4.setText(QCoreApplication.translate("SettingsDialog", u"Close", None))
        self.label_5.setText(QCoreApplication.translate("SettingsDialog", u"Open", None))
        self.tabWidget_settings.setTabText(self.tabWidget_settings.indexOf(self.tab_handset), QCoreApplication.translate("SettingsDialog", u"Hand Set", None))
    # retranslateUi

