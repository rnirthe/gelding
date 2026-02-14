from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import QRegularExpression, Qt

from tools import signals, ToolCollection


class MainWindow(QWidget):
    def __init__(self, model):
        self.model = model
        self.toolcollection = ToolCollection(model)
        super().__init__()
        self.setWindowTitle("Gelding")
        self.mainArea = MainArea(self.model)
        self.toolbar = self.toolcollection.toolbar
        self.workspace = self.toolcollection.workspace
        self.setLayout(Layout(self.mainArea, self.toolbar, self.workspace))

    def closeEvent(self, event):
        self.model.save_and_close(event)


class Layout(QGridLayout):
    def __init__(self, mainArea, toolView, useArea):
        super().__init__()
        self.setRowStretch(0, 5)
        self.setRowStretch(1, 8)
        self.setColumnStretch(0, 5)
        self.setColumnStretch(1, 8)
        self.addWidget(mainArea, 0, 1, 2, 1)
        self.addWidget(toolView, 0, 0)
        self.addLayout(useArea, 1, 0)


class MainArea(QScrollArea):
    def __init__(self, model):
        self.model = model
        super().__init__()
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setViewportMargins(0, -9, 0, -9)
        self.contains = MonthsWidget(model)
        self.setWidget(self.contains)
        signals.upd_main_signal.connect(self.upd_main)

    def upd_main(self):
        self.takeWidget()
        self.contains = MonthsWidget(self.model)
        self.setWidget(self.contains)


class MonthsWidget(QWidget):
    def __init__(self, model):
        self.model = model
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addSpacing(9)
        for m in self.model.months:
            layout.addWidget(
                MonthItem(self.model, m), alignment=Qt.AlignmentFlag.AlignTop
            )
        layout.addSpacing(9)
        layout.addStretch()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class MonthItem(QWidget):
    def __init__(self, model, month):
        self.model = model
        self.month = month
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        rem_spacing(self.main_layout)
        self.init_header()
        self.init_content()
        signals.upd_months_signal.connect(self.upd_months)

    def init_header(self):
        if self.month.order < self.model.current_month:
            self.header = PastMonthHead()
            self.header.setCheckable(True)
        else:
            self.header = FutureMonthHead()
            self.header.setCheckable(True)
            self.header.setChecked(True)
        self.header.setText(self.month.name)
        self.header.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.header.clicked.connect(self.on_toggled)
        self.main_layout.addWidget(self.header)

    def init_content(self):
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(0)
        if self.month.order < self.model.current_month:
            self.content.setVisible(False)
        self.init_balance()
        self.init_transactions()
        self.init_footer()
        self.main_layout.addWidget(self.content)

    def upd_months(self):
        self.main_layout.removeWidget(self.header)
        self.main_layout.removeWidget(self.content)
        self.header.deleteLater()
        self.content.deleteLater()
        self.init_header()
        self.init_content()

    def init_balance(self):
        if self.month.order == self.model.current_month:
            self.bal = BalanceLine()
            bal_layout = QHBoxLayout(self.bal)
            bal_layout.addWidget(QLabel("Current balance:"))
            bal_layout.addStretch()
            bal_layout.addWidget(QLabel("€"), alignment=Qt.AlignmentFlag.AlignRight)

            bal_edit = QLineEdit(
                f"{self.model.current_balance / 100}",
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
        if self.month.order > self.model.current_month:
            self.bal = BalanceLine()
            bal_layout = QHBoxLayout(self.bal)
            bal_layout.addWidget(QLabel("Predicted balance:"))
            bal_layout.addStretch()
            bal_layout.addWidget(QLabel("€"), alignment=Qt.AlignmentFlag.AlignRight)
            bal_layout.addWidget(
                QLabel(f"{self.month.get_prev_month().get_total() / 100}"),
                alignment=Qt.AlignmentFlag.AlignRight,
            )
            self.content_layout.addWidget(self.bal)

    def init_transactions(self):
        self.transactions = TWidget()
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

    def init_footer(self):
        self.footer = QWidget()
        self.footer_layout = QVBoxLayout(self.footer)
        self.footer_layout.addWidget(TotalLine())
        self.total = QWidget()
        self.total_layout = QHBoxLayout(self.total)
        self.total_layout.addWidget(
            QLabel(
                f"€{self.month.get_total() / 100}",
                alignment=Qt.AlignmentFlag.AlignRight,
            )
        )
        self.footer_layout.addWidget(self.total)
        self.content_layout.addWidget(self.footer)

    def upd_footer_label(self):
        self.content_layout.removeWidget(self.footer)
        self.init_footer()

    def on_toggled(self, expanded: bool):
        self.content.setVisible(expanded)

    def on_bal_change(self, balance):
        self.temp_bal = balance

    def on_return_pressed(self):
        self.model.current_balance = int(float(self.temp_bal) * 100)
        signals.upd_months_signal.emit()


class BalanceLine(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)


class TWidget(QWidget):
    def __init__(self):
        super().__init__()


class PastMonthHead(QPushButton):
    def __init__(self):
        super().__init__()


class FutureMonthHead(QPushButton):
    def __init__(self):
        super().__init__()


class TotalLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(2)


def rem_spacing(layout):
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.layout():
            rem_spacing(item.layout())
        elif item.widget():
            widget = item.widget()
            if widget.layout():
                rem_spacing(widget.layout())
