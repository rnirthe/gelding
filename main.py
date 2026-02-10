import sys
from PySide6.QtWidgets import QApplication
from ui import MainWindow
from model import Model
from storage import DataBase
from tools import ToolSet

if __name__ == "__main__":
    app = QApplication()
    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
    app.setStyleSheet
    db = DataBase()
    model = Model(db)
    ts = ToolSet(db, model)
    main_w = MainWindow(model, ts)
    main_w.show()
    sys.exit(app.exec())
