from PyQt6.QtCore import QTranslator, QLocale, QLibraryInfo
from PyQt6.QtWidgets import QApplication
from .Environment import Environment
import sys
import os


def main() -> None:
    if not os.path.isdir(os.path.join(os.path.dirname(__file__), "ui_compiled")):
        print("Could not find compiled ui files. Please run tools/CompileUI.py first.", file=sys.stderr)
        sys.exit(1)

    from .gui.WelcomeDialog import WelcomeDialog
    from .gui.MainWindow import MainWindow

    app = QApplication(sys.argv)

    env = Environment()

    app.setWindowIcon(env.icon)
    app.setApplicationVersion(env.version)
    app.setApplicationName("jdDBusDebugger")
    app.setDesktopFileName("page.codeberg.JakobDev.jdDBusDebugger")

    if env.settings.get("language") == "default":
        current_locale = QLocale.system()
    else:
        current_locale = QLocale(env.settings.get("language"))

    app_translator = QTranslator()
    if app_translator.load(current_locale, "jdDBusDebugger", "_", os.path.join(env.program_dir, "translations")):
        app.installTranslator(app_translator)

    qt_translator = QTranslator()
    if qt_translator.load(current_locale, "qt", "_", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(qt_translator)

    w = MainWindow(env)
    w.showMaximized()

    if env.settings.get("showWelcomeDialogStartup"):
        WelcomeDialog(None, env).open_dialog()

    sys.exit(app.exec())
