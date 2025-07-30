from PyQt6.QtWidgets import QWidget, QComboBox, QLineEdit, QHBoxLayout
from ...types.DBusValue import BytearraySource
from PyQt6.QtCore import QCoreApplication
from .BrowseButton import BrowseButton


class BytearrayInput(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self._source_box = QComboBox()
        self._source_box.addItem(QCoreApplication.translate("BytearrayInput", "String"), BytearraySource.STRING)
        self._source_box.addItem(QCoreApplication.translate("BytearrayInput", "File"), BytearraySource.FILE)

        self._source_box.currentIndexChanged.connect(self._source_box_changed)

        self._main_layout = QHBoxLayout()
        self._main_layout.addWidget(self._source_box)
        self._main_layout.addWidget(QLineEdit())

        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self._main_layout)

    def _source_box_changed(self) -> None:
        self._main_layout.takeAt(1).widget().setParent(None)
        match self._source_box.currentData():
            case BytearraySource.STRING:
                self._main_layout.addWidget(QLineEdit())
            case BytearraySource.FILE:
                self._main_layout.addWidget(BrowseButton(self))

    def get_bytearray_data(self) -> None:
        match self._source_box.currentData():
            case BytearraySource.STRING:
                return {"type": BytearraySource.STRING, "string": self._main_layout.itemAt(1).widget().text()}
            case BytearraySource.FILE:
                return {"type": BytearraySource.FILE, "path": self._main_layout.itemAt(1).widget().get_file_path()}

    def get_validation_error(self) -> str | None:
        if self._source_box.currentData() == BytearraySource.FILE:
            return self._main_layout.itemAt(1).widget().get_validation_error()
        else:
            return None
