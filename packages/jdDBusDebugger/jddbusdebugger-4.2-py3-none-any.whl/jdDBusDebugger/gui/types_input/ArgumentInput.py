from PyQt6.QtWidgets import QWidget, QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QApplication, QStyle, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt, QCoreApplication
from ...types.DBusValue import DBusValue
from .InputHandler import InputHandler
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon


if TYPE_CHECKING:
    from ...types.Method import MethodArgument


class _TableColumns:
    NAME = 0
    TYPE = 1
    INPUT = 2


class ArgumentInput(QDialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self._ok = False
        self._input_handler = InputHandler()

        self._table_widget = QTableWidget(0, 3)

        for i in range(3):
            self._table_widget.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        ok_button = QPushButton(QCoreApplication.translate("ArgumentInput", "OK"))
        cancel_button = QPushButton(QCoreApplication.translate("ArgumentInput", "Cancel"))

        self._table_widget.setHorizontalHeaderLabels(("Name", "Type", "Input"))

        ok_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)))
        cancel_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)))

        ok_button.clicked.connect(self._ok_button_clicked)
        cancel_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._table_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.resize(400, 400)

    def _ok_button_clicked(self) -> None:
        self._ok = True
        self.close()

    def get_argument_values(self, name: str, arguments: list["MethodArgument"]) -> list[DBusValue] | None:
        self._ok = False

        for row, arg in enumerate(arguments):
            self._table_widget.insertRow(row)

            name_item = QTableWidgetItem(arg.name)
            name_item.setFlags(name_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self._table_widget.setItem(row, _TableColumns.NAME, name_item)

            type_item = QTableWidgetItem(arg.dbus_type.get_display_name())
            type_item.setFlags(type_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self._table_widget.setItem(row, _TableColumns.TYPE, type_item)

            self._table_widget.setCellWidget(row, _TableColumns.INPUT, self._input_handler.generate_widget_for_type(self, arg.dbus_type))

        self.setWindowTitle(
            QCoreApplication.translate("ArgumentInput", "Call {{name}}").replace("{{name}}", name),
        )

        self.exec()

        if not self._ok:
            return None

        return_list: list[DBusValue] = []

        for row, arg in enumerate(arguments):
            return_list.append(self._input_handler.get_value_from_widget(self._table_widget.cellWidget(row, _TableColumns.INPUT), arg.dbus_type))

        return return_list
