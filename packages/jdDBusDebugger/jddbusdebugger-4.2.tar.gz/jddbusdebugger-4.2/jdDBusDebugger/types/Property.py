from PyQt6.QtDBus import QDBusMessage, QDBusVariant
from ..Functions import format_dbus_error
from typing import Any, TYPE_CHECKING
from .DBusValue import DBusValue
from .DBusType import DBusType
from lxml import etree


if TYPE_CHECKING:
    from .Interface import Interface


class Property:
    def __init__(self) -> None:
        self.name = ""
        self.read_access = True
        self.write_access = False
        self.dbus_type: DBusType | None = None
        self.interface: "Interface" | None = None

    @classmethod
    def from_xml(obj, interface: "Interface", element: etree._Element):
        prop = obj()
        prop.interface = interface

        prop.name = element.get("name")
        prop.dbus_type = DBusType.from_type_text(element.get("type"))

        match element.get("access", "readwrite"):
            case "readwrite":
                prop.read_access = True
                prop.write_access = True
            case "read":
                prop.read_access = True
                prop.write_access = False
            case "write":
                prop.read_access = False
                prop.write_access = True

        return prop

    def get_value(self) -> tuple[DBusValue | None, str | None]:
        msg= QDBusMessage.createMethodCall(self.interface.service.name, self.interface.object_path, "org.freedesktop.DBus.Properties", "Get")
        msg.setArguments((self.interface.name, self.name))
        result = self.interface.service.connection.connection.call(msg)

        if result.errorMessage() == "":
            return DBusValue.create(self.dbus_type, result.arguments()[0]), None
        else:
            return None, result.errorMessage()

    def set_value(self, value: Any) -> str | None:
        msg= QDBusMessage.createMethodCall(self.interface.service.name, self.interface.object_path, "org.freedesktop.DBus.Properties", "Set")
        msg.setArguments((self.interface.name, self.name, QDBusVariant(value)))
        result = self.interface.service.connection.connection.call(msg)
        if result.errorName() == "":
            return None
        else:
            return format_dbus_error(result)
