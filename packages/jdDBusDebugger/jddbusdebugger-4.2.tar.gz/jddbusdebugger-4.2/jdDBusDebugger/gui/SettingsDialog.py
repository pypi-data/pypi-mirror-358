from ..ui_compiled.SettingsDialog import Ui_SettingsDialog
from PyQt6.QtWidgets import QDialog, QApplication, QStyle
from ..core.Languages import get_language_names
from ..Functions import select_combo_box_data
from PyQt6.QtCore import Qt, QCoreApplication
from ..core.Settings import Settings
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon
import os


if TYPE_CHECKING:
    from ..Environment import Environment
    from .MainWindow import MainWindow


class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, env: "Environment", main_window: "MainWindow") -> None:
        super().__init__(main_window)

        self.setupUi(self)

        self._env = env

        language_names = get_language_names()
        self.language_box.addItem(language_names.get("en", "en"), "en")
        for lang in env.get_available_languages():
            self.language_box.addItem(language_names.get(lang, lang), lang)
        self.language_box.model().sort(0, Qt.SortOrder.AscendingOrder)
        self.language_box.insertItem(0, QCoreApplication.translate("SettingsDialog", "Use system language"), "default")

        self.method_returns_object_path_box.addItem(QCoreApplication.translate("SettingsDialog", "Add object path to list"), "add")
        self.method_returns_object_path_box.addItem(QCoreApplication.translate("SettingsDialog", "Ask the User"), "ask")
        self.method_returns_object_path_box.addItem(QCoreApplication.translate("SettingsDialog", "Do nothing"), "nothing")

        self.reset_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton)))
        self.ok_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)))
        self.cancel_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)))

        self.reset_button.clicked.connect(lambda: self._update_widgets(Settings()))
        self.ok_button.clicked.connect(self._ok_button_clicked)
        self.cancel_button.clicked.connect(self.close)

    def _update_widgets(self, settings: Settings) -> None:
        select_combo_box_data(self.language_box, settings.get("language"))
        select_combo_box_data(self.method_returns_object_path_box, settings.get("methodReturnsObjectPath"))
        self.warn_session_system_connection_fail_check_box.setChecked(settings.get("warnSesssionSystemConnectionFail"))

    def _get_settings(self, settings: Settings) -> None:
        settings.set("language", self.language_box.currentData())
        settings.set("methodReturnsObjectPath", self.method_returns_object_path_box.currentData())
        settings.set("warnSesssionSystemConnectionFail", self.warn_session_system_connection_fail_check_box.isChecked())

    def _ok_button_clicked(self) -> None:
        self._get_settings(self._env.settings)

        self._env.settings.save(os.path.join(self._env.data_dir, "settings.json"))

        self.close()

    def open_dialog(self) -> None:
        self._update_widgets(self._env.settings)

        self.exec()
