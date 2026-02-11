import uuid


class Model:
    def __init__(self, db):
        self.db = db
        self.months = []
        self.transactions = []
        db.load(self)

    def gen_uid(self):
        return uuid.uuid1().hex

    def add_link_month_and_trans(self, month, trans):
        month.trans_links.add(trans)
        trans.month_links.add(month)

    def rem_link_month_and_trans(self, month, trans):
        month.trans_links.remove(trans)
        trans.month_links.remove(month)

    def get_month_from_name(self, name):
        for month in self.months:
            if month.name == name:
                return month

    def get_month_from_id(self, id):
        for month in self.months:
            if month.id == id:
                return month

    def get_trans_from_id(self, id):
        for trans in self.transactions:
            if trans.id == id:
                return trans

    def save_and_close(self, event):
        self.db.save(self)
        self.db.close()
        event.accept()


class Month:
    def __init__(self, model, id, name, order):
        self.model = model
        self.id = id
        self.name = name
        self.order = order
        self.trans_links = set()

    def set_balance(self, q):
        self.balance = q

    def get_balance(self):
        if hasattr(self, "balance"):
            return self.balance
        if self.order == self.model.current_month:
            return self.model.current_balance
        return 0

    def get_total(self):
        total = self.get_balance()
        for t in self.trans_links:
            total += t.q
        return total


class Trans:
    def __init__(self, id, name, q):
        self.id = id
        self.name = name
        self.q = q
        self.month_links = set()
