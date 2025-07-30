from ..types.actions.ActionBase import ActionBase
from ..Functions import read_json_file
from typing import TYPE_CHECKING
from ..types.Macro import Macro
import json
import uuid
import os


if TYPE_CHECKING:
    from ..types.Connection import Connection
    from ..Environment import Environment


class MacroManager:
    def __init__(self, env: "Environment") -> None:
        self._current_actions: list[ActionBase] = []
        self._macros: list[Macro] = []
        self._recording = False
        self._env = env

        self._load_all_macros()

    def _generate_macro_id(self) -> str:
        while True:
            current_id = str(uuid.uuid4())
            if self.get_macro_by_id(current_id) is None:
                return current_id

    def _load_all_macros(self) -> None:
        self._macros.clear()

        json_data = read_json_file(os.path.join(self._env.data_dir, "macros.json"), None)

        if json_data is None:
            return

        for macro_data in json_data["macros"]:
            self._macros.append(Macro.from_json_data(macro_data))

    def save_all_macros(self) -> None:
        json_data = {
            "version": 1,
            "macros": []
        }

        for macro in self._macros:
            json_data["macros"].append(macro.get_json_data())

        text = json.dumps(json_data, indent=4, ensure_ascii=False)

        with open(os.path.join(self._env.data_dir, "macros.json"), "w", encoding="utf-8") as f:
            f.write(text)

    def add_macro(self, macro: Macro) -> None:
        macro.id = self._generate_macro_id()
        self._macros.append(macro)

    def get_macro_by_id(self, macro_id: str) -> Macro | None:
        for macro in self._macros:
            if macro.id == macro_id:
                return macro
        return None

    def get_macro_by_name(self, name: str) -> Macro | None:
        for macro in self._macros:
            if macro.name.lower() == name.lower():
                return macro
        return None

    def is_recording(self) -> bool:
        return self._recording

    def get_current_actions(self) -> list[ActionBase]:
        return self._current_actions

    def has_current_macro(self) -> bool:
        return len(self._current_actions) > 0

    def start_recording(self) -> None:
        self._current_actions.clear()
        self._recording = True

    def stop_recording(self) -> None:
        self._recording = False

    def reset_recording(self) -> None:
        self._current_actions.clear()
        self._recording = False

    def save_current_macro(self, name: str, connection: "Connection") -> None:
        self._macros.append(Macro.create(self._generate_macro_id(), name, self._current_actions, connection))
        self.save_all_macros()

    def record_action(self, action: ActionBase) -> None:
        if self._recording:
            self._current_actions.append(action)

    def get_macros_for_connection(self, connection: "Connection") -> list[Macro]:
        macro_list: list[Macro] = []

        for macro in self._macros:
            if macro.do_connection_match(connection):
                macro_list.append(macro)

        return macro_list

    def get_all_macros(self) -> list[Macro]:
        return self._macros

    def delete_macro(self, macro_id: str) -> None:
        for count, macro in enumerate(self._macros):
            if macro.id == macro_id:
                del self._macros[count]
                return
