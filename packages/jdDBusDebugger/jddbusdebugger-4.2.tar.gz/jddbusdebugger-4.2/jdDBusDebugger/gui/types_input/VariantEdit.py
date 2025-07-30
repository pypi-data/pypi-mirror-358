from PyQt6.QtWidgets import QWidget, QComboBox, QHBoxLayout
from ...types.DBusType import DBusTypeEnum, DBusType
from ...types.DBusValue import DBusValue
from .InputHandler import InputHandler
from typing import Any


class VariantEdit(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self._input_handler = InputHandler()

        self._type_box = QComboBox()

        self._input_handler = InputHandler()

        for dbus_type in DBusType.get_available_types():
            if dbus_type.type_const != DBusTypeEnum.VARIANT:
                self._type_box.addItem(dbus_type.get_display_name(), dbus_type)

        self._type_box.currentIndexChanged.connect(self._type_box_changed)

        self._main_layout = QHBoxLayout()
        self._main_layout.addWidget(self._type_box)
        self._main_layout.addWidget(self._input_handler.generate_widget_for_type(self, self._type_box.currentData()))

        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self._main_layout)

    def _type_box_changed(self) -> None:
        self._main_layout.takeAt(1).widget().setParent(None)
        self._main_layout.addWidget(self._input_handler.generate_widget_for_type(self, self._type_box.currentData()))

    def get_value(self) -> DBusValue:
        value = self._input_handler.get_value_from_widget(self._main_layout.itemAt(1).widget(), self._type_box.currentData())
        return DBusValue.create(DBusType.from_type_const(DBusTypeEnum.VARIANT), value.get_value())
