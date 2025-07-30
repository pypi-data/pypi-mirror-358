from PyQt6.QtDBus import QDBusMessage
from typing import TYPE_CHECKING
from .DBusType import DBusType
from lxml import etree


if TYPE_CHECKING:
    from .Interface import Interface


class MethodArgument:
    def __init__(self, name: str, dbus_type: str) -> None:
        self.name = name
        self.dbus_type = DBusType.from_type_text(dbus_type)


class Method:
    def __init__(self) -> None:
        self.name = ""
        self.interface: "Interface" | None = None
        self.arguments: list[MethodArgument] = []
        self.return_types: list[DBusType] = []

    @classmethod
    def from_xml(obj, interface: "Interface", element: etree._Element):
        method = obj()
        method.interface = interface

        method.name = element.get("name")

        for arg in element.findall("arg"):
            match arg.get("direction"):
                case "in":
                    method.arguments.append(MethodArgument(arg.get("name", "Unknown"), arg.get("type")))
                case "out":
                    method.return_types.append(DBusType.from_type_text(arg.get("type")))

        return method

    def get_method_call(self) -> QDBusMessage:
        return QDBusMessage.createMethodCall(self.interface.service.name, self.interface.object_path, self.interface.name, self.name)
