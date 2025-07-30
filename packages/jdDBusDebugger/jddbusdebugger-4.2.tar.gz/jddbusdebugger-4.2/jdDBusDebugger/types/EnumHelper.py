from typing import Any
import inspect


class EnumHelper:
    @classmethod
    def get_enum_name_by_value(cls: "EnumHelper", value: str) -> str:
        for member in inspect.getmembers(cls):
            if member[1] == value:
                return member[0]

    @classmethod
    def get_enum_value_by_name(cls: "EnumHelper", name: str) -> Any:
        for member in inspect.getmembers(cls):
            if member[0] == name:
                return member[1]