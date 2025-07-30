from PyQt6.QtWidgets import QDialog, QMessageBox, QApplication, QStyle, QFileDialog
from ..ui_compiled.ConnectDialog import Ui_ConnectDialog
from ..types.Connection import Connection
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon


if TYPE_CHECKING:
    from .MainWindow import MainWindow


class ConnectDialog(QDialog, Ui_ConnectDialog):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)

        self.setupUi(self)

        self._ok = False
        self._connection = None
        self._main_window = main_window

        self.ok_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)))
        self.cancel_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)))

        self.browse_button.clicked.connect(self._browse_button_clicked)
        self.ok_button.clicked.connect(self._ok_button_clicked)
        self.cancel_button.clicked.connect(self.close)

    def _browse_button_clicked(self) -> None:
        path = QFileDialog.getOpenFileName(self, directory="/")[0]

        if path != "":
            self.address_edit.setText( f"unix:path={path}")

    def _ok_button_clicked(self) -> None:
        name = self.name_edit.text().strip()
        address = self.address_edit.text().strip()

        if name == "":
            QMessageBox.critical(self, QCoreApplication.translate("ConnectDialog", "Name not set"), QCoreApplication.translate("ConnectDialog", "You need to enter a name"))
            return

        if address == "":
            QMessageBox.critical(self, QCoreApplication.translate("ConnectDialog", "Address not set"), QCoreApplication.translate("ConnectDialog", "You need to enter a address"))
            return

        connection = Connection.new_custom_connection(address, name)
        if not connection.is_connected():
            QMessageBox.critical(self, QCoreApplication.translate("ConnectDialog", "Invalid Address"), QCoreApplication.translate("ConnectDialog", "Could not connect to {{address}}").replace("{{address}}", address))
            return

        self._ok = True
        self._connection = connection

        self.close()

    def get_connection(self) -> tuple[Connection, bool] | None:
        self._ok = False

        self.exec()

        if not self._ok:
            return

        return (self._connection, self.auto_connect_check_box.isChecked())
