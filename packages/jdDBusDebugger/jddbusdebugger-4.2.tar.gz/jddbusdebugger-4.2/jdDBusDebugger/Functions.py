from PyQt6.QtWidgets import QWidget, QComboBox, QTableWidget, QMessageBox
from PyQt6.QtDBus import QDBusMessage, QDBusConnection
from PyQt6.QtCore import QObject, QCoreApplication
from typing import Any, Literal
import subprocess
import functools
import shutil
import json
import sys
import os


def read_json_file(path: str, default: Any) -> Any:
    """
    Tries to parse the given JSON file and prints a error if the file couldn't be parsed
    Returns default if the file is not found or couldn't be parsed
    """
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except json.decoder.JSONDecodeError as e:
            print(f"Can't parse {os.path.basename(path)}: {e.msg}: line {e.lineno} column {e.colno} (char {e.pos})", file=sys.stderr)
            return default
        except Exception:
            print("Can't read " + os.path.basename(path), file=sys.stderr)
            return default
    else:
        return default


def select_combo_box_data(box: QComboBox, data: Any, default_index: int = 0) -> None:
    """Set the index to the item with the given data"""
    index = box.findData(data)
    if index == -1:
        box.setCurrentIndex(default_index)
    else:
        box.setCurrentIndex(index)


def clear_table_widget(table: QTableWidget):
    """Removes all Rows from a QTableWidget"""
    while table.rowCount() > 0:
        table.removeRow(0)


def get_table_widget_sender_row(table: QTableWidget, column: int, sender: QObject) -> int:
    """Get the Row in a QTableWidget that contains the Button that was clicked"""
    for i in range(table.rowCount()):
        if table.cellWidget(i, column) == sender:
            return i


def format_dbus_error(msg: QDBusMessage) -> str:
    if msg.errorMessage() == "":
        return msg.errorName()
    else:
        return f"{msg.errorName()}: {msg.errorMessage()}"


def is_integer(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False

def is_flatpak() -> bool:
    return os.path.exists("/.flatpak-info")


def get_running_flatpaks() -> list[dict[Literal["pid", "id"], str]]:
    command = ["flatpak", "ps", "--columns=child-pid,application"]

    if is_flatpak():
        command = ["flatpak-spawn", "--host"] + command

    try:
        result = subprocess.run(command, capture_output=True)
    except Exception:
        return []

    flatpak_list = []

    for line in result.stdout.decode("utf-8").splitlines():
        try:
            pid, app_id = line.split("\t")
        except ValueError:
            continue

        if not is_integer(pid) or app_id == "":
            continue

        flatpak_list.append({"pid": pid, "id": app_id})

    return flatpak_list


def get_all_processes() -> dict[int, str]:
    command = ["ps", "-e", "-o", "pid,comm="]

    if is_flatpak():
        command = ["flatpak-spawn", "--host"] + command

    process_dict = {}
    result = subprocess.run(command, capture_output=True)
    for line in result.stdout.decode("utf-8").splitlines():
        line = line.strip()

        try:
            pid, name = line.split(" ")
        except ValueError:
            continue

        try:
            process_dict[int(pid)] = name
        except ValueError:
            continue

    return process_dict


def check_socat(parent: QWidget) -> bool:
    if not shutil.which("socat"):
        QMessageBox.critical(
            parent,
            QCoreApplication.translate("Functions", "socat not found"),
            QCoreApplication.translate("Functions", "socat was not found. It needs to be installed to use this Feature.")
        )
        return False
    else:
        return True


@functools.cache
def is_scheme_supported(scheme: str) -> bool:
    conn = QDBusConnection.sessionBus()

    if not conn.isConnected():
        return False

    msg = QDBusMessage.createMethodCall(
        "org.freedesktop.portal.Desktop",
        "/org/freedesktop/portal/desktop",
        "org.freedesktop.portal.OpenURI",
        "SchemeSupported"
    )

    msg.setArguments((scheme, {}))

    resp = conn.call(msg)

    if resp.type() != QDBusMessage.MessageType.ReplyMessage:
        print(f"Failed to call org.freedesktop.portal.OpenURI.SchemeSupported: {resp.errorMessage()}", file=sys.stderr)
        return False

    return resp.arguments()[0]
