from ..ui_compiled.ConnectFlatpakDialog import Ui_ConnectFlatpakDialog
from PyQt6.QtWidgets import QDialog, QMessageBox, QApplication, QStyle
from ..Functions import get_running_flatpaks
from ..types.Connection import Connection
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon


if TYPE_CHECKING:
    from .MainWindow import MainWindow


class ConnectFlatpakDialog(QDialog, Ui_ConnectFlatpakDialog):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)

        self.setupUi(self)

        self._main_window = main_window

        self.flatpak_box.setPlaceholderText(QCoreApplication.translate("ConnectFlatpakDialog", "Select flatpak"))
        self.flatpak_box.setCurrentIndex(-1)

        self.ok_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)))
        self.cancel_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)))

        self.flatpak_box.currentIndexChanged.connect(self._flatpak_box_changed)
        self.ok_button.clicked.connect(self._ok_button_clicked)
        self.cancel_button.clicked.connect(self.close)

    def _flatpak_box_changed(self) -> None:
        self.ok_button.setEnabled(True)

        if self.name_edit.text() == "":
            self.name_edit.setText(self.flatpak_box.currentText().split(" ")[0])

    def _ok_button_clicked(self) -> None:
        name = self.name_edit.text().strip()

        if name == "":
            QMessageBox.critical(
                self,
                QCoreApplication.translate("ConnectFlatpakDialog", "Name not set"),
                QCoreApplication.translate("ConnectFlatpakDialog", "You need to enter a name"),
            )
            return

        if self.session_bus_radio_button.isChecked():
            bus = "session"
        elif self.system_bus_radio_button.isChecked():
            bus = "system"
        elif self.accessibility_bus_radio_button.isChecked():
            bus = "flatpak-accessibility"

        conn = Connection.new_process_connection(self.flatpak_box.currentData(), bus, name)

        if not conn.is_connected():
            QMessageBox.critical(
                self,
                QCoreApplication.translate("ConnectFlatpakDialog", "Error"),
                QCoreApplication.translate("ConnectFlatpakDialog", "Unable to connect to the specified bus of the Flatpak"),
            )
            return

        self._main_window.add_tab(conn, True, True)
        self.close()

    def open_dialog(self) -> None:
        flatpak_list = get_running_flatpaks()

        if len(flatpak_list) == 0:
            QMessageBox.critical(
                self._main_window,
                QCoreApplication.translate("ConnectFlatpakDialog", "No running Flatpaks"),
                QCoreApplication.translate("ConnectFlatpakDialog", "jdDBusDebugger was unable to detect any running Flatpaks"),
            )
            return

        for current_flatpak in flatpak_list:
            self.flatpak_box.addItem(f'{current_flatpak["id"]} ({current_flatpak["pid"]})', current_flatpak["pid"])

        self.exec()
