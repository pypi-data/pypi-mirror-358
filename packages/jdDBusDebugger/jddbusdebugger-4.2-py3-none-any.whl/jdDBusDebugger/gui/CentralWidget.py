from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QTreeWidgetItem, QInputDialog, QMessageBox, QMenu, QApplication, QHeaderView
from PyQt6.QtGui import QCursor, QAction, QContextMenuEvent, QTextCharFormat, QColor, QIcon, QDesktopServices
from ..Functions import clear_table_widget, format_dbus_error, is_scheme_supported
from .types_input.SingleValueInputDialog import SingleValueInputDialog
from PyQt6.QtCore import Qt, QObject, QCoreApplication, QUrl, pyqtSlot
from ..types.actions.PropertyAction import PropertyAction
from ..ui_compiled.CentralWidget import Ui_CentralWidget
from PyQt6.QtDBus import QDBusMessage, QDBusConnection
from ..types.actions.SignalAction import SignalAction
from .types_input.ArgumentInput import ArgumentInput
from ..types.actions.CallAction import CallAction
from ..types.DBusType import DBusTypeEnum
from ..types.DBusValue import DBusValue
from typing import Any, TYPE_CHECKING
import secrets


if TYPE_CHECKING:
    from ..types.actions.ActionBase import ActionBase
    from ..types.actions.EmitAction import EmitAction
    from ..types.Connection import Connection
    from ..types.Interface import Interface
    from ..Environment import Environment
    from ..types.Property import Property
    from ..types.Service import Service
    from .MainWindow import MainWindow
    from ..types.Method import Method
    from ..types.Signal import Signal



class _ObjectItem(QTreeWidgetItem):
    def __init__(self) -> None:
        super().__init__()

        self.name = ""


class _MethodItem(_ObjectItem):
    def __init__(self, central_widget: "CentralWidget", method: "Method") -> None:
        super().__init__()

        self._central_widget = central_widget
        self._method = method
        self.name = method.name

        self.setText(0, method.name)

    def get_context_menu_actions(self) -> list[QAction]:
        action_list: list[QAction] = []

        call_action = QAction(QCoreApplication.translate("CentralWidget", "Call"), self._central_widget)
        call_action.triggered.connect(self.call_method)
        action_list.append(call_action)

        return action_list

    def call_method(self) -> None:
        if len(self._method.arguments) != 0:
            args = ArgumentInput(self._central_widget).get_argument_values(self._method.name, self._method.arguments)

            if args is None:
                return
        else:
            args = []

        self._central_widget.call_method(self._method, args, True)


class _PropertyItem(QTreeWidgetItem):
    def __init__(self, central_widget: "CentralWidget", prop: "Property") -> None:
        super().__init__()

        self._central_widget = central_widget
        self._property = prop
        self.name = prop.name

        self.setText(0, prop.name)

    def get_context_menu_actions(self) -> list[QAction]:
        action_list: list[QAction] = []

        if self._property.read_access:
            get_value_action = QAction(QCoreApplication.translate("CentralWidget", "Get value"), self._central_widget)
            get_value_action.triggered.connect(self.get_value)
            action_list.append(get_value_action)

        if self._property.write_access:
            set_value_action = QAction(QCoreApplication.translate("CentralWidget", "Set value"), self._central_widget)
            set_value_action.triggered.connect(self._set_value)
            action_list.append(set_value_action)

        return action_list

    def get_value(self) -> None:
        self._central_widget.get_property_value(self._property, True)

    def _set_value(self) -> None:
        old_value, err = self._property.get_value()

        if err is not None:
            self._central_widget.add_log_error(err)
            return

        new_value, ok = SingleValueInputDialog(self._central_widget, self._property.dbus_type).open_input_dialog(old_value)
        if ok:
            self._central_widget.set_property_value(self._property, new_value, True)


