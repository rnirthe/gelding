from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QStackedLayout,
    QButtonGroup,
    QVBoxLayout,
)
from PySide6.QtCore import QRegularExpression, Signal, QObject, Qt


class ToolCollection:
    def __init__(self, model):
        self.signals = Signals()
        self.euroValidator = EuroValidator()
        self.tool_indexes = [
            (0, WorkspaceItem(model, self)),
            (1, AddMonth(model, self)),
            (2, AddTrans(model, self)),
            (3, DelTrans(model, self)),
        ]
        self.tools = {"Add Month": 1, "Add Transaction": 2, "Delete Transaction": 3}
        self.model = model
        self.workspace = Workspace(self)
        self.toolbar = ToolBar(self)

    def rem_spacing(self, layout):
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.layout():
                self.rem_spacing(item.layout())
            elif item.widget():
                widget = item.widget()
                if widget.layout():
                    self.rem_spacing(widget.layout())


class ToolBar(QWidget):
    def __init__(self, tc):
        super().__init__()
        self.tc = tc
        self.buttons = ToolButtons(tc)
        tool_layout = QVBoxLayout(self)
        for button in self.buttons.buttons():
            tool_layout.addWidget(button)
        tool_layout.addStretch()


class ToolButtons(QButtonGroup):
    def __init__(self, tc):
        super().__init__()
        self.tc = tc
        self.workspace = self.tc.workspace
        self.button_now = QPushButton("")
        self.setExclusive(False)
        for tool in self.tc.tools:
            button = ToolButton(tool)
            button.setCheckable(True)
            self.addButton(button)
        self.buttonClicked.connect(self.on_click)

    def on_click(self, button):
        if self.button_now.text() == button.text():
            button.setChecked(False)
            self.workspace.clear()
            self.button_now = QPushButton("")
        else:
            self.button_now.setChecked(False)
            button.setChecked(True)
            self.workspace.show_tool(button.text())
            self.button_now = button


class Workspace(QStackedLayout):
    def __init__(self, tc):
        super().__init__()
        self.tc = tc
        for index, tool in self.tc.tool_indexes:
            self.insertWidget(index, tool)

    def clear(self):
        self.setCurrentIndex(0)

    def show_tool(self, label):
        self.setCurrentIndex(self.tc.tools[label])


class WorkspaceItem(QWidget):
    def __init__(self, model, tc):
        super().__init__()
        self.model = model
        self.tc = tc
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


class AddMonth(WorkspaceItem):
    def __init__(self, model, tc):
        super().__init__(model, tc)
        tool_layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        save_button = QPushButton("Save")

        tool_layout.addRow("Name", self.name_edit)
        tool_layout.addRow(save_button)
        save_button.clicked.connect(self.save)

    def save(self):
        name = self.name_edit.text()[:]
        self.name_edit.clear()
        self.model.create_month(name, None)
        self.tc.signals.upd_main_signal.emit()


class AddTrans(WorkspaceItem):
    def __init__(self, model, tc):
        super().__init__(model, tc)
        tool_layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        self.quantity_edit = QLineEdit()
        self.quantity_edit.setValidator(self.tc.euroValidator)
        self.month_name_edit = QLineEdit()
        save_button = QPushButton("Save")

        tool_layout.addRow("Name", self.name_edit)
        tool_layout.addRow("Quantity", self.quantity_edit)
        tool_layout.addRow("Month Name", self.month_name_edit)
        tool_layout.addRow(save_button)
        save_button.clicked.connect(self.save)

    def save(self):
        name = self.name_edit.text()[:]
        self.name_edit.clear()
        quantity = float(self.quantity_edit.text())
        self.quantity_edit.clear()
        month_name = self.month_name_edit.text()[:]
        self.month_name_edit.clear()
        self.model.create_transaction(name, quantity, month_name)
        self.tc.signals.upd_months_signal.emit()


class DelTrans(WorkspaceItem):
    def __init__(self, model, tc):
        super().__init__(model, tc)
        tool_layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        delete_button = QPushButton("Delete")
        tool_layout.addRow("Name", self.name_edit)
        tool_layout.addRow(delete_button)
        delete_button.clicked.connect(self.delete)

    def delete(self):
        name = self.name_edit.text()[:]
        self.name_edit.clear()
        self.model.delete_transaction(name)
        self.tc.signals.upd_months_signal.emit()


class Signals(QObject):
    upd_months_signal = Signal()
    upd_main_signal = Signal()


class ToolButton(QPushButton):
    def __init__(self, name):
        super().__init__(name)


class EuroValidator(QRegularExpressionValidator):
    def __init__(self):
        # euro_regex = QRegularExpression("(?<!\\w)\\d*\\.\\d{0,2}(?!.)")
        euro_regex = QRegularExpression(r"^-?\d+\.?\d{2}$")
        super().__init__(euro_regex)
