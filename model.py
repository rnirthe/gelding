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
        month.trans_links = [t for t in month.trans_links if not t.id == trans.id]
        trans.month_links = [m for m in trans.month_links if not m.id == month.id]

    def get_month_from_name(self, name):
        for month in self.months:
            if month.name == name:
                return month

    def get_transaction_from_name(self, name):
        for trans in self.transactions:
            if trans.name == name:
                return trans

    def get_month_from_id(self, id):
        for month in self.months:
            if month.id == id:
                return month

    def get_transaction_from_id(self, id):
        for trans in self.transactions:
            if trans.id == id:
                return trans

    def delete_transaction(self, trans):
        self.transactions.remove(trans)
        if not hasattr(self, "del_trans_ids"):
            self.del_trans_ids = []
        for month in self.months:
            self.rem_link_month_and_trans(month, trans)
        self.del_trans_ids.append(trans.id)

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

    def get_balance(self):
        if self.order == self.model.current_month:
            return self.model.current_balance
        if self.order > 1:
            return self.get_prev_month().get_total()
        return 0

    def get_total(self):
        total = self.get_balance()
        for t in self.trans_links:
            total += t.q
        return total

    def get_prev_month(self):
        for month in self.model.months:
            if month.order == self.order - 1:
                return month
        return self


class Trans:
    def __init__(self, id, name, q):
        self.id = id
        self.name = name
        self.q = q
        self.month_links = set()
