from PySide6.QtWidgets import (
    QWidget,
    QStackedLayout,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
)
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtCore import Qt


class MainWindow(QWidget):
    def __init__(self, model, ts):
        self.ts = ts
        super().__init__()
        self.setWindowTitle("Gelding")
        palette = Palette()
        self.setPalette(palette)
        font = Font()
        self.mainArea = MonthsWidget(model, ts, palette, font)
        self.arena = ArenaLayout(ts, palette, font)
        self.toolView = ToolViewWidget(self.arena, palette, font)
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
    def __init__(self, arena, palette, font):
        self.arena = arena
        super().__init__()
        self.setPalette(palette)
        self.setFont(font)
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
    def __init__(self, ts, palette, font):
        self.ts = ts
        super().__init__()
        self.insertWidget(0, QWidget())
        self.insertWidget(1, UseMe(palette, font))
        self.tool_dict = {"UseMe": 1}

    def clear(self):
        self.setCurrentIndex(0)

    def show_tool(self, label):
        self.setCurrentIndex(self.tool_dict[label])


class UseMe(QListWidget):
    def __init__(self, palette, font):
        super().__init__()
        self.setPalette(palette)
        self.setFont(font)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.addItem("UseMe")


class MonthsWidget(QListWidget):
    def __init__(self, model, ts, palette, font):
        self.model = model
        self.ts = ts
        super().__init__()
        for m in model.months:
            self.addItem(MonthsItem(model, m))
        self.setPalette(palette)
        self.setFont(font)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class MonthsItem(QListWidgetItem):
    def __init__(self, model, m):
        super().__init__(m.name)
        if m.order < model.misc["current_month"]:
            self.setBackground(QColor("#aabd8c"))
            self.setForeground(QColor("#5fab70"))
            self.setFlags(Qt.ItemFlag.NoItemFlags)


class Font(QFont):
    def __init__(self):
        super().__init__()
        self.setFamily("Avantgarde")
        self.setPointSize(20)


class Palette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.ColorRole.Window, QColor("#f9b9b7"))
        self.setColor(QPalette.ColorRole.Base, QColor("#5fab70"))
        self.setColor(QPalette.ColorRole.Text, QColor("#053c5e"))
        self.setColor(QPalette.ColorRole.Highlight, QColor("#8d86c9"))
