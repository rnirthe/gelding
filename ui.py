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
from PySide6.QtCore import Qt

from tools import ToolCollection


class MainWindow(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Gelding")
        self.tc = ToolCollection(model)
        self.mainArea = MainArea(self.model, self.tc)
        self.toolbar = self.tc.toolbar
        self.workspace = self.tc.workspace
        self.setLayout(Layout(self.tc, self.mainArea, self.toolbar, self.workspace))

    def closeEvent(self, event):
        self.model.save_and_close(event)


class Layout(QGridLayout):
    def __init__(self, tc, mainArea, toolbar, workspace):
        super().__init__()
        self.setContentsMargins(5, 5, 5, 5)
        self.setSpacing(5)
        self.setRowStretch(0, 5)
        self.setRowStretch(1, 8)
        self.setColumnStretch(0, 5)
        self.setColumnStretch(1, 8)
        self.addWidget(mainArea, 0, 1, 2, 1)
        self.addWidget(toolbar, 0, 0)
        self.addLayout(workspace, 1, 0)


class MainArea(QScrollArea):
    def __init__(self, model, tc):
        super().__init__()
        self.model = model
        self.tc = tc
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setViewportMargins(0, -9, 0, -9)
        self.contains = MonthsWidget(self.model, self.tc)
        self.setWidget(self.contains)
        self.tc.signals.upd_main_signal.connect(self.upd_main)

    def upd_main(self):
        self.takeWidget()
        self.contains = MonthsWidget(self.model, self.tc)
        self.setWidget(self.contains)


class MonthsWidget(QWidget):
    def __init__(self, model, tc):
        super().__init__()
        layout = QVBoxLayout(self)
        tc.rem_spacing(layout)
        layout.addSpacing(9)
        for m in model.months:
            layout.addWidget(
                MonthItem(model, tc, m),
                alignment=Qt.AlignmentFlag.AlignTop,
            )
        layout.addSpacing(9)
        layout.addStretch()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class MonthItem(QWidget):
    def __init__(self, model, tc, month):
        super().__init__()
        self.model = model
        self.tc = tc
        self.month = month
        self.main_layout = QVBoxLayout(self)
        self.tc.rem_spacing(self.main_layout)
        self.init_header()
        self.init_content()
        self.tc.signals.upd_months_signal.connect(self.upd_months)

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
            bal_layout.addWidget(QLabel("Current Balance:"))
            bal_layout.addStretch()
            bal_layout.addWidget(QLabel("€"), alignment=Qt.AlignmentFlag.AlignRight)

            bal_edit = QLineEdit(
                f"{self.model.current_balance}",
                alignment=Qt.AlignmentFlag.AlignRight,
            )
            bal_edit.setMinimumWidth(1)
            bal_edit.setValidator(self.tc.euroValidator)
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
            bal_layout.addWidget(QLabel("Predicted Balance:"))
            bal_layout.addStretch()
            bal_layout.addWidget(QLabel("€"), alignment=Qt.AlignmentFlag.AlignRight)
            bal_layout.addWidget(
                QLabel(f"{self.month.get_prev_month().get_total()}"),
                alignment=Qt.AlignmentFlag.AlignRight,
            )
            self.content_layout.addWidget(self.bal)

    def init_transactions(self):
        self.transactions = TWidget()
        self.transactions_layout = QVBoxLayout(self.transactions)
        self.tc.rem_spacing(self.transactions_layout)

        transactions = sorted(self.month.trans_links, key=lambda t: t.q, reverse=True)
        for t in transactions:
            self.trans = QWidget()
            trans_layout = QHBoxLayout(self.trans)
            self.tc.rem_spacing(trans_layout)
            trans_layout.addWidget(QLabel(f"{t.name}:"))
            trans_layout.addWidget(
                QLabel(f"€{t.q}"), alignment=Qt.AlignmentFlag.AlignRight
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
                f"€{self.month.get_total()}",
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
        self.model.set_current_balance(self.temp_bal)
        self.tc.signals.upd_months_signal.emit()


class BalanceLine(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


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
