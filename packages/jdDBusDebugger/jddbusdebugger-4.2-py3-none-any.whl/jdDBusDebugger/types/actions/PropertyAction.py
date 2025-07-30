from typing import Literal, Any, TYPE_CHECKING
from .ActionBase import ActionBase
from ..DBusValue import DBusValue
import subprocess


if TYPE_CHECKING:
    from ..Property import Property


class PropertyAction(ActionBase):
    def __init__(self) -> None:
        super().__init__()

        self.action_type = "property"
        self.property_method: Literal["get", "set"] = ""
        self.property_name = ""
        self.property_value: "DBusValue" | None = None


    @classmethod
    def from_property(obj, prop: "Property", prop_method: Literal["get", "set"], value: DBusValue | None) -> "PropertyAction":
        action = obj()

        action.service_name = prop.interface.service.name
        action.object_path = prop.interface.object_path
        action.interface_name = prop.interface.name
        action.property_name = prop.name
        action.property_method = prop_method
        action.property_value = value

        return action

    @classmethod
    def from_json_data(obj, data: dict[str, Any]) -> "PropertyAction":
        action = obj()

        action.service_name = data["service_name"]
        action.object_path = data["object_path"]
        action.interface_name = data["interface_name"]
        action.property_name = data["property_name"]
        action.property_method = data["property_method"]

        if data["property_value"] is not None:
            action.property_value = DBusValue.from_json_data(data["property_value"])

        return action

    def get_json_data(self) -> Any:
        if self.property_value is not None:
            json_value = self.property_value.get_json_data()
        else:
            json_value = None

        return {
            "action_type": self.action_type,
            "service_name": self.service_name,
            "object_path": self.object_path,
            "interface_name": self.interface_name,
            "property_name": self.property_name,
            "property_method": self.property_method,
            "property_value": json_value
        }

    def get_qdbus_command(self) -> str:
        if self.property_method == "get":
            command = ["qdbus", self.service_name, self.object_path, "org.freedesktop.DBus.Properties.Get", self.interface_name, self.property_name]
        else:
            command = ["qdbus", self.service_name, self.object_path, "org.freedesktop.DBus.Properties.Set", self.interface_name, self.property_name, self.property_value.get_printable_text()]

        return subprocess.list2cmdline(command)

    def get_gdbus_command(self) -> str:
        if self.property_method == "get":
            command = ["gdbus", "call", "--session", "--dest", self.service_name, "--object-path", self.object_path, "--method", "org.freedesktop.DBus.Properties.Get", self.interface_name, self.property_name]
        else:
            return "Not available"

        return subprocess.list2cmdline(command)
