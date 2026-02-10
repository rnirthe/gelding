from model import Trans


class ToolSet:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def create_transaction(self, name, q, month_name, main_window=None):
        month = self.model.get_month_from_name(month_name)
        id = self.model.gen_uid()
        trans = Trans(id, name, q)
        self.model.transactions.append(trans)
        self.model.add_link_month_and_trans(month, trans)
        if main_window:
            main_window.set_mainArea()

    def exit(self, event):
        self.db.save(self.model)
        self.db.close()
        event.accept()
