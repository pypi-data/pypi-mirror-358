from PyQt6.QtWidgets import QWidget, QDialog, QApplication, QStyle
from ..ui_compiled.WelcomeDialog import Ui_WelcomeDialog
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon
import os


if TYPE_CHECKING:
    from ..Environment import Environment


class WelcomeDialog(QDialog, Ui_WelcomeDialog):
    def __init__(self, parent: QWidget | None, env: "Environment") -> None:
        super().__init__(parent)

        self.setupUi(self)

        self._env = env

        self.ok_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)))

        self.ok_button.clicked.connect(self.close)

    def open_dialog(self) -> None:
        self.show_startup_check_box.setChecked(self._env.settings.get("showWelcomeDialogStartup"))

        self.exec()

        self._env.settings.set("showWelcomeDialogStartup", self.show_startup_check_box.isChecked())
        self._env.settings.save(os.path.join(self._env.data_dir, "settings.json"))
