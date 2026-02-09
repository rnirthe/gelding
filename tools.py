class ToolSet:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def exit(self, event):
        self.db.save(self.model)
        self.db.close()
        event.accept()
