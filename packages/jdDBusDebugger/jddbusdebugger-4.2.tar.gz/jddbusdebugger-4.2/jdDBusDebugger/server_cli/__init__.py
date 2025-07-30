from PyQt6.QtCore import QCoreApplication
from ..types.Connection import Connection
from ..core.Server import Server
import traceback
import argparse
import shutil
import sys


def main() -> None:
    parser = argparse.ArgumentParser(prog="jddbusdebugger-server")
    parser.add_argument("bus", nargs=1, help="The bus. Use session, system or a custom connection.")
    args, _ = parser.parse_known_args()

    if not shutil.which("socat"):
        print("socat not found", file=sys.stderr)
        return

    bus: str = args.bus[0]

    app = QCoreApplication(sys.argv)

    match bus:
        case "session":
            connection = Connection.new_session_connection()
        case "system":
            connection = Connection.new_system_connection()
        case _:
            connection = Connection.new_custom_connection(bus, "custom")

    if not connection.is_connected():
        print("Could not conenct to the given bus", file=sys.stderr)
        sys.exit(1)

    server = Server(connection)
    server.start()

    while True:
        try:
            app.processEvents()
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            break
        except KeyboardInterrupt:
            break

    server.stop()
