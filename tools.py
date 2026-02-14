from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedLayout,
    QButtonGroup,
    QVBoxLayout,
)
from PySide6.QtCore import Signal, QObject, Qt


class ToolCollection:
    def __init__(self, model):
        self.tool_indexes = [
            (0, QWidget()),
            (1, AddMonth(model)),
            (2, AddTrans(model)),
            (3, DelTrans(model)),
        ]
        self.tools = {"Add Month": 1, "Add Transaction": 2, "Delete Transaction": 3}
        self.model = model
        self.workspace = Workspace(self)
        self.toolbar = ToolBar(self)


class ToolBar(QWidget):
    def __init__(self, tool_collection):
        super().__init__()
        self.tool_collection = tool_collection
        self.buttons = ToolButtons(tool_collection)
        tool_layout = QVBoxLayout(self)
        for button in self.buttons.buttons():
            tool_layout.addWidget(button)


class ToolButtons(QButtonGroup):
    def __init__(self, tool_collection):
        self.tool_collection = tool_collection
        self.workspace = self.tool_collection.workspace
        self.button_now = ""
        super().__init__()
        self.setExclusive(True)
        for tool in self.tool_collection.tools:
            button = QPushButton(tool)
            button.setCheckable(True)
            self.addButton(button)
        self.buttonClicked.connect(self.on_click)

    def on_click(self, button):
        if self.button_now == button.text():
            button.setChecked(False)
            self.workspace.clear()
            self.button_now = ""
        else:
            self.workspace.show_tool(button.text())
            self.button_now = button.text()


class Workspace(QStackedLayout):
    def __init__(self, tool_collection):
        self.tool_collection = tool_collection
        super().__init__()
        for index, tool in self.tool_collection.tool_indexes:
            self.insertWidget(index, tool)

    def clear(self):
        self.setCurrentIndex(0)

    def show_tool(self, label):
        self.setCurrentIndex(self.tool_collection.tools[label])


class AddMonth(QWidget):
    def __init__(self, model):
        self.model = model
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tool_layout = QFormLayout(self)
        tool_layout.addWidget(QLabel("Add Month", alignment=Qt.AlignmentFlag.AlignTop))
        self.name_edit = QLineEdit()
        save_button = QPushButton("Save")

        tool_layout.addRow("name", self.name_edit)
        tool_layout.addRow(save_button)
        save_button.clicked.connect(self.save)

    def save(self):
        name = self.name_edit.text()[:]
        self.name_edit.clear()
        self.model.create_month(name, None)
        signals.upd_main_signal.emit()


class AddTrans(QWidget):
    def __init__(self, model):
        self.model = model
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tool_layout = QFormLayout(self)
        tool_layout.addWidget(
            QLabel("Add Transaction", alignment=Qt.AlignmentFlag.AlignTop)
        )
        self.name_edit = QLineEdit()
        self.q_edit = QLineEdit()
        self.month_name_edit = QLineEdit()
        save_button = QPushButton("Save")

        tool_layout.addRow("name", self.name_edit)
        tool_layout.addRow("quantity", self.q_edit)
        tool_layout.addRow("month_name", self.month_name_edit)
        tool_layout.addRow(save_button)
        save_button.clicked.connect(self.save)

    def save(self):
        name = self.name_edit.text()[:]
        self.name_edit.clear()
        q = float(self.q_edit.text())
        self.q_edit.clear()
        month_name = self.month_name_edit.text()[:]
        self.month_name_edit.clear()
        self.model.create_transaction(name, q * 100, month_name)
        signals.upd_months_signal.emit()


class DelTrans(QWidget):
    def __init__(self, model):
        self.model = model
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tool_layout = QFormLayout(self)
        tool_layout.addWidget(
            QLabel("Delete Transaction", alignment=Qt.AlignmentFlag.AlignTop)
        )
        self.name_edit = QLineEdit()
        delete_button = QPushButton("Delete")
        tool_layout.addRow("name", self.name_edit)
        tool_layout.addRow(delete_button)
        delete_button.clicked.connect(self.delete)

    def delete(self):
        name = self.name_edit.text()[:]
        self.name_edit.clear()
        self.model.delete_transaction(name)
        signals.upd_months_signal.emit()


class Signals(QObject):
    upd_months_signal = Signal()
    upd_main_signal = Signal()


signals = Signals()
