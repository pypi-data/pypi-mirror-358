from PyQt6.QtDBus import QDBusMessage
from typing import TYPE_CHECKING
from .DBusType import DBusType
from lxml import etree


if TYPE_CHECKING:
    from .Interface import Interface


class Signal:
    def __init__(self) -> None:
        self.name = ""
        self.is_connected = False
        self.interface: "Interface" | None = None
        self.types: list[DBusType] = []

    def get_id(self) -> str:
        return "{self.interface.service.name}#{self.interface.object_path}#{self.interface.name}#{self.name}"

    @classmethod
    def from_xml(obj, interface: "Interface", element: etree._Element):
        signal = obj()
        signal.interface = interface

        signal.name = element.get("name")

        for arg in element.findall("arg"):
            signal.types.append(DBusType.from_type_text(arg.get("type")))

        return signal
