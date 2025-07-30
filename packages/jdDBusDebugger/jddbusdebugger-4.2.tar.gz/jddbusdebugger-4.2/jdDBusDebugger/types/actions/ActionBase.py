from typing import Any


class ActionBase:
    def __init__(self) -> None:
        self.action_type: str = ""
        self.service_name: str = ""
        self.object_path: str = ""
        self.interface_name: str = ""

    @classmethod
    def from_json_data(obj, data: dict[str, Any]) -> "ActionBase":
        raise NotImplementedError()

    def get_json_data(self) -> Any:
        raise NotImplementedError()

    def get_qdbus_command(self) -> str:
        raise NotImplementedError()

    def get_gdbus_command(self) -> str:
        raise NotImplementedError()
