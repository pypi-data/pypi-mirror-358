from ..Functions import format_dbus_error, is_flatpak, get_all_processes
from PyQt6.QtCore import QObject, QCoreApplication, QProcess
from PyQt6.QtDBus import QDBusConnection, QDBusMessage
from ..core.UnixUserDatabase import UnixUserDatabase
from typing import Literal, Type, Optional
from ..Constants import SERVER_CONSTANTS
from .Service import Service
import tempfile
import getpass
import time
import os


class Connection(QObject):
    def __init__(self, connection: QDBusConnection, connection_type: Literal["session", "system", "custom"]) -> None:
        super().__init__()

        self.connection_type = connection_type
        self.connection = connection

        self.custom_address = ""
        self.custom_name = ""

        self._error_message: str | None = None

        self.service_list: list[Service] = []

        self.reload_services()

    @classmethod
    def new_session_connection(cls: Type["Connection"]) -> "Connection":
        return cls(QDBusConnection.sessionBus(), "session")

    @classmethod
    def new_system_connection(cls: Type["Connection"]) -> "Connection":
        return cls(QDBusConnection.systemBus(), "system")

    @classmethod
    def new_custom_connection(cls: Type["Connection"], address: str, name: str) -> "Connection":
        conn = cls(QDBusConnection.connectToBus(address, name), "custom")
        conn.custom_address = address
        conn.custom_name = name
        return conn

    @classmethod
    def new_accessibility_connection(cls: Type["Connection"]) -> Optional["Connection"]:
        msg = QDBusMessage.createMethodCall("org.a11y.Bus", "/org/a11y/bus", "org.a11y.Bus", "GetAddress")
        result = QDBusConnection.sessionBus().call(msg)

        if result.errorName() != "":
            return None

        return cls.new_custom_connection(result.arguments()[0], QCoreApplication.translate("Connection", "Accessibility"))

    @classmethod
    def new_process_connection(cls: Type["Connection"], pid: str, bus: Literal["session", "system", "flatpak-accessibility"], name: str) -> "Connection":
        match bus:
            case "session":
                socket_path = os.path.join("/proc", pid, "root", "run", "user", str(os.getuid()), "bus")
            case "system":
                socket_path = os.path.join("/proc", pid, "root", "var", "run", "dbus", "system_bus_socket ")
            case "flatpak-accessibility":
                socket_path = os.path.join("/proc", pid, "root", "run", "flatpak", "at-spi-bus")
            case _:
                raise ValueError("Invalid bus")

        conn = cls(QDBusConnection(""), "custom")
        conn.custom_name = name

        if is_flatpak():
            conn._socket_path = tempfile.mktemp(prefix="jddbusdebugger_proxy_")
            conn._process = QProcess(conn)
            conn._process.start("flatpak-spawn", ["--host", "xdg-dbus-proxy", f"unix:path={socket_path}", conn._socket_path])
            conn._process.waitForStarted()
            conn._process.waitForStarted()
            time.sleep(1)
            connect_path = conn._socket_path
        else:
            connect_path = socket_path

        conn.connection = QDBusConnection.connectToBus(f"unix:path={connect_path}", name)
        conn.custom_address = f"unix:path={connect_path}"
        conn._error_message = None
        conn.reload_services()

        return conn

    @classmethod
    def new_server_connection(cls: Type["Connection"], ip: str, name: str) -> "Connection":
        conn = cls(QDBusConnection(""), "custom")
        conn._process = QProcess(conn)

        conn._socket_path = tempfile.mktemp(prefix="jddbusdebugger_server_")
        conn._process.start("socat", [f"UNIX-LISTEN:{conn._socket_path},fork,reuseaddr,unlink-early,user={getpass.getuser()},group={getpass.getuser()},mode=770", f"TCP:{ip}:{SERVER_CONSTANTS.SOCAT_PORT}"])
        conn._process.waitForStarted()

        time.sleep(1)

        conn.connection = QDBusConnection.connectToBus(f"unix:path={conn._socket_path}", name)
        conn.custom_address = f"unix:path={conn._socket_path}"
        conn._error_message = None
        conn.custom_name = name
        conn.reload_services()

        return conn

    def is_connected(self) -> bool:
        msg = QDBusMessage.createMethodCall("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", "GetId")
        result = self.connection.call(msg)
        return result.errorName() == ""

    def reload_services(self) -> None:
        self.service_list.clear()

        activatable_message = QDBusMessage.createMethodCall("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", "ListActivatableNames")
        activatable_result = self.connection.call(activatable_message)

        if activatable_result.errorName() != "":
            self._error_message = format_dbus_error(activatable_result)
            return

        activatable_list: list[str] = activatable_result.arguments()[0]

        name_message = QDBusMessage.createMethodCall("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", "ListNames")
        name_result = self.connection.call(name_message)

        if name_result.errorMessage() != "":
            self._error_message = format_dbus_error(name_message)
            return

        name_list: list[str] = name_result.arguments()[0]

        connection_names: list[str] = []
        all_services: list[str] = []

        for i in activatable_list:
            all_services.append(i)

        for i in name_list:
            if i not in all_services:
                if i.startswith(":"):
                    connection_names.append(i)
                else:
                    all_services.append(i)

        connection_names.sort()
        all_services.sort()

        all_services += connection_names

        process_dict = get_all_processes()

        for i in all_services:
            service = Service(self, i, i in activatable_list)

            if service.pid is not None and service.pid in process_dict:
                service.process_name = process_dict[service.pid]

            self.service_list.append(service)

    def get_service_by_name(self, name: str) -> Service | None:
        for service in self.service_list:
            if service.name == name:
                return service
        return None

    def get_error_message(self) -> str | None:
        return self._error_message

    def get_name(self) -> str:
        match self.connection_type:
            case "session":
                return QCoreApplication.translate("Connection", "Session")
            case "system":
                return QCoreApplication.translate("Connection", "System")
            case "custom":
                return self.custom_name

    def get_address(self) -> str:
        match self.connection_type:
            case "session":
                return os.getenv("DBUS_SESSION_BUS_ADDRESS") or ""
            case "system":
                return os.getenv("DBUS_SYSTEM_BUS_ADDRESS") or "unix:path=/var/run/dbus/system_bus_socket"
            case "custom":
                return self.custom_address

    def get_information(self) -> tuple[dict[str, str] | None, str | None]:
        credentials_message = QDBusMessage.createMethodCall("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", "GetConnectionCredentials")
        credentials_message.setArguments([self.connection.baseService()])
        credentials_result = self.connection.call(credentials_message)

        if credentials_result.errorName() != "":
            return None, format_dbus_error(credentials_result)

        credentials_dict = credentials_result.arguments()[0]

        return {
            "unique_name": self.connection.baseService(),
            "pid": str(credentials_dict["ProcessID"]),
            "uid": str(credentials_dict["UnixUserID"]),
            "user_name": UnixUserDatabase().get_database().get_user_name(credentials_dict["UnixUserID"]),
        }, None

    def close(self) -> None:
        try:
            self._process.kill()
            os.remove(self._socket_path)
        except Exception:
            pass
