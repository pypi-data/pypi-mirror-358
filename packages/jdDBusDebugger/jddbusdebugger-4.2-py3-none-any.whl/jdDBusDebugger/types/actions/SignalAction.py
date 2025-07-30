from typing import TYPE_CHECKING, Any
from .ActionBase import ActionBase
import subprocess


if TYPE_CHECKING:
    from ..Signal import Signal


class SignalAction(ActionBase):
    def __init__(self) -> None:
        super().__init__()

        self.action_type = "signal"
        self.signal_action = ""
        self.signal_name = ""


    @classmethod
    def from_signal(obj, signal: "Signal", signal_action: str):
        action = obj()

        action.service_name = signal.interface.service.name
        action.object_path = signal.interface.object_path
        action.interface_name = signal.interface.name
        action.signal_name = signal.name
        action.signal_action = signal_action

        return action

    @classmethod
    def from_json_data(obj, data: dict[str, Any]) -> "SignalAction":
        action = obj()

        action.service_name = data["service_name"]
        action.object_path = data["object_path"]
        action.interface_name = data["interface_name"]
        action.signal_name= data["signal_name"]
        action.signal_action = data["signal_action"]

        return action

    def get_json_data(self) -> Any:
        return {
            "action_type": self.action_type,
            "service_name": self.service_name,
            "object_path": self.object_path,
            "interface_name": self.interface_name,
            "signal_name": self.signal_name,
            "signal_action": self.signal_action,
        }

    def get_qdbus_command(self) -> str:
        return "Not available"

    def get_gdbus_command(self) -> str:
        return "Not available"