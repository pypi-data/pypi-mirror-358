from PyQt6.QtDBus import QDBusVariant, QDBusArgument, QDBusUnixFileDescriptor, QDBusObjectPath
from .DBusType import DBusTypeEnum, DBusType
from PyQt6.QtCore import QByteArray
from .EnumHelper import EnumHelper
from typing import Any


class BytearraySource(EnumHelper):
    STRING = "string"
    FILE = "file"


class DBusValue:
    def __init__(self) -> None:
        self.dbus_type = DBusType()
        self.value: Any = None

    @classmethod
    def create(cls: type["DBusValue"], dbus_type: DBusType, value: Any) -> "DBusValue":
        dbus_value = cls()

        dbus_value.dbus_type = dbus_type
        dbus_value.value = value

        return dbus_value

    @classmethod
    def from_json_data(obj, json_data: dict[str, Any]) -> "DBusValue":
        dbus_value = obj()

        dbus_value.dbus_type= DBusType.from_json_data(json_data["type"])

        match dbus_value.dbus_type.type_const:
            case DBusTypeEnum.DICT:
                dbus_value.value = {}
                for key, value in json_data["value"].items():
                    dbus_value.value[key] = obj.from_json_data(value)
            case _:
                dbus_value.value = json_data["value"]

        return dbus_value

    def get_json_data(self) -> dict[str, Any]:
        match self.dbus_type.type_const:
            case DBusTypeEnum.DICT:
                json_value = {}
                for key, value in self.value.items():
                    json_value[key] = value.get_json_data()
            case _:
                json_value = self.value

        return {
            "type": self.dbus_type.get_json_data(),
            "value": json_value
        }

    def get_value(self) -> Any:
        if self.dbus_type.is_simple_type():
            arg = QDBusArgument()
            arg.add(self.value, self.dbus_type.get_qmeta_type().id())
            return arg

        match self.dbus_type.type_const:
            case DBusTypeEnum.VARIANT:
                return QDBusVariant(self.value)
            case DBusTypeEnum.ARRAY:
                arg = QDBusArgument()
                arg.beginArray(self.dbus_type.array_type.get_qmeta_type())
                for value in self.value:
                    arg.add(value.get_value())
                arg.endArray()
                return arg
            case DBusTypeEnum.DICT:
                return_dict = {}
                for key, value in self.value.items():
                    return_dict[key] = value.get_value()
                return return_dict
            case DBusTypeEnum.STRUCT:
                arg = QDBusArgument()
                arg.beginStructure()
                for current_value in self.value:
                    arg.add(current_value.get_value())
                arg.endStructure()
                return arg
            case DBusTypeEnum.FILE_HANDLE:
                try:
                    f = open(self.value, "rb")
                    return QDBusUnixFileDescriptor(f.fileno())
                except Exception:
                    return None
            case DBusTypeEnum.BYTE_ARRAY:
                match self.value["type"]:
                    case BytearraySource.STRING:
                        return QByteArray(self.value["string"].encode("utf-8"))
                    case BytearraySource.FILE:
                        try:
                            with open(self.value["path"], "rb") as f:
                                return QByteArray(f.read())
                        except Exception:
                            return QByteArray()
                    case _:
                        return QByteArray()
            case DBusTypeEnum.OBJECT_PATH:
                return QDBusObjectPath(self.value)

    def get_printable_text(self) -> str:
        match self.dbus_type.type_const:
            case DBusTypeEnum.DICT:
                return str(self.value)
                print_dict: dict[str, str] = {}
                for key, value in self.value.items():
                    print_dict[key] = value.get_printable_text()
                return str(print_dict)
            case DBusTypeEnum.ARRAY:
                array: list[str] = []
                for i in self.value:
                    array.append(DBusValue.create(self.dbus_type.array_type, i).get_printable_text())
                return "[" + ", ".join(array) + "]"
            case DBusTypeEnum.BYTE_ARRAY:
                return str(self.value.data())
            case DBusTypeEnum.FILE_HANDLE:
                return f"<FileHandle '{self.value}'>"
            case DBusTypeEnum.OBJECT_PATH:
                return f"<ObjectPath '{self.value}'>"
            case _:
                return str(self.value)
