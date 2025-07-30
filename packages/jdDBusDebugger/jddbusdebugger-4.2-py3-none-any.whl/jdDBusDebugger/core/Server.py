from PyQt6.QtNetwork import QUdpSocket, QHostAddress
from PyQt6.QtCore import QObject, QProcess
from ..Constants import SERVER_CONSTANTS
from typing import TYPE_CHECKING
import traceback
import socket
import json
import sys


if TYPE_CHECKING:
    from ..types.Connection import Connection


class Server(QObject):
    def __init__(self, connection: "Connection") -> None:
        super().__init__()

        self._is_running = False
        self._process = QProcess()
        self._connection = connection

        self._broadcast_socket = QUdpSocket(self)
        self._broadcast_socket.bind(SERVER_CONSTANTS.BROADCAST_PORT, QUdpSocket.BindFlag.ShareAddress)

        self._broadcast_socket.readyRead.connect(self._read_broadcast_socket)

    def _send_back(self, data: bytes, address: QHostAddress) -> None:
        if not data.startswith(SERVER_CONSTANTS.BROADCAST_MAGIC.encode("utf-8")):
            return

        _, token = data.decode("utf-8").split(":")

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.connect(('<broadcast>', 0))

        reply_data = {
            "hostname": socket.gethostname(),
            "ip": s.getsockname()[0],
        }

        send_content = f"{SERVER_CONSTANTS.REPLY_MAGIC}:{token}:{json.dumps(reply_data)}"

        send_socket = QUdpSocket(self)
        send_socket.connectToHost(address, SERVER_CONSTANTS.REPLY_PORT)
        send_socket.write(send_content.encode("utf-8"))

    def _read_broadcast_socket(self) -> None:
        if not self._is_running:
            return

        while self._broadcast_socket.hasPendingDatagrams():
            data, address, _ = self._broadcast_socket.readDatagram(int(self._broadcast_socket.pendingDatagramSize()))

            try:
                self._send_back(data, address)
            except Exception:
                print(traceback.format_exc(), file=sys.stderr)

    def start(self) -> None:
        socket_path = self._connection.get_address().removeprefix("unix:path=")
        self._process.start("socat", [f"TCP-LISTEN:{SERVER_CONSTANTS.SOCAT_PORT},reuseaddr,fork", f"UNIX-CONNECT:{socket_path}"])
        self._is_running = True

    def stop(self) -> None:
        self._process.kill()
        self._process.waitForFinished()
        self._is_running = False

    def is_running(self) -> bool:
        return self._is_running
