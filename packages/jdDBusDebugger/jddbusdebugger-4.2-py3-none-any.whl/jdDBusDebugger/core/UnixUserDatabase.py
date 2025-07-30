from ..Functions import is_flatpak
import os


class UnixUserDatabase:
    _instance = None

    def __init__(self) -> None:
        if is_flatpak():
            passwd_path = "/run/host/etc/passwd"
        else:
            passwd_path = "/etc/passwd"

        self._unix_user: dict[int, str] = {}

        if not os.access(passwd_path, os.R_OK):
            return

        with open(passwd_path, "r", encoding="utf-8") as f:
            for line in f.read().splitlines():
                content = line.split(":")
                self._unix_user[int(content[2])] = content[0]

    @classmethod
    def get_database(cls) -> "UnixUserDatabase":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_user_name(self, uid: int) -> str:
        if uid in self._unix_user:
            return self._unix_user[uid]
        else:
            return str(uid)
