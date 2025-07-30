from PyQt6.QtWidgets import QDialog, QMessageBox, QApplication, QStyle
from ..ui_compiled.ConnectServerDialog import Ui_ConnectServerDialog
from PyQt6.QtCore import QByteArray, QCoreApplication
from PyQt6.QtNetwork import QUdpSocket, QHostAddress
from ..types.Connection import Connection
from ..Constants import SERVER_CONSTANTS
from ..Functions import check_socat
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon
import traceback
import secrets
import json
import sys


if TYPE_CHECKING:
    from .MainWindow import MainWindow


class ConnectServerDialog(QDialog, Ui_ConnectServerDialog):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)

        self.setupUi(self)

        self._main_window = main_window
        self._token = secrets.token_hex()

        self._listen_socket = QUdpSocket(self)
        send_socket = QUdpSocket(self)

        self._listen_socket.bind(SERVER_CONSTANTS.REPLY_PORT, QUdpSocket.BindFlag.ShareAddress)
        self._listen_socket.readyRead.connect(self._read_socket)

        self.server_box.setPlaceholderText(QCoreApplication.translate("ConnectServerDialog", "Select server"))
        self.server_box.setCurrentIndex(-1)

        datagram = QByteArray(f"{SERVER_CONSTANTS.BROADCAST_MAGIC}:{self._token}".encode("utf-8"))
        send_socket.writeDatagram(datagram, QHostAddress.SpecialAddress.Broadcast, SERVER_CONSTANTS.BROADCAST_PORT)

        self.ok_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)))
        self.cancel_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)))

        self.server_box.currentIndexChanged.connect(self._server_box_changed)
        self.ok_button.clicked.connect(self._ok_button_clicked)
        self.cancel_button.clicked.connect(self.close)

    def _recive_data(self, data: bytes) -> None:
        start_bytes = f"{SERVER_CONSTANTS.REPLY_MAGIC}:{self._token}:".encode("utf-8")

        if not data.startswith(start_bytes):
            return

        json_text = data.removeprefix(start_bytes).decode("utf-8")

        json_data = json.loads(json_text)

        self.server_box.addItem(f"{json_data['hostname']} ({json_data['ip']})", json_data['ip'])

    def _read_socket(self) -> None:
        while self._listen_socket.hasPendingDatagrams():
            data, _ , _ = self._listen_socket.readDatagram(int(self._listen_socket.pendingDatagramSize()))

            try:
                self._recive_data(data)
            except Exception:
                print(traceback.format_exc(), file=sys.stderr)

    def _server_box_changed(self) -> None:
        self.ok_button.setEnabled(True)

        if self.name_edit.text() == "":
            self.name_edit.setText(self.server_box.currentText().split(" ")[0])

    def _ok_button_clicked(self) -> None:
        name = self.name_edit.text().strip()

        if name == "":
            QMessageBox.critical(
                self,
                QCoreApplication.translate("ConnectServerDialog", "Name not set"),
                QCoreApplication.translate("ConnectServerDialog", "You need to enter a name"),
            )
            return

        conn = Connection.new_server_connection(self.server_box.currentData(), name)

        if not conn.is_connected():
            QMessageBox.critical(
                self,
                QCoreApplication.translate("ConnectServerDialog", "Error"),
                QCoreApplication.translate("ConnectServerDialog", "Unable to connect to the Server"),
            )
            return

        self._main_window.add_tab(conn, True, True)
        self.close()

    def open_dialog(self) -> None:
        if not check_socat(self._main_window):
            return

        self.exec()