class _SignalItem(QTreeWidgetItem):
    def __init__(self, central_widget: "CentralWidget", signal: "Signal") -> None:
        super().__init__()

        self._central_widget = central_widget
        self._signal = signal
        self.name = signal.name

        self.setText(0, signal.name)

    def get_context_menu_actions(self) -> list[QAction]:
        action_list: list[QAction] = []

        connect_or_disconnect_action = QAction("", self._central_widget)
        if self._signal.is_connected:
            connect_or_disconnect_action.setText(QCoreApplication.translate("CentralWidget", "Disconnect"))
        else:
            connect_or_disconnect_action.setText(QCoreApplication.translate("CentralWidget", "Connect"))
        connect_or_disconnect_action.triggered.connect(self.connect_or_disconnect)
        action_list.append(connect_or_disconnect_action)

        return action_list

    def connect_or_disconnect(self):
        if self._signal.is_connected:
            self._central_widget.disconnect_signal(self._signal, True)
        else:
            self._central_widget.connect_signal(self._signal, True)


class _SignalListener(QObject):
    def __init__(self, central_widget: "CentralWidget", signal: "Signal") -> None:
        super().__init__()

        self._central_widget = central_widget
        self._signal = signal

    @pyqtSlot(QDBusMessage)
    def signal_slot(self, msg: QDBusMessage) -> None:
        arg_list: list[str] = []

        for i in range(len(self._signal.types)):
            value = DBusValue.create(self._signal.types[i], msg.arguments()[i])
            arg_list.append(value.get_printable_text())

        if len(arg_list) == 0:
            arg_text = QCoreApplication.translate("CentralWidget", "No parameters")
        else:
            arg_text = ", ".join(arg_list)

        self._central_widget.add_log_text(QCoreApplication.translate("CentralWidget", "Signal {{signal}} emited: {{reply}}").replace("{{signal}}", msg.member()).replace("{{reply}}", arg_text))

        if QApplication.activeWindow() is not None:
            return

        msg = QDBusMessage.createMethodCall("org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop", "org.freedesktop.portal.Notification", "AddNotification")
        msg.setArguments([secrets.token_hex(), {
            "title": QCoreApplication.translate("CentralWidget", "{{signal}} emitted").replace("{{signal}}", self._signal.name),
            "body": arg_text,
        }])
        QDBusConnection.sessionBus().asyncCall(msg)


class _ServicesTableColumns:
    NAME = 0
    ACTIVATABLE = 1
    PROCESS = 2
    USER = 3


