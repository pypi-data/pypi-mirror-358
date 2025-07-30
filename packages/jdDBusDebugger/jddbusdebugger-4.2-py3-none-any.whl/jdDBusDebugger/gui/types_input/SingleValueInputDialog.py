from PyQt6.QtWidgets import QDialog, QWidget, QPushButton, QMessageBox, QApplication, QStyle, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QCoreApplication
from ...types.DBusValue import DBusValue
from .InputHandler import InputHandler
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon


if TYPE_CHECKING:
    from ...types.DBusType import DBusType


class SingleValueInputDialog(QDialog):
    def __init__(self, parent: QWidget | None, dbus_type: "DBusType") -> None:
        super().__init__(parent)

        self._ok = False
        self._dbus_type = dbus_type
        self._input_handler = InputHandler()

        self._input_widget = self._input_handler.generate_widget_for_type(self, dbus_type)
        ok_button = QPushButton(QCoreApplication.translate("SingleValueInputDialog", "OK"))
        cancel_button = QPushButton(QCoreApplication.translate("SingleValueInputDialog", "Cancel"))

        ok_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)))
        cancel_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)))

        ok_button.clicked.connect(self._ok_button_clicked)
        cancel_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._input_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowTitle(QCoreApplication.translate("SingleValueInputDialog", "Enter value"))

    def _ok_button_clicked(self) -> None:
        validation_error = self._input_handler.get_validation_error(self._input_widget, self._dbus_type)
        if validation_error is not None:
            QMessageBox.critical(self, QCoreApplication.translate("SingleValueInputDialog", "Invalid data"), validation_error)
            return

        self._ok = True

        self.close()

    def open_input_dialog(self, current_value: DBusValue | None = None) -> tuple[DBusValue | None, bool]:
        self._ok = False

        if current_value is not None:
            self._input_handler.set_widget_value(self._input_widget, self._dbus_type, current_value)

        self.exec()

        if not self._ok:
            return None, False

        return self._input_handler.get_value_from_widget(self._input_widget, self._dbus_type), True
