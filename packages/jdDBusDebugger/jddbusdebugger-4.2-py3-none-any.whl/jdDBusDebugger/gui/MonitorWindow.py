from PyQt6.QtGui import QCloseEvent, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import QObject, QThread, QCoreApplication, pyqtSignal
from PyQt6.QtWidgets import QWidget, QStyle, QApplication, QMessageBox
from ..ui_compiled.MonitorWindow import Ui_MonitorWindow
from PyQt6.QtDBus import QDBusMessage
from typing import TYPE_CHECKING
import jeepney.io.blocking
import dataclasses
import jeepney
import copy
import sys


if TYPE_CHECKING:
    from ..types.Connection import Connection
    from .MainWindow import MainWindow


@dataclasses.dataclass
class _MessageFilter:
    sender: str = dataclasses.field(default="")
    destination: str = dataclasses.field(default="")
    path: str = dataclasses.field(default="")
    interface: str = dataclasses.field(default="")
    member: str = dataclasses.field(default="")
    signature: str = dataclasses.field(default="")
    message_types: list[int] = dataclasses.field(default_factory=lambda: [])


class _Message:
    def __init__(self, msg: jeepney.low_level.Message) -> None:
        self._message_type = msg.header.message_type
        self._body = str(msg.body)

        self._header = {}
        for i in (jeepney.HeaderFields.sender, jeepney.HeaderFields.destination, jeepney.HeaderFields.path, jeepney.HeaderFields.interface, jeepney.HeaderFields.member, jeepney.HeaderFields.signature):
            try:
                self._header[i] = msg.header.fields[i]
            except KeyError:
                self._header[i] = ""

    def check_message_filter(self, message_filter: _MessageFilter) -> bool:
        if self._message_type not in message_filter.message_types:
            return False

        for field in (
            (message_filter.sender, jeepney.HeaderFields.sender),
            (message_filter.destination, jeepney.HeaderFields.destination),
            (message_filter.path, jeepney.HeaderFields.path),
            (message_filter.interface, jeepney.HeaderFields.interface),
            (message_filter.member, jeepney.HeaderFields.member),
        ):
            if field[0] != "":
                if field[0] not in self._header[field[1]]:
                    return False

        return True

    def get_row(self) -> list[QStandardItem]:
        row: list[QStandardItem] = []

        match self._message_type:
            case jeepney.MessageType.method_call:
                row.append(QStandardItem(QCoreApplication.translate("MonitorWindow", "Method call", "Message type")))
            case jeepney.MessageType.method_return:
                row.append(QStandardItem(QCoreApplication.translate("MonitorWindow", "Method return", "Message type")))
            case jeepney.MessageType.error:
                row.append(QStandardItem(QCoreApplication.translate("MonitorWindow", "Error", "Message type")))
            case jeepney.MessageType.signal:
                row.append(QStandardItem(QCoreApplication.translate("MonitorWindow", "Signal", "Message type")))
            case _:
                row.append(QStandardItem(QCoreApplication.translate("MonitorWindow", "Unknown", "Message type")))

        for i in (jeepney.HeaderFields.sender, jeepney.HeaderFields.destination, jeepney.HeaderFields.path, jeepney.HeaderFields.interface, jeepney.HeaderFields.member, jeepney.HeaderFields.signature):
            row.append(QStandardItem(self._header[i]))

        row.append(QStandardItem(self._body))

        return row


class MonitorWorker(QObject):
    new_message = pyqtSignal(_Message)
    error_message = pyqtSignal(str)

    def setup(self, connection: "Connection") -> str | None:
        self._parent_connection = connection

        match connection.connection_type:
            case "session":
                bus = "SESSION"
            case "system":
                bus = "SYSTEM"
            case "custom":
                bus = connection.custom_address

        try:
            self._connection = jeepney.io.blocking.open_dbus_connection(bus=bus)
        except Exception as ex:
            return str(ex)

        address = jeepney.DBusAddress(
            bus_name="org.freedesktop.DBus",
            object_path="/org/freedesktop/DBus",
            interface="org.freedesktop.DBus.Monitoring",
        )

        req = jeepney.new_method_call(address, "BecomeMonitor", "asu", ([], 0))
        rep = self._connection.send_and_get_reply(req)
        if rep.header.message_type == jeepney.MessageType.error:
            return rep.body[0]

        return None

    def set_message_filter(self, message_filter: _MessageFilter) -> None:
        self._message_filter = message_filter

    def close_thread(self) -> None:
        self._exit = True

    def run(self) -> None:
        self._exit = False

        while True:
            if self._exit:
                return

            try:
                msg = _Message(self._connection.receive())
            except ConnectionResetError:
                error_message = self.setup(self._parent_connection)
                if error_message is not None:
                    self.error_message.emit(error_message)
                    return
                continue
            except Exception as ex:
                print(ex, file=sys.stderr)
                continue

            if self._exit:
                return

            if msg.check_message_filter(self._message_filter):
                self.new_message.emit(msg)



