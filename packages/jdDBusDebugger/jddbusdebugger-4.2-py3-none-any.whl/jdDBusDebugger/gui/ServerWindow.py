from PyQt6.QtWidgets import QDialog, QApplication, QStyle
from ..ui_compiled.ServerWindow import Ui_ServerWindow
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtCore import QCoreApplication
from ..Functions import check_socat
from ..core.Server import Server
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .MainWindow import MainWindow


class ServerWindow(QDialog, Ui_ServerWindow):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)

        self.setupUi(self)

        self._main_window = main_window

        self._server = Server(main_window.get_current_connection())

        self.close_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton)))

        self.start_stop_button.clicked.connect(self._start_stop_button_clicked)
        self.close_button.clicked.connect(self.close)

    def _start_stop_button_clicked(self) -> None:
        if self._server.is_running():
            self._server.stop()
            self.start_stop_button.setText(QCoreApplication.translate("ServerWindow", "Start"))
        else:
            self._server.start()
            self.start_stop_button.setText(QCoreApplication.translate("ServerWindow", "Stop"))

    def open_window(self) -> None:
        if not check_socat(self._main_window):
            return

        self.exec()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._server.is_running():
            self._server.stop()

        event.accept()
