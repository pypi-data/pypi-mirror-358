from PyQt6.QtWidgets import QWidget, QPushButton, QFileDialog
from PyQt6.QtCore import QCoreApplication
import os


class BrowseButton(QPushButton):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(QCoreApplication.translate("BrowseButton", "Browse"), parent)

        self._current_path = ""

        self.clicked.connect(self._button_clicked)

    def _button_clicked(self) -> None:
        path = QFileDialog.getOpenFileName(self, directory=os.path.expanduser("~"))[0]

        if path == "":
            return

        self._current_path = path
        self.setText(os.path.basename(path))

    def get_file_path(self) -> str:
        return self._current_path

    def get_validation_error(self) -> str | None:
        if self._current_path == "":
            return QCoreApplication.translate("BrowseButton", "No file selected")
        else:
            return None
