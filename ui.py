from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget,
    QStackedLayout,
    QGridLayout,
    QListWidget,
    QLabel,
    QLineEdit,
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QScrollArea,
)
from PySide6.QtCore import QRegularExpression, Qt, Signal, QObject


class Signals(QObject):
    upd_transactions_signal = Signal()
    upd_months_signal = Signal()


signals = Signals()


class MainWindow(QWidget):
    def __init__(self, ts):
        self.ts = ts
        super().__init__()
        self.setWindowTitle("Gelding")
        self.mainArea = QScrollArea()
        self.mainArea.setWidgetResizable(True)
        self.mainArea.setWidget(MonthsWidget(self.ts))
        self.arena = ArenaLayout(self.ts)
        self.toolView = ToolViewWidget(self.arena)
        self.setLayout(Layout(self.mainArea, self.toolView, self.arena))

    def closeEvent(self, event):
        self.ts.exit(event)


class Layout(QGridLayout):
    def __init__(self, mainArea, toolView, arena):
        super().__init__()
        self.setRowStretch(0, 5)
        self.setRowStretch(1, 8)
        self.setColumnStretch(0, 5)
        self.setColumnStretch(1, 8)
        self.addWidget(mainArea, 0, 1, 2, 1)
        self.addWidget(toolView, 0, 0)
        self.addLayout(arena, 1, 0)


class ToolViewWidget(QListWidget):
    def __init__(self, arena):
        self.arena = arena
        super().__init__()
        for tool in self.arena.tool_dict:
            self.addItem(tool)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.itemSelectionChanged.connect(self.on_selection_change)

    def on_selection_change(self):
        items = self.selectedItems()
        if items != []:
            self.arena.show_tool(items[0].text())
        else:
            self.arena.clear()


class ArenaLayout(QStackedLayout):
    def __init__(
        self,
        ts,
    ):
        self.ts = ts
        super().__init__()
        self.insertWidget(0, QWidget())
        self.insertWidget(1, AddTrans(ts))
        self.insertWidget(2, DelTrans(ts))
        self.tool_dict = {"Add Transaction": 1, "Delete Transaction": 2}

    def clear(self):
        self.setCurrentIndex(0)

    def show_tool(self, label):
        self.setCurrentIndex(self.tool_dict[label])


class AddTrans(QWidget):
    def __init__(self, ts):
        self.ts = ts
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
        q = int(self.q_edit.text())
        self.q_edit.clear()
        month_name = self.month_name_edit.text()[:]
        self.month_name_edit.clear()
        self.ts.create_transaction(name, q, month_name)
        signals.upd_transactions_signal.emit()


class DelTrans(QWidget):
    def __init__(self, ts):
        self.ts = ts
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
        self.ts.delete_transaction(name)
        signals.upd_transactions_signal.emit()


class MonthsWidget(QWidget):
    def __init__(self, ts):
        self.ts = ts
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        for m in self.ts.get_all_months():
            layout.addWidget(MonthItem(self.ts, m))
        layout.addStretch()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class MonthItem(QWidget):
    def __init__(self, ts, month):
        self.ts = ts
        self.month = month
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.init_header()
        self.init_content()
        signals.upd_transactions_signal.connect(self.upd_transactions)
        signals.upd_months_signal.connect(self.upd_months)

    def init_header(self):
        self.header = QPushButton()
        self.header.setText(self.month.name)
        self.header.setCheckable(True)
        self.header.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.header.clicked.connect(self.on_toggled)
        if self.month.order >= self.ts.get_current_month():
            self.header.setChecked(True)
        self.main_layout.addWidget(self.header)

    def init_content(self):
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(0)
        if self.month.order < self.ts.get_current_month():
            self.content.setVisible(False)
        self.init_balance()
        self.init_transactions()
        self.init_footer()
        self.main_layout.addWidget(self.content)

    def upd_months(self):
        self.main_layout.removeWidget(self.header)
        self.main_layout.removeWidget(self.content)
        self.init_header()
        self.init_content()

    def init_balance(self):
        if self.month.order == self.ts.get_current_month():
            self.bal = ShinyWidget()
            bal_layout = QHBoxLayout(self.bal)
            bal_layout.addWidget(QLabel("Current balance:"))
            bal_layout.addStretch()
            bal_layout.addWidget(QLabel("€"), alignment=Qt.AlignmentFlag.AlignRight)

            bal_edit = QLineEdit(
                f"{self.ts.get_current_balance() / 100}",
                alignment=Qt.AlignmentFlag.AlignRight,
            )
            bal_edit.setMinimumWidth(1)
            bal_edit.setValidator(
                QRegularExpressionValidator(
                    QRegularExpression("(?<!\\w)\\d*\\.\\d{0,2}(?!.)")
                )
            )
            bal_edit.textEdited.connect(self.on_bal_change)
            bal_edit.returnPressed.connect(self.on_return_pressed)
            bal_edit.editingFinished.connect(bal_edit.clearFocus)

            bal_layout.addWidget(
                bal_edit,
                alignment=Qt.AlignmentFlag.AlignRight,
            )
            self.content_layout.addWidget(self.bal)
        if self.month.order > self.ts.get_current_month():
            self.bal = ShinyWidget()
            bal_layout = QHBoxLayout(self.bal)
            bal_layout.addWidget(QLabel("Predicted balance:"))
            bal_layout.addStretch()
            bal_layout.addWidget(QLabel("€"), alignment=Qt.AlignmentFlag.AlignRight)
            bal_layout.addWidget(
                QLabel(f"{self.ts.get_total_prev(self.month) / 100}"),
                alignment=Qt.AlignmentFlag.AlignRight,
            )
            self.content_layout.addWidget(self.bal)

    def init_transactions(self):
        self.transactions = QWidget()
        self.transactions_layout = QVBoxLayout(self.transactions)
        transactions = sorted(self.month.trans_links, key=lambda t: t.q, reverse=True)
        for t in transactions:
            self.trans = QWidget()
            trans_layout = QHBoxLayout(self.trans)
            trans_layout.addWidget(QLabel(f"{t.name}:"))
            trans_layout.addWidget(
                QLabel(f"€{t.q / 100}"), alignment=Qt.AlignmentFlag.AlignRight
            )
            self.transactions_layout.addWidget(self.trans)
        self.content_layout.addWidget(self.transactions)

    def upd_transactions(self):
        self.content_layout.removeWidget(self.transactions)
        self.content_layout.removeWidget(self.footer)
        self.init_transactions()
        self.init_footer()

    def init_footer(self):
        self.footer = QWidget()
        self.footer_layout = QHBoxLayout(self.footer)
        self.footer_layout.addWidget(
            QLabel(
                f"=================\n€{self.month.get_total() / 100}",
                alignment=Qt.AlignmentFlag.AlignRight,
            )
        )
        self.content_layout.addWidget(self.footer)

    def upd_footer_label(self):
        self.content_layout.removeWidget(self.footer)
        self.init_footer()

    def on_toggled(self, expanded: bool):
        self.content.setVisible(expanded)

    def on_bal_change(self, balance):
        self.temp_bal = balance

    def on_return_pressed(self):
        self.ts.change_balance(int(float(self.temp_bal) * 100))
        signals.upd_months_signal.emit()


class ShinyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
