from PySide6.QtWidgets import QDialog

from src.ui.settings_window import Ui_SettingsDialog


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.rejected.connect(self.reject)
