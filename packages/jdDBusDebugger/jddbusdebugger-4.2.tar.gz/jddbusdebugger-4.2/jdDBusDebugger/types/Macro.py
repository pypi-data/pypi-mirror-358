
from .actions.PropertyAction import PropertyAction
from .actions.SignalAction import SignalAction
from .actions.CallAction import CallAction
from .actions.EmitAction import EmitAction
from typing import Any, TYPE_CHECKING
import copy


if TYPE_CHECKING:
    from .actions.ActionBase import ActionBase
    from .Connection import Connection


class Macro:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.connection_type = ""
        self.connection_address = ""

        self.actions: list["ActionBase"] = []

    @classmethod
    def create(obj, macro_id: str, name: str, actions: list["ActionBase"], connection: "Connection") -> "Macro":
        macro = obj()

        macro.id = macro_id
        macro.name = name

        macro.connection_type = connection.connection_type

        if connection.connection_type == "custom":
            macro.connection_address = connection.custom_address

        macro.actions = copy.deepcopy(actions)

        return macro

    @classmethod
    def from_json_data(obj, json_data: dict[str, Any]) -> "Macro":
        macro = obj()

        macro.id = json_data["id"]
        macro.name = json_data["name"]
        macro.connection_type = json_data["connection_type"]
        macro.connection_address = json_data["connection_address"]

        for action_data in json_data["actions"]:
            match action_data["action_type"]:
                case "call":
                    macro.actions.append(CallAction.from_json_data(action_data))
                case "property":
                    macro.actions.append(PropertyAction.from_json_data(action_data))
                case "signal":
                    macro.actions.append(SignalAction.from_json_data(action_data))
                case "emit":
                    macro.actions.append(EmitAction.from_json_data(action_data))

        return macro

    def get_json_data(self) -> dict[str, Any]:
        json_data = {
            "id": self.id,
            "name": self.name,
            "connection_type": self.connection_type,
            "connection_address": self.connection_address,
            "actions": []
        }

        for action in self.actions:
            json_data["actions"].append(action.get_json_data())

        return json_data

    def do_connection_match(self, connection: "Connection") -> bool:
        if self.connection_type == "custom" and connection.connection_type == "custom":
            return self.connection_address == connection.custom_address

        return self.connection_type == connection.connection_type
