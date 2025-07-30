from typing import TYPE_CHECKING
from .Property import Property
from .Signal import Signal
from .Method import Method
from lxml import etree


if TYPE_CHECKING:
    from .Service import Service


class Interface:
    def __init__(self) -> None:
        self.name = ""
        self.object_path = ""
        self.service: "Service" | None = None

        self.methods: list[Method] = []
        self.signals: list[Signal] = []
        self.properties: list[Property] = []

    @classmethod
    def from_xml(obj, service: "Service", object_path: str, element: etree._Element):
        interface = obj()
        interface.service = service
        interface.object_path = object_path
        interface.name = element.get("name")

        for method in element.findall("method"):
            interface.methods.append(Method.from_xml(interface, method))

        for property in element.findall("property"):
            interface.properties.append(Property.from_xml(interface, property))

        for signal in element.findall("signal"):
            interface.signals.append(Signal.from_xml(interface, signal))

        return interface

    def get_method_by_name(self, name: str) -> Method | None:
        for method in self.methods:
            if method.name == name:
                return method
        return None

    def get_property_by_name(self, name: str) -> Property | None:
        for prop in self.properties:
            if prop.name == name:
                return prop
        return None

    def get_signal_by_name(self, name: str) -> Signal | None:
        for signal in self.signals:
            if signal.name == name:
                return signal
        return None
