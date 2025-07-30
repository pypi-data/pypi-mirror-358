from ..ui_compiled.GenerateScriptDialog import Ui_GenerateScriptDialog
from PyQt6.QtWidgets import QDialog
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..types.actions.ActionBase import ActionBase


class GenerateScriptDialog(QDialog, Ui_GenerateScriptDialog):
    def __init__(self) -> None:
        super().__init__()

        self.setupUi(self)

        self._actions: list["ActionBase"] = []

        # self.program_box.addItem("qdbus", "dbus-send")
        self.program_box.addItem("qdbus", "qdbus")
        self.program_box.addItem("gdbus", "gdbus")

        self.program_box.currentIndexChanged.connect(self._update_script)
        self.ok_button.clicked.connect(self.close)

    def _update_script(self):
        self.script_edit.clear()

        match  self.program_box.currentData():
            case "dbus-send":
                func = "get_dbus_send_command"
            case "qdbus":
                func = "get_qdbus_command"
            case "gdbus":
                func = "get_gdbus_command"
            case _:
                return

        command_list: list[str] = []

        for action in self._actions:
            command_list.append(getattr(action, func)())

        text = ""

        for command in command_list:
            text += command + "\n"

        self.script_edit.setPlainText(text)


    def open_dialog(self, actions: list["ActionBase"]) -> None:
        self._actions = actions

        self._update_script()

        self.exec()
