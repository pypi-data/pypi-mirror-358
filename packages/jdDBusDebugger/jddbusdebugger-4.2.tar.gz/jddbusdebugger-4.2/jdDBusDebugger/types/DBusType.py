from PyQt6.QtCore import QMetaType
from .EnumHelper import EnumHelper
from typing import Any
import re


class DBusTypeEnum(EnumHelper):
    UNKNOWN = 0
    BYTE = 1
    BOOLEAN = 2
    INT16 = 3
    UINT16 = 4
    INT32 = 5
    UINT32 = 6
    INT64 = 7
    UINT64 = 8
    DOUBLE = 9
    STRING = 10
    VARIANT = 11
    OBJECT_PATH = 12
    FILE_HANDLE = 13
    ARRAY = 14
    STRUCT = 15
    DICT = 16
    BYTE_ARRAY = 17


class DBusType:
    def __init__(self) -> None:
        self.type_text = ""
        self.type_const = DBusTypeEnum.UNKNOWN
        self.array_type: "DBusType" | None = None

    @classmethod
    def from_type_text(cls: type["DBusType"], type_text: str) -> "DBusType":
        dbus_type = cls()

        dbus_type.type_text = type_text

        if len(type_text) == 1:
            match type_text:
                case "y":
                    dbus_type.type_const = DBusTypeEnum.BYTE
                case "b":
                    dbus_type.type_const = DBusTypeEnum.BOOLEAN
                case "n":
                    dbus_type.type_const = DBusTypeEnum.INT16
                case "q":
                    dbus_type.type_const = DBusTypeEnum.UINT16
                case "i":
                    dbus_type.type_const = DBusTypeEnum.INT32
                case "u":
                    dbus_type.type_const = DBusTypeEnum.UINT32
                case "x":
                    dbus_type.type_const = DBusTypeEnum.INT64
                case "t":
                    dbus_type.type_const = DBusTypeEnum.UINT64
                case "d":
                    dbus_type.type_const = DBusTypeEnum.DOUBLE
                case "s":
                    dbus_type.type_const = DBusTypeEnum.STRING
                case "v":
                    dbus_type.type_const = DBusTypeEnum.VARIANT
                case "o":
                    dbus_type.type_const = DBusTypeEnum.OBJECT_PATH
                case "h":
                    dbus_type.type_const = DBusTypeEnum.FILE_HANDLE
                case _:
                    dbus_type.type_const = DBusTypeEnum.UNKNOWN
        else:
            if re.match(r"a{[a-z]{2,}}", type_text) is not None:
                dbus_type.type_const = DBusTypeEnum.DICT
                #dbus_type.dict_key = DBusType(dbus_type.type_text[2])
                #dbus_type.dict_value = DBusType(dbus_type.type_text[3:-1])
            elif type_text.startswith("a"):
                dbus_type.type_const = DBusTypeEnum.ARRAY
                dbus_type.array_type = cls.from_type_text(type_text[1:])
                if dbus_type.array_type.type_const == DBusTypeEnum.BYTE:
                    dbus_type.type_const = DBusTypeEnum.BYTE_ARRAY
            else:
                dbus_type.type_const = DBusTypeEnum.UNKNOWN

        return dbus_type

    @classmethod
    def from_type_const(cls: type["DBusType"], type_const: int) -> "DBusType":
        dbus_type = cls()

        dbus_type.type_const = type_const

        return dbus_type

    @classmethod
    def from_display_name(cls: type["DBusType"], name: str) -> "DBusType":
        for current_type in cls.get_available_types():
            if current_type.get_display_name() == name:
                return current_type

    @classmethod
    def from_json_data(cls: type["DBusType"], json_data: dict[str, Any]) -> "DBusType":
        dbus_type = cls()

        dbus_type.type_text = json_data["type_text"]
        dbus_type.type_const = DBusTypeEnum.get_enum_value_by_name(json_data["type_const"])
        dbus_type.signature_type_const = DBusTypeEnum.get_enum_value_by_name(json_data["signature_type_const"])

        match dbus_type.type_const:
            case DBusTypeEnum.ARRAY:
                dbus_type.array_type = cls.from_json_data("array_type")

        return dbus_type

    def get_json_data(self) -> dict[str, Any]:
        json_data = {
            "type_text": self.type_text,
            "type_const": DBusTypeEnum.get_enum_name_by_value(self.type_const),
        }

        match self.type_const:
            case DBusTypeEnum.ARRAY:
                json_data["array_type"] = self.array_type.get_json_data()

        return json_data

    def get_display_name(self) -> str:
        match self.type_const:
            case DBusTypeEnum.BYTE:
                return "Byte"
            case DBusTypeEnum.BOOLEAN:
                return "Boolean"
            case DBusTypeEnum.INT16:
                return "Int16"
            case DBusTypeEnum.UINT16:
                return "UInt16"
            case DBusTypeEnum.INT32:
                return "Int32"
            case DBusTypeEnum.UINT32:
                return "UInt32"
            case DBusTypeEnum.INT64:
                return "Int64"
            case DBusTypeEnum.UINT64:
                return "UInt64"
            case DBusTypeEnum.DOUBLE:
                return "Double"
            case DBusTypeEnum.STRING:
                return "String"
            case DBusTypeEnum.VARIANT:
                return "Variant"
            case DBusTypeEnum.OBJECT_PATH:
                return "Object Path"
            case DBusTypeEnum.FILE_HANDLE:
                return "File Handle"
            case DBusTypeEnum.ARRAY:
                return "Array"
            case DBusTypeEnum.STRUCT:
                return "Struct"
            case DBusTypeEnum.DICT:
                return "Dict"
            case DBusTypeEnum.BYTE_ARRAY:
                return "Bytearray"
            case _:
                return "Unknown"

    def get_qmeta_type(self) -> QMetaType:
        # https://doc.qt.io/qt-6/qdbustypesystem.html
        match self.type_const:
            case DBusTypeEnum.BYTE:
                return QMetaType(QMetaType.Type.UChar.value)
            case DBusTypeEnum.BOOLEAN:
                return QMetaType(QMetaType.Type.Bool.value)
            case DBusTypeEnum.INT16:
                return QMetaType(QMetaType.Type.Short.value)
            case DBusTypeEnum.UINT16:
                return QMetaType(QMetaType.Type.UShort.value)
            case DBusTypeEnum.INT32:
                return QMetaType(QMetaType.Type.Int.value)
            case DBusTypeEnum.UINT32:
                return QMetaType(QMetaType.Type.UInt.value)
            case DBusTypeEnum.INT64:
                return QMetaType(QMetaType.Type.LongLong.value)
            case DBusTypeEnum.UINT64:
                return QMetaType(QMetaType.Type.ULongLong.value)
            case DBusTypeEnum.DOUBLE:
                return QMetaType(QMetaType.Type.Double.value)
            case DBusTypeEnum.STRING:
                return QMetaType(QMetaType.Type.QString.value)

    def is_simple_type(self) -> bool:
        return self.type_const in (
            DBusTypeEnum.BYTE,
            DBusTypeEnum.BOOLEAN,
            DBusTypeEnum.INT16,
            DBusTypeEnum.UINT16,
            DBusTypeEnum.INT32,
            DBusTypeEnum.UINT32,
            DBusTypeEnum.INT64,
            DBusTypeEnum.UINT64,
            DBusTypeEnum.DOUBLE,
            DBusTypeEnum.STRING,
        )

    def __repr__(self) -> str:
        return f"DBusType(type_text: '{self.type_text}' type_const: {DBusTypeEnum.get_enum_name_by_value(self.type_const)}, array_type: {self.array_type})"

    @classmethod
    def get_available_types(cls: type["DBusType"]) -> list["DBusType"]:
        return [
            cls.from_type_const(DBusTypeEnum.BYTE),
            cls.from_type_const(DBusTypeEnum.BOOLEAN),
            cls.from_type_const(DBusTypeEnum.INT16),
            cls.from_type_const(DBusTypeEnum.UINT16),
            cls.from_type_const(DBusTypeEnum.INT32),
            cls.from_type_const(DBusTypeEnum.UINT32),
            cls.from_type_const(DBusTypeEnum.INT64),
            cls.from_type_const(DBusTypeEnum.UINT64),
            cls.from_type_const(DBusTypeEnum.DOUBLE),
            cls.from_type_const(DBusTypeEnum.STRING),
            cls.from_type_const(DBusTypeEnum.VARIANT),
            cls.from_type_const(DBusTypeEnum.OBJECT_PATH),
            cls.from_type_const(DBusTypeEnum.FILE_HANDLE),
            cls.from_type_const(DBusTypeEnum.ARRAY),
            cls.from_type_const(DBusTypeEnum.STRUCT),
            cls.from_type_const(DBusTypeEnum.DICT),
            cls.from_type_const(DBusTypeEnum.BYTE_ARRAY),
        ]