class CentralWidget(QWidget, Ui_CentralWidget):
    def __init__(self, env: "Environment", main_window: "MainWindow", connection: "Connection") -> None:
        super().__init__(main_window)

        self.setupUi(self)

        self._env = env
        self.connection = connection
        self._main_window = main_window
        self._current_service: "Service" | None = None
        self._signal_listener = {}

        self.service_search_edit.textChanged.connect(self._update_service_table_visibility)
        self.services_table.cellDoubleClicked.connect(self._service_clicked)
        self.refresh_services_button.clicked.connect(self._refresh_services)

        self.object_search_edit.textChanged.connect(self._update_object_tree_search)
        self.object_tree.itemDoubleClicked.connect(self._tree_item_double_clicked)
        self.refresh_object_tree_button.clicked.connect(self._refresh_object_tree)
        self.add_object_path_button.clicked.connect(self._add_object_path_button_clicked)

        self.clear_log_edit_button.clicked.connect(lambda: self.log_edit.setPlainText(""))

        self.services_table.contextMenuEvent = self._services_table_context_menu
        self.object_tree.contextMenuEvent = self._object_tree_context_menu

        self.services_table.horizontalHeader().setSectionResizeMode(_ServicesTableColumns.NAME, QHeaderView.ResizeMode.Stretch)
        self.services_table.verticalHeader().setVisible(False)

        self._update_service_table()
        self._update_object_tree_enabled()

        if self.connection.get_error_message() is not None:
            self.add_log_error(QCoreApplication.translate("CentralWidget", "An error occurred while retrieving the data for this connection: {{error}}").replace("{{error}}", self.connection.get_error_message()))

    def _update_service_table(self) -> None:
        clear_table_widget(self.services_table)

        for row, service in enumerate(self.connection.service_list):
            self.services_table.insertRow(row)

            name_item = QTableWidgetItem(service.name)
            name_item.setToolTip(service.name)
            name_item.setFlags(name_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.services_table.setItem(row, _ServicesTableColumns.NAME, name_item)

            if service.activatable:
                activatable_item = QTableWidgetItem(QCoreApplication.translate("CentralWidget", "Yes"))
            else:
                activatable_item = QTableWidgetItem(QCoreApplication.translate("CentralWidget", "No"))
            activatable_item.setToolTip(activatable_item.text())
            activatable_item.setFlags(activatable_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.services_table.setItem(row, _ServicesTableColumns.ACTIVATABLE, activatable_item)

            if service.pid is not None:
                if service.process_name is None:
                    pid_item = QTableWidgetItem(str(service.pid))
                else:
                    pid_item = QTableWidgetItem(f"{service.process_name} ({service.pid})")

                pid_item.setToolTip(pid_item.text())
            else:
                pid_item = QTableWidgetItem("")
            pid_item.setFlags(pid_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.services_table.setItem(row, _ServicesTableColumns.PROCESS, pid_item)

            user_item = QTableWidgetItem(service.user_name)
            user_item.setToolTip(service.user_name)
            user_item.setFlags(user_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.services_table.setItem(row, _ServicesTableColumns.USER, user_item)

        self._update_service_table_visibility()

    def _refresh_services(self) -> None:
        self.connection.reload_services()
        self._update_service_table()

        if self.connection.get_error_message() is not None:
            self.add_log_error(QCoreApplication.translate("CentralWidget", "An error occurred while retrieving the data for this connection: {{error}}").replace("{{error}}", self.connection.get_error_message()))

    def _update_service_table_visibility(self) -> None:
        search_text = self.service_search_edit.text().lower().strip()

        for row in range(self.services_table.rowCount()):
            if search_text in self.services_table.item(row, _ServicesTableColumns.NAME).text().lower():
                self.services_table.showRow(row)
            else:
                self.services_table.hideRow(row)

    def _create_object_item(self, object_path: str, interface_list: list["Interface"]) -> QTableWidgetItem:
        object_item = QTreeWidgetItem(self.object_tree)
        object_item.setText(0, object_path)

        for interface in interface_list:
            interface_item = QTreeWidgetItem()
            interface_item.setText(0, interface.name)
            object_item.addChild(interface_item)

            if len(interface.methods) != 0:
                methods_item = QTreeWidgetItem()
                methods_item.setText(0, QCoreApplication.translate("CentralWidget", "Methods"))
                for method in interface.methods:
                    methods_item.addChild(_MethodItem(self, method))
                interface_item.addChild(methods_item)

            if len(interface.properties) != 0:
                property_item = QTreeWidgetItem()
                property_item.setText(0, QCoreApplication.translate("CentralWidget", "Properties"))
                for prop in interface.properties:
                    property_item.addChild(_PropertyItem(self, prop))
                interface_item.addChild(property_item)

            if len(interface.signals) != 0:
                signal_item = QTreeWidgetItem()
                signal_item.setText(0, QCoreApplication.translate("CentralWidget", "Signals"))
                for signal in interface.signals:
                    signal_item.addChild(_SignalItem(self, signal))
                interface_item.addChild(signal_item)

        return object_item

    def _update_object_tree(self, service: "Service") -> None:
        self.object_search_edit.setText("")
        self.object_tree.clear()
        for key, value in service.objects.items():
            self.object_tree.addTopLevelItem(self._create_object_item(key, value))

    def _search_object_items(self, top_item: QTreeWidgetItem, search_text: str) -> None:
        if top_item.childCount() == 0:
            top_item.setHidden(search_text != "")
            return

        item_found = False
        for interface_pos in range(top_item.childCount()):
            interface_item = top_item.child(interface_pos)
            interface_found = False
            for type_pos in range(interface_item.childCount()):
                type_item = interface_item.child(type_pos)
                type_found = False
                for object_pos in range(type_item.childCount()):
                    object_item: _ObjectItem = type_item.child(object_pos)
                    if search_text in object_item.name.lower():
                        object_item.setHidden(False)
                        object_item.setExpanded(True)
                        item_found = True
                        type_found = True
                        interface_found = True
                    else:
                        object_item.setHidden(True)
                type_item.setHidden(not type_found)
            interface_item.setHidden(not interface_found)
        top_item.setHidden(not item_found)

    def _update_object_tree_search(self) -> None:
        search_text = self.object_search_edit.text().lower()
        for pos in range(self.object_tree.topLevelItemCount()):
            top_item = self.object_tree.topLevelItem(pos)
            self._search_object_items(top_item, search_text)

    def _services_table_context_menu(self, event: QContextMenuEvent) -> None:
        row = self.services_table.currentRow()

        if row == -1:
            return

        service = self.connection.service_list[row]

        menu = QMenu(self)

        copy_menu = menu.addMenu(QCoreApplication.translate("CentralWidget", "Copy"))
        copy_menu.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))

        copy_name_action = QAction(QCoreApplication.translate("CentralWidget", "Name"), self)
        copy_name_action.triggered.connect(lambda: QApplication.clipboard().setText(service.name))
        copy_menu.addAction(copy_name_action)

        if service.process_name is not None:
            copy_process_name_action = QAction(QCoreApplication.translate("CentralWidget", "Process name"), self)
            copy_process_name_action.triggered.connect(lambda: QApplication.clipboard().setText(service.process_name))
            copy_menu.addAction(copy_process_name_action)

        if service.pid is not None:
            copy_pid_action = QAction(QCoreApplication.translate("CentralWidget", "PID"), self)
            copy_pid_action.triggered.connect(lambda: QApplication.clipboard().setText(str(service.pid)))
            copy_menu.addAction(copy_pid_action)

        if service.user_name is not None:
            copy_user_action = QAction(QCoreApplication.translate("CentralWidget", "User"), self)
            copy_user_action.triggered.connect(lambda: QApplication.clipboard().setText(service.user_name))
            copy_menu.addAction(copy_user_action)

        if service.pid is not None and is_scheme_supported("jdsystemmonitor"):
            menu.addSeparator()

            process_properties_action = QAction(QCoreApplication.translate("CentralWidget", "Process properties"), self)
            process_properties_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
            process_properties_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(f"jdsystemmonitor:ProcessDialog/{service.pid}")))
            menu.addAction(process_properties_action)

        menu.popup(event.globalPos())

    def _service_clicked(self, row: int) -> None:
        service = self.connection.service_list[row]

        error_list = service.load()

        for err in error_list:
            self.add_log_error(err)

        self._update_object_tree(service)
        self._current_service = service
        self._update_object_tree_enabled()

    def _refresh_object_tree(self) -> None:
        self._current_service.load()
        self._update_object_tree(self._current_service)

    def _update_object_tree_enabled(self) -> None:
        enabled = self._current_service is not None
        self.object_search_edit.setReadOnly(not enabled)
        self.refresh_object_tree_button.setEnabled(enabled)
        self.add_object_path_button.setEnabled(enabled)

    def _tree_item_double_clicked(self, item: QTreeWidgetItem) -> None:
        if isinstance(item, _MethodItem):
            item.call_method()

        if isinstance(item, _PropertyItem):
            item.get_value()

        if isinstance(item, _SignalItem):
            item.connect_or_disconnect()

    def _object_tree_context_menu(self, event: QContextMenuEvent) -> None:
        if self._current_service is None:
            return

        item = self.object_tree.itemAt(event.pos())

        menu = QMenu(self)

        if item is not None:
            copy_action = QAction(QCoreApplication.translate("CentralWidget", "Copy"), self)
            copy_action.triggered.connect(lambda: QApplication.clipboard().setText(item.text(0)))
            copy_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
            menu.addAction(copy_action)

            menu.addSeparator()

            if isinstance(item, _MethodItem) or isinstance(item, _PropertyItem) or isinstance(item, _SignalItem):
                for action in item.get_context_menu_actions():
                    menu.addAction(action)
                menu.addSeparator()

        refresh_action = QAction(QCoreApplication.translate("CentralWidget", "Refresh"), self)
        refresh_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh))
        menu.addAction(refresh_action)

        menu.popup(QCursor.pos())

    def _add_object_path_button_clicked(self) -> None:
        if self._current_service is None:
            return

        object_path = QInputDialog.getText(self, QCoreApplication.translate("CentralWidget", "Add object path"), QCoreApplication.translate("CentralWidget", "If this service has a object path that is not found trough introspection, you cann add it here"))[0].strip()

        if object_path == "":
            return

        interfaces, error_list = self._current_service.add_object_path(object_path)

        for err in error_list:
            self.add_log_error(err)

        if interfaces is None:
            QMessageBox.critical(self, QCoreApplication.translate("CentralWidget", "Path not loaded"), QCoreApplication.translate("CentralWidget", "The given object path could not be loaded"))
        else:
            self.object_tree.addTopLevelItem(self._create_object_item(object_path, interfaces))

    def call_method(self, method: "Method", arguments: list["DBusValue"], record_macro: bool) -> None:
        if record_macro:
            self._main_window.macro_manager.record_action(CallAction.from_message(method, arguments))

        self.add_log_text(QCoreApplication.translate("CentralWidget", "Calling {{method}}").replace("{{method}}", method.name))

        call = method.get_method_call()

        dbus_arguments: list[Any] = []
        for arg in arguments:
            dbus_arguments.append(arg.get_value())

        call.setArguments(dbus_arguments)
        result = self.connection.connection.call(call)

        if result.errorName() != "":
            self.add_log_error(format_dbus_error(result))
            return

        if len(result.arguments()) != len(method.return_types):
            self.add_log_error(QCoreApplication.translate("CentralWidget", "Invalid introspect data"))
            return

        return_text: list[str] = []

        for i in range(len(method.return_types)):
            if method.return_types[i] is not None and method.return_types[i].type_const == DBusTypeEnum.OBJECT_PATH:
                object_path = result.arguments()[i]

                match self._env.settings.get("methodReturnsObjectPath"):
                    case "add":
                        add_object_path = True
                    case "ask":
                        add_object_path = QMessageBox.question(self, QCoreApplication.translate("CentralWidget", "Add object path"), QCoreApplication.translate("CentralWidget", "This method returned the object path {{path}}. Do you want to add it to the list?").replace("{{path}}", object_path)) == QMessageBox.StandardButton.Yes
                    case _:
                        add_object_path = False

                if add_object_path:
                    interfaces, error_list = method.interface.service.add_object_path(object_path)

                    for err in error_list:
                        self.add_log_error(err)

                    if interfaces is not None:
                        self.object_tree.addTopLevelItem(self._create_object_item(object_path, interfaces))

            value = DBusValue.create(method.return_types[i], result.arguments()[i])
            return_text.append(value.get_printable_text())

        if len(return_text) == 0:
            self.add_log_text(QCoreApplication.translate("CentralWidget", "No return value"))
        else:
            self.add_log_text(", ".join(return_text))

    def get_property_value(self, prop: "Property", record_macro: bool) -> None:
        if record_macro:
            self._main_window.macro_manager.record_action(PropertyAction.from_property(prop, "get", None))

        self.add_log_text(QCoreApplication.translate("CentralWidget", "Get value of Property {{property}}").replace("{{property}}", prop.name))

        value, err = prop.get_value()

        if err is not None:
            self.add_log_error(err)
            return

        self.add_log_text(value.get_printable_text())

    def set_property_value(self, prop: "Property", value: "DBusValue", record_macro: bool) -> None:
        if record_macro:
            self._main_window.macro_manager.record_action(PropertyAction.from_property(prop, "set", value))

        err = prop.set_value(value.get_value())

        if err is None:
            self.add_log_text(QCoreApplication.translate("CentralWidget", "Set value of Property {{property}} to {{value}}").replace("{{property}}", prop.name).replace("{{value}}", value.get_printable_text()))
        else:
            self.add_log_error(QCoreApplication.translate("CentralWidget", "Failed to set Property {{property}} to {{value}}: {{error}}").replace("{{property}}", prop.name).replace("{{value}}", value.get_printable_text()).replace("{{error}}", err))

    def connect_signal(self, signal: "Signal", record_macro: bool) -> None:
        if record_macro:
            self._main_window.macro_manager.record_action(SignalAction.from_signal(signal, "connect"))

        if not signal.is_connected:
            listener = _SignalListener(self, signal)
            self.connection.connection.connect(signal.interface.service.name, signal.interface.object_path, signal.interface.name, signal.name, listener.signal_slot)
            self.add_log_text(QCoreApplication.translate("CentralWidget", "Connected to Signal {{signal}}").replace("{{signal}}", signal.name))
            signal.is_connected = True
            self._signal_listener[signal.get_id()] = listener

    def disconnect_signal(self,  signal: "Signal", record_macro: bool) -> None:
        if record_macro:
            self._main_window.macro_manager.record_action(SignalAction.from_signal(signal, "disconnect"))

        listener = _SignalListener(self, signal)
        self.connection.connection.disconnect(signal.interface.service.name, signal.interface.object_path, signal.interface.name, signal.name, listener.signal_slot)
        self.add_log_text(QCoreApplication.translate("CentralWidget", "Disconnected from Signal {{signal}}").replace("{{signal}}", signal.name))
        signal.is_connected = False

        if signal.get_id() in self._signal_listener:
            del self._signal_listener[signal.get_id()]

    def add_log_error(self, text: str) -> None:
        error_format = QTextCharFormat()
        error_format.setForeground(QColor("red"))

        cursor = self.log_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        default_format = cursor.charFormat()
        cursor.setCharFormat(error_format)
        cursor.insertText(text.removesuffix("\n"), error_format)
        cursor.insertText("\n\n", default_format)
        self.log_edit.moveCursor(cursor.MoveOperation.End)

    def add_log_text(self, text: str) -> None:
        cursor = self.log_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text.removesuffix("\n") + "\n\n")
        self.log_edit.moveCursor(cursor.MoveOperation.End)

    def _execute_call_action(self, action: "CallAction", interface: "Interface") -> None:
        method = interface.get_method_by_name(action.method_name)
        if method is None:
            self.add_log_error(QCoreApplication.translate("CentralWidget", "Method {{method}} was not found").replace("{{method}}", action.method_name))
            return

        self.call_method(method, action.parameter_list, False)

    def _execute_property_action(self, action: PropertyAction, interface: "Interface") -> None:
        prop =  interface.get_property_by_name(action.property_name)
        if prop is None:
            self.add_log_error(QCoreApplication.translate("CentralWidget", "Property {{property}} was not found").replace("{{property}}", action.property_name))
            return

        match action.property_method:
            case "get":
                self.get_property_value(prop, False)
            case "set":
                self.set_property_value(prop, action.property_value, False)

    def _execute_signal_action(self, action: SignalAction, interface: "Interface") -> None:
        signal = interface.get_signal_by_name(action.signal_name)
        if signal is None:
            self.add_log_error(QCoreApplication.translate("CentralWidget", "Signal {{signal}} was not found").replace("{{signal}}", action.signal_name))
            return

        match action.signal_action:
            case "connect":
                self.connect_signal(signal, False)
            case "disconnect":
                self.disconnect_signal(signal, False)

    def _execute_emit_action(self, action: "EmitAction") -> None:
        signal_args: list[Any] = []
        print_args: list[str] = []
        for arg in action.argument_list:
            signal_args.append(arg.get_value())
            print_args.append(arg.get_printable_text())

        signal = QDBusMessage.createSignal(action.emit_path, action.emit_interface, action.emit_name)
        signal.setArguments(signal_args)

        if self.connection.connection.send(signal):
            self.add_log_text(QCoreApplication.translate("CentralWidget", "Signal was emited on path {{path}} and interface {{interface}} with these arguments: {{arguments}}").replace("{{path}}", action.emit_path).replace("{{interface}}", f"{action.emit_interface}.{action.emit_name}").replace("{{arguments}}", str(print_args)))
        else:
            self.add_log_error(QCoreApplication.translate("CentralWidget", "Could not emit Signal on path {{path}} and interface {{interface}} with these arguments: {{arguments}}").replace("{{path}}", action.emit_path).replace("{{interface}}", f"{action.emit_interface}.{action.emit_name}").replace("{{arguments}}", str(print_args)))

    def execute_action(self, action: "ActionBase") -> None:
        if action.action_type == "emit":
            self._execute_emit_action(action)
            return

        service = self.connection.get_service_by_name(action.service_name)
        if service is None:
            self.add_log_error(QCoreApplication.translate("CentralWidget", "Service {{service}} was not found").replace("{{service}}", action.service_name))
            return

        if not service.is_loaded:
            service.load()

        interface = service.get_interface_by_name(action.object_path, action.interface_name)
        if interface is None:
            self.add_log_error(QCoreApplication.translate("CentralWidget", "Interface {{interface}} was not found on {{path}}").replace("{{interface}}", action.interface_name).replace("{{path}}", action.object_path))
            return

        match action.action_type:
            case "call":
                self._execute_call_action(action, interface)
            case "property":
                self._execute_property_action(action, interface)
            case "signal":
                self._execute_signal_action(action, interface)
