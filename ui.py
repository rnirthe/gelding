from pathlib import Path
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
    QToolButton,
    QPushButton,
    QScrollArea,
    QSizePolicy,
)
from PySide6.QtCore import Qt


class MainWindow(QWidget):
    def __init__(self, model, ts):
        self.model = model
        self.ts = ts
        super().__init__()
        self.setWindowTitle("Gelding")
        self.mainArea = QScrollArea()
        self.mainArea.setWidgetResizable(True)
        self.set_mainArea()
        self.arena = ArenaLayout(ts, self)
        self.toolView = ToolViewWidget(self.arena)
        self.setLayout(Layout(self.mainArea, self.toolView, self.arena))

    def set_mainArea(self):
        self.mainArea.setWidget(MonthsWidget(self.model, self.ts))

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
        main_window,
    ):
        self.ts = ts
        super().__init__()
        self.insertWidget(0, QWidget())
        self.insertWidget(1, AddTrans(ts, main_window))
        self.tool_dict = {"Add Transaction": 1}

    def clear(self):
        self.setCurrentIndex(0)

    def show_tool(self, label):
        self.setCurrentIndex(self.tool_dict[label])


class AddTrans(QWidget):
    def __init__(self, ts, main_window):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tool_layout = QFormLayout(self)
        tool_layout.addWidget(
            QLabel("Add Transaction", alignment=Qt.AlignmentFlag.AlignTop)
        )
        name_edit = QLineEdit()
        q_edit = QLineEdit()
        month_name_edit = QLineEdit()
        save_button = QPushButton("Save")

        def save():
            name = name_edit.text()[:]
            name_edit.clear()
            q = int(q_edit.text())
            q_edit.clear()
            month_name = month_name_edit.text()[:]
            month_name_edit.clear()
            ts.create_transaction(name, q, month_name, main_window)

        tool_layout.addRow("name", name_edit)
        tool_layout.addRow("quantity", q_edit)
        tool_layout.addRow("month_name", month_name_edit)
        tool_layout.addRow(save_button)
        save_button.clicked.connect(save)


class MonthsWidget(QWidget):
    def __init__(self, model, ts):
        self.model = model
        self.ts = ts
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        for m in self.model.months:
            layout.addWidget(MonthItem(self.model, m, self))
        layout.addStretch()

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class MonthItem(QWidget):
    def __init__(self, model, m, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.header = QPushButton()
        self.header.setText(m.name)
        self.header.setCheckable(True)
        self.header.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.header)
        layout.setSpacing(0)

        self.content = QWidget()
        content_layout = QVBoxLayout(self.content)
        content_layout.setSpacing(0)
        if m.order < model.current_month:
            self.content.setVisible(False)
        if m.order == model.current_month:
            content_layout.addWidget(
                QLabel(
                    f"Current balance: €{model.current_balance / 100}",
                    alignment=Qt.AlignmentFlag.AlignRight,
                    indent=9,
                )
            )
        if m.order >= model.current_month:
            self.header.setChecked(True)

        for t in m.trans_links:
            self.trans = QWidget()
            trans_layout = QHBoxLayout(self.trans)
            trans_layout.addWidget(QLabel(f"{t.name}:"))
            trans_layout.addWidget(
                QLabel(f"\t€{t.q / 100}"), alignment=Qt.AlignmentFlag.AlignRight
            )
            content_layout.addWidget(self.trans)
        self.footer = QWidget()
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.addWidget(QLabel())
        footer_layout.addWidget(
            QLabel(
                f"=================\n€{m.get_total() / 100}",
                alignment=Qt.AlignmentFlag.AlignRight,
            )
        )
        content_layout.addWidget(self.footer)
        layout.addWidget(self.content)

        self.header.clicked.connect(self.on_toggled)

    def on_toggled(self, expanded: bool):
        self.content.setVisible(expanded)


# class Palette(QPalette):
#     def __init__(self):
#         super().__init__()
#         self.setColor(QPalette.ColorRole.Base, QColor("#5fab70"))
#         self.setColor(QPalette.ColorRole.Text, QColor("#053c5e"))
