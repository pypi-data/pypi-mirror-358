from typing import TYPE_CHECKING, Any
from .ActionBase import ActionBase
from ..DBusValue import DBusValue
import subprocess
import copy


if TYPE_CHECKING:
    from ..DBusValue import DBusValue
    from ..Method import Method


class CallAction(ActionBase):
    def __init__(self) -> None:
        super().__init__()

        self.action_type = "call"
        self.method_name = ""

        self.parameter_list: list["DBusValue"] = []

    @classmethod
    def from_json_data(obj, data: dict[str, Any]) -> "CallAction":
        action = obj()

        action.service_name = data["service_name"]
        action.object_path = data["object_path"]
        action.interface_name = data["interface_name"]
        action.method_name = data["method_name"]

        for param_data in data["parameters"]:
            action.parameter_list.append(DBusValue.from_json_data(param_data))
        return action

    def get_json_data(self) -> Any:
        parameters: list[dict[str, Any]] = []

        for param in self.parameter_list:
            parameters.append(param.get_json_data())

        return {
            "action_type": self.action_type,
            "service_name": self.service_name,
            "object_path": self.object_path,
            "interface_name": self.interface_name,
            "method_name": self.method_name,
            "parameters": parameters
        }

    def get_dbus_send_command(self) -> str:
        command = ["dbus-send", "--print-reply", "--type=method_call", f"--dest={self.service_name}", self.object_path, f"{self.interface_name}.{self.method_name}"]

        for param in self.parameter_list:
            command += param.get_printable_text()

        return subprocess.list2cmdline(command)

    def get_qdbus_command(self) -> str:
        command = ["qdbus", self.service_name, self.object_path, f"{self.interface_name}.{self.method_name}"]

        for param in self.parameter_list:
            command += param.get_printable_text()

        return subprocess.list2cmdline(command)

    def get_gdbus_command(self) -> str:
        command = ["gdbus", "call", "--session", "--dest", self.service_name, "--object-path", self.object_path, "--method", f"{self.interface_name}.{self.method_name}"]
        return subprocess.list2cmdline(command)

    @classmethod
    def from_message(obj, method: "Method", arguments: list["DBusValue"]):
        action = obj()

        action.service_name = method.interface.service.name
        action.object_path = method.interface.object_path
        action.interface_name = method.interface.name
        action.method_name = method.name

        #action.parameter_list = copy.deepcopy(arguments)
        action.parameter_list = arguments

        return action
