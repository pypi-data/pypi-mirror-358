from PyQt6.QtWidgets import QDialog, QApplication, QStyle, QFormLayout
from ..ui_compiled.EmitSignalDialog import Ui_EmitSignalDialog
from .types_input.StructInput import EditStructButton
from ..types.actions.EmitAction import EmitAction
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon


if TYPE_CHECKING:
    from .MainWindow import MainWindow


class EmitSignalDialog(QDialog, Ui_EmitSignalDialog):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)

        self.setupUi(self)

        self._main_window = main_window
        self._edit_struct_button = EditStructButton()

        self.ok_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)))
        self.cancel_button.setIcon(QIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)))

        self.ok_button.clicked.connect(self._ok_button_clicked)
        self.cancel_button.clicked.connect(self.close)

        self.form_layout.setWidget(3, QFormLayout.ItemRole.FieldRole, self._edit_struct_button)

    def _ok_button_clicked(self) -> None:
        action = EmitAction.create(self.path_edit.text(), self.interface_edit.text(), self.name_edit.text(), self._edit_struct_button.get_struct())

        self._main_window.get_current_central_widget().execute_action(action)
        self._main_window.macro_manager.record_action(action)

        self.close()

    def open_dialog(self) -> None:
        self.open()