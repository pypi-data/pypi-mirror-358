from ..core.UnixUserDatabase import UnixUserDatabase
from PyQt6.QtDBus import QDBusMessage
from typing import TYPE_CHECKING
from .Interface import Interface
from lxml import etree
import traceback
import sys
import io
import os


if TYPE_CHECKING:
    from .Connection import Connection


class Service:
    def __init__(self, connection : "Connection", name: str, activatable: bool) -> None:
        self.connection = connection

        self.name = name
        self.activatable = activatable
        self.pid: int | None = None
        self.process_name: str | None = None
        self.user_name: str | None = None

        self.objects: dict[str, list[Interface]] = {}

        self.is_loaded = False

        self._update_data()

    def _update_data(self) -> None:
        pid_message = QDBusMessage.createMethodCall("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", "GetConnectionUnixProcessID")
        pid_message.setArguments([self.name])
        pid_result = self.connection.connection.call(pid_message)
        if pid_result.errorName() == "":
            self.pid = pid_result.arguments()[0]

        user_message = QDBusMessage.createMethodCall("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", "GetConnectionUnixUser")
        user_message.setArguments([self.name])
        user_result = self.connection.connection.call(user_message)
        if user_result.errorName() == "":
            uid = user_result.arguments()[0]
            self.user_name = UnixUserDatabase.get_database().get_user_name(uid)

    def _introspect_node(self, parent_path: str, name: str, error_list: list[str]) -> None:
        current_path = parent_path.removesuffix("/") + "/" + name

        message = QDBusMessage.createMethodCall(self.name, current_path, "org.freedesktop.DBus.Introspectable", "Introspect")
        result = self.connection.connection.call(message)

        if result.errorName() != "":
            if result.errorMessage() == "":
                error_list.append(result.errorName())
            else:
                error_list.append(f"{result.errorName()}: {result.errorMessage()}")
            return

        if len(result.arguments()) != 1 or not isinstance(result.arguments()[0], str):
            error_list.append("Introspect has wrong return type")
            return

        xml_string: str = result.arguments()[0]

        try:
            root = etree.parse(io.BytesIO(xml_string.encode("utf-8")))

            self.objects[current_path] = []
            for interface_element in root.findall("interface"):
                inter = Interface.from_xml(self, current_path, interface_element)
                self.objects[current_path].append(inter)

            for child_node in root.findall("node"):
                self._introspect_node(current_path, child_node.get("name"), error_list)
        except Exception as ex:
            error_list.append(f"Failed to parse Introspect XML: {ex}")
            print(traceback.format_exc(), file=sys.stderr)

    def add_object_path(self, object_path: str) -> tuple[list[Interface] | None, list[str]]:
        error_list: list[str] = []
        self._introspect_node(os.path.dirname(object_path), os.path.basename(object_path), error_list)
        return self.objects.get(object_path), error_list

    def load(self) -> list[str]:
        error_list: list[str] = []
        self._introspect_node("", "", error_list)
        self.is_loaded = True
        return error_list

    def get_interface_by_name(self, object_path: str, name: str) -> Interface | None:
        if object_path not in self.objects:
            return None

        for interface in self.objects[object_path]:
            if interface.name == name:
                return interface

        return None
