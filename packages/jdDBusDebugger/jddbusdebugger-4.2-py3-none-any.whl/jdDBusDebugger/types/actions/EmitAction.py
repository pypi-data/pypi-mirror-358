from typing import Type, Any, TYPE_CHECKING
from .ActionBase import ActionBase
from ..DBusValue import DBusValue
import subprocess


class EmitAction(ActionBase):
    def __init__(self) -> None:
        super().__init__()

        self.action_type = "emit"
        self.emit_path = ""
        self.emit_interface = ""
        self.emit_name = ""

        self.argument_list: list["DBusValue"] = []

    @classmethod
    def create(obj: Type["EmitAction"], path: str, interface: str, name: str, arguments: list["DBusValue"]) -> "EmitAction":
        action = obj()

        action.emit_path = path
        action.emit_interface = interface
        action.emit_name = name
        action.argument_list = arguments

        return action

    @classmethod
    def from_json_data(obj: Type["EmitAction"], data: dict[str, Any]) -> "EmitAction":
        action = obj()

        action.emit_path = data["emit_path"]
        action.emit_interface = data["emit_interface"]
        action.emit_name = data["emit_name"]

        for arg_data in data["arguments"]:
            action.argument_list.append(DBusValue.from_json_data(arg_data))

        return action

    def get_json_data(self) -> Any:
        arguments: list[dict[str, Any]] = []

        for arg in self.argument_list:
            arguments.append(arg.get_json_data())

        return {
            "action_type": self.action_type,
            "emit_path": self.emit_path,
            "emit_interface": self.emit_interface,
            "emit_name": self.emit_name,
            "arguments": arguments,
        }

    def get_qdbus_command(self) -> str:
        return "Not available"

    def get_gdbus_command(self) -> str:
        return "Not available"