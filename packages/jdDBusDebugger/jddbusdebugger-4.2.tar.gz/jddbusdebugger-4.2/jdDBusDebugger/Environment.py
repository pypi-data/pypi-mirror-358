from .core.Settings import Settings
from PyQt6.QtGui import QIcon
import platform
import pathlib
import os


class Environment:
    def __init__(self) -> None:
        self.program_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = self._get_data_path()

        with open(os.path.join(self.program_dir, "version.txt"), "r", encoding="utf-8") as f:
            self.version = f.read().strip()

        self.icon = QIcon(os.path.join(self.program_dir, "Icon.png"))

        try:
            os.makedirs(self.data_dir)
        except FileExistsError:
            pass

        self.settings = Settings()
        self.settings.load(os.path.join(self.data_dir, "settings.json"))

    def _get_data_path(self) -> str:
        if platform.system() == "Windows":
            return os.path.join(os.getenv("APPDATA"), "JakobDev", "jdDBusDebugger")
        elif platform.system() == "Darwin":
            return os.path.join(pathlib.Path.home(), "Library", "Application Support", "JakobDev", "jdDBusDebugger")
        elif platform.system() == "Haiku":
            return os.path.join(pathlib.Path.home(), "config", "settings", "JakobDev", "jdDBusDebugger")
        else:
            if os.getenv("XDG_DATA_HOME"):
                return os.path.join(os.getenv("XDG_DATA_HOME"), "JakobDev", "jdDBusDebugger")
            else:
                return os.path.join(pathlib.Path.home(), ".local", "share", "JakobDev", "jdDBusDebugger")

    def get_available_languages(self) -> list[str]:
        lang_list: list[str] = []

        for lang_file in os.listdir(os.path.join(self.program_dir, "translations")):
            if lang_file.startswith("jdDBusDebugger_") and lang_file.endswith(".qm"):
                lang_list.append(lang_file.removeprefix("jdDBusDebugger_").removesuffix(".qm"))

        return lang_list
