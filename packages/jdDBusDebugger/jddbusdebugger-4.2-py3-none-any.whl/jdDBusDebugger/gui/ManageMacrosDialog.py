from PyQt6.QtWidgets import QDialog, QListWidgetItem, QInputDialog, QMessageBox, QFileDialog
from ..ui_compiled.ManageMacrosDialog import Ui_ManageMacrosDialog
from .GenerateScriptDialog import GenerateScriptDialog
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
from ..types.Macro import Macro
import traceback
import json
import sys
import os


if TYPE_CHECKING:
    from ..core.MacroManager import MacroManager
    from .MainWindow import MainWindow


class ManageMacrosDialog(QDialog, Ui_ManageMacrosDialog):
    def __init__(self, main_window: "MainWindow", macro_manager: "MacroManager") -> None:
        super().__init__(main_window)

        self.setupUi(self)

        self._macro_manager = macro_manager

        self.macro_list.currentRowChanged.connect(self._update_buttons_enabled)

        self.rename_button.clicked.connect(self._rename_button_clicked)
        self.delete_button.clicked.connect(self._delete_button_clicked)
        self.view_script_button.clicked.connect(self._view_script_button_clicked)
        self.export_button.clicked.connect(self._export_button_clicked)
        self.import_button.clicked.connect(self._import_button_clicked)
        self.ok_button.clicked.connect(self.close)

    def _get_selected_macro(self) -> Macro:
        return self._macro_manager.get_macro_by_id(self.macro_list.currentItem().data(42))

    def _update_buttons_enabled(self) -> None:
        enabled = self.macro_list.currentRow() != -1
        self.rename_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
        self.view_script_button.setEnabled(enabled)
        self.export_button.setEnabled(enabled)

    def _update_macro_list(self) -> None:
        self.macro_list.clear()

        for macro in self._macro_manager.get_all_macros():
            item = QListWidgetItem(macro.name)
            item.setData(42, macro.id)
            self.macro_list.addItem(item)

        self._update_buttons_enabled()

    def _rename_button_clicked(self) -> None:
        macro = self._get_selected_macro()

        name = QInputDialog.getText(self, QCoreApplication.translate("ManageMacrosDialog", "Enter name"), QCoreApplication.translate("ManageMacrosDialog", "Please enter a new name for the macro"), text=macro.name)[0].strip()

        if name == "" or name.lower() == macro.name.lower():
            return

        if self._macro_manager.get_macro_by_name(name) is not None:
            QMessageBox.critical(self, QCoreApplication.translate("ManageMacrosDialog", "Name exists"), QCoreApplication.translate("ManageMacrosDialog", "There is already a macro with this name"))
            return

        macro.name = name

        self._macro_manager.save_all_macros()
        self._update_macro_list()

    def _delete_button_clicked(self) -> None:
        macro = self._get_selected_macro()

        if QMessageBox.question(self, QCoreApplication.translate("ManageMacrosDialog", "Delete macro"), QCoreApplication.translate("ManageMacrosDialog", "This will delete {{name}} forever. Are you sure??").replace("{{name}}", macro.name)) != QMessageBox.StandardButton.Yes:
            return

        self._macro_manager.delete_macro(macro.id)
        self._macro_manager.save_all_macros()
        self._update_macro_list()

    def _view_script_button_clicked(self) -> None:
        macro = self._get_selected_macro()

        GenerateScriptDialog().open_dialog(macro.actions)

    def _export_button_clicked(self) -> None:
        macro = self._get_selected_macro()

        filter = QCoreApplication.translate("ManageMacrosDialog", "JSON files") + " (*.json);;" +   QCoreApplication.translate("ManageMacrosDialog", "All Files") + " (*)"

        path = QFileDialog.getSaveFileName(self, directory=os.path.expanduser("~"), filter = filter)[0]

        if path == "":
            return

        try:
            data = macro.get_json_data()
            data["version"] = 1

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            QMessageBox.critical(self, QCoreApplication.translate("ManageMacrosDialog", "Could not export macro"), QCoreApplication.translate("ManageMacrosDialog", "The macro could not be exported to {{path}} due to an error").replace("{{path}}", path))

    def _import_button_clicked(self) -> None:
        filter = QCoreApplication.translate("ManageMacrosDialog", "JSON files") + " (*.json);;" +   QCoreApplication.translate("ManageMacrosDialog", "All Files") + " (*)"

        path = QFileDialog.getOpenFileName(self, directory=os.path.expanduser("~"), filter = filter)[0]

        if path == "":
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            macro = Macro.from_json_data(data)
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            QMessageBox.critical(self, QCoreApplication.translate("ManageMacrosDialog", "Could not import macro"), QCoreApplication.translate("ManageMacrosDialog", "The macro could not be imported. Please make sure you use the correct file."))
            return

        while True:
            name = QInputDialog.getText(self, QCoreApplication.translate("ManageMacrosDialog", "Enter name"), QCoreApplication.translate("ManageMacrosDialog", "Please enter a name for the macro"), text=macro.name)[0].strip()

            if name == "":
                return

            if self._macro_manager.get_macro_by_name(name) is not None:
                QMessageBox.critical(self, QCoreApplication.translate("ManageMacrosDialog", "Name exists"), QCoreApplication.translate("ManageMacrosDialog", "There is already a macro with this name"))
                continue

            break

        macro.name = name

        self._macro_manager.add_macro(macro)
        self._macro_manager.save_all_macros()
        self._update_macro_list()

    def open_dialog(self) -> None:
        self._update_macro_list()

        self.exec()