class MonitorWindow(QWidget, Ui_MonitorWindow):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()

        self.setupUi(self)

        self._main_window = main_window

        self._model = QStandardItemModel(0, 8)
        self.table_view.setModel(self._model)

        self._model.setHorizontalHeaderLabels([
            QCoreApplication.translate("MonitorWindow", "Type", "Table Header"),
            QCoreApplication.translate("MonitorWindow", "Sender", "Table Header"),
            QCoreApplication.translate("MonitorWindow", "Destination", "Table Header"),
            QCoreApplication.translate("MonitorWindow", "Path", "Table Header"),
            QCoreApplication.translate("MonitorWindow", "Interface", "Table Header"),
            QCoreApplication.translate("MonitorWindow", "Member", "Table Header"),
            QCoreApplication.translate("MonitorWindow", "Signature", "Table Header"),
            QCoreApplication.translate("MonitorWindow", "Body", "Table Header"),
        ])

        self.clear_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_LineEditClearButton)))
        self.ok_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)))

        self.sender_edit.textChanged.connect(self._update_message_filter)
        self.destination_edit.textChanged.connect(self._update_message_filter)
        self.path_edit.textChanged.connect(self._update_message_filter)
        self.interface_edit.textChanged.connect(self._update_message_filter)
        self.member_edit.textChanged.connect(self._update_message_filter)
        self.signature_edit.textChanged.connect(self._update_message_filter)

        self.type_method_call_check_box.stateChanged.connect(self._update_message_filter)
        self.type_method_return_check_box.stateChanged.connect(self._update_message_filter)
        self.type_error_check_box.stateChanged.connect(self._update_message_filter)
        self.type_signal_check_box.stateChanged.connect(self._update_message_filter)

        self.clear_button.clicked.connect(lambda: self._model.setRowCount(0))
        self.ok_button.clicked.connect(self.close)

    def _get_message_filter(self) -> _MessageFilter:
        message_filter = _MessageFilter()

        message_filter.sender = self.sender_edit.text().strip()
        message_filter.destination = self.destination_edit.text().strip()
        message_filter.path = self.path_edit.text().strip()
        message_filter.interface = self.interface_edit.text().strip()
        message_filter.member = self.member_edit.text().strip()
        message_filter.signature = self.signature_edit.text().strip()

        if self.type_method_call_check_box.isChecked():
            message_filter.message_types.append(jeepney.MessageType.method_call)

        if self.type_method_return_check_box.isChecked():
            message_filter.message_types.append(jeepney.MessageType.method_return)


        if self.type_error_check_box.isChecked():
            message_filter.message_types.append(jeepney.MessageType.error)


        if self.type_signal_check_box.isChecked():
            message_filter.message_types.append(jeepney.MessageType.signal)

        return message_filter

    def _update_message_filter(self) -> None:
        self._worker.set_message_filter(self._get_message_filter())

    def _new_message(self, msg: _Message) -> None:
        self._model.appendRow(msg.get_row())
        self.table_view.scrollToBottom()

    def _error_message(self, error_message: str) -> None:
        QMessageBox.critical(
            self,
            QCoreApplication.translate("MonitorWindow", "Error"),
            QCoreApplication.translate("MonitorWindow", "Lost monitor session") + "<br><br>" + error_message,
        )
        self.close()

    def _start(self) -> None:
        self._thread = QThread()
        self._worker = MonitorWorker()

        self._worker.moveToThread(self._thread)
        self._worker.set_message_filter(self._get_message_filter())

        self._thread.started.connect(self._worker.run)
        self._worker.new_message.connect(self._new_message)

        self._thread.start()

    def open_window(self) -> None:
        self._thread = QThread()
        self._worker = MonitorWorker()

        self._worker.moveToThread(self._thread)

        connection = self._main_window.get_current_central_widget().connection
        error_message = self._worker.setup(connection)
        if error_message is not None:
            QMessageBox.critical(
                self._main_window,
                QCoreApplication.translate("MonitorWindow", "Error"),
                QCoreApplication.translate("MonitorWindow", "Could not start monitor session") + "<br><br>" + error_message,
            )
            return

        self._worker.set_message_filter(self._get_message_filter())

        self._thread.started.connect(self._worker.run)
        self._worker.new_message.connect(self._new_message)
        self._worker.error_message.connect(self._error_message)

        self._thread.start()

        match connection.connection_type:
            case "session":
                self.setWindowTitle(QCoreApplication.translate("MonitorWindow", "Monitor Session"))
            case "system":
                self.setWindowTitle(QCoreApplication.translate("MonitorWindow", "Monitor System"))
            case "custom":
                self.setWindowTitle(QCoreApplication.translate("MonitorWindow", "Monitor {{name}}").replace("{{name}}", connection.connection.name()))

        self.show()

    def closeEvent(self, event: QCloseEvent | None) -> None:
        self._worker.close_thread()

        # Send a signal to exit receive()
        signal = QDBusMessage.createSignal("/", "page.codeberg.JakobDev.jdDBusDebugger", "StopMonitor")
        self._main_window.get_current_central_widget().connection.connection.send(signal)

        self._thread.quit()
        self._thread.wait()

        return super().closeEvent(event)
