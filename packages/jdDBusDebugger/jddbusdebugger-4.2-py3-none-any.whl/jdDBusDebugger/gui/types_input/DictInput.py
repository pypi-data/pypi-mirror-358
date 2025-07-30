from PyQt6.QtWidgets import QWidget, QDialog, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QMessageBox, QApplication, QStyle, QHBoxLayout, QVBoxLayout
from ...Functions import get_table_widget_sender_row
from PyQt6.QtCore import QCoreApplication
from ...types.DBusType import DBusType
from .InputHandler import InputHandler
from PyQt6.QtGui import QCloseEvent
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon


if TYPE_CHECKING:
    from ...types.DBusValue import DBusValue


class _DictInputTableColumns:
    KeyName = 0
    ValueType = 1
    ValueContent = 2
    Remove = 3


class DictInputDialog(QDialog):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self._input_handler = InputHandler()

        self._dict_input_table = QTableWidget(0, 4)
        add_row_button = QPushButton(QCoreApplication.translate("DictInput", "Add"))
        ok_button = QPushButton(QCoreApplication.translate("DictInput", "OK"))

        self._dict_input_table.setHorizontalHeaderLabels((QCoreApplication.translate("DictInput", "Key"), QCoreApplication.translate("DictInput", "Type"), QCoreApplication.translate("DictInput", "Value"), QCoreApplication.translate("DictInput", "Remove")))

        add_row_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        ok_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)))

        add_row_button.clicked.connect(self._add_row_button_clicked)
        ok_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(ok_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._dict_input_table)
        main_layout.addWidget(add_row_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setWindowTitle(QCoreApplication.translate("DictInput", "Edit Dictionary"))

    def _get_type_combo_box(self) -> QComboBox:
        box = QComboBox()
        for dbus_type in DBusType.get_available_types():
            box.addItem(dbus_type.get_display_name(), dbus_type)
        return box

    def _value_type_box_changed(self) -> None:
        type_box: QComboBox = self.sender()

        row = get_table_widget_sender_row(self._dict_input_table, _DictInputTableColumns.ValueType, type_box)

        self._dict_input_table.setCellWidget(row, _DictInputTableColumns.ValueContent, self._input_handler.generate_widget_for_type(self, type_box.currentData()))

    def _remove_button_clicked(self) -> None:
        row = get_table_widget_sender_row(self._dict_input_table, _DictInputTableColumns.Remove, self.sender())
        self._dict_input_table.removeRow(row)

    def _add_row_button_clicked(self) -> None:
        row = self._dict_input_table.rowCount()
        self._dict_input_table.insertRow(row)

        self._dict_input_table.setItem(row, _DictInputTableColumns.KeyName, QTableWidgetItem())

        value_type_box = self._get_type_combo_box()
        value_type_box.currentIndexChanged.connect(self._value_type_box_changed)
        self._dict_input_table.setCellWidget(row, _DictInputTableColumns.ValueType, value_type_box)

        self._dict_input_table.setCellWidget(row, _DictInputTableColumns.ValueContent, self._input_handler.generate_widget_for_type(self, value_type_box.currentData()))

        remove_button = QPushButton(QCoreApplication.translate("DictInput", "Remove"))
        remove_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListRemove))
        remove_button.clicked.connect(self._remove_button_clicked)
        self._dict_input_table.setCellWidget(row, _DictInputTableColumns.Remove, remove_button)

    def get_validation_error(self) -> str | None:
        existing_keys: dict[str, bool] = {}

        for row in range(self._dict_input_table.rowCount()):
            key = self._dict_input_table.item(row, _DictInputTableColumns.KeyName).text()

            if key == "":
                return QCoreApplication.translate("DictInput", "The key must not be empty")

            if key in existing_keys:
                return QCoreApplication.translate("DictInput", "The key {{key}} appears more than once").replace("{{key}}", key)

            value_type = self._dict_input_table.cellWidget(row, _DictInputTableColumns.ValueType).currentData()
            validation_error = self._input_handler.get_validation_error(self._dict_input_table.cellWidget(row, _DictInputTableColumns.ValueContent), value_type)
            if validation_error is not None:
                return validation_error

        return None

    def get_dict(self) -> dict[str, "DBusValue"]:
        input_dict = {}

        for row in range(self._dict_input_table.rowCount()):
            value_type = self._dict_input_table.cellWidget(row, _DictInputTableColumns.ValueType).currentData()
            input_dict[self._dict_input_table.item(row, _DictInputTableColumns.KeyName).text()] = self._input_handler.get_value_from_widget(self._dict_input_table.cellWidget(row, _DictInputTableColumns.ValueContent), value_type)

        return input_dict

    def closeEvent(self, event: QCloseEvent) -> None:
        err = self.get_validation_error()

        if err is None:
            event.accept()
        else:
            QMessageBox.critical(self, QCoreApplication.translate("DictInput", "Data invalid"), QCoreApplication.translate("DictInput", "Your data is not valid") + "<br><br>" + err)
            event.ignore()


class EditDictButton(QPushButton):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(QCoreApplication.translate("DictInput", "Edit Dict"))

        self._dict_input_dialog = DictInputDialog(parent)

        self.clicked.connect(lambda: self._dict_input_dialog.open())

    def get_dict(self) -> dict[str, "DBusValue"]:
        return self._dict_input_dialog.get_dict()
