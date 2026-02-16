import uuid


class Model:
    def __init__(self, db):
        self.db = db
        self.months = []
        self.transactions = []
        self.current_balance = 0
        self.current_month = 0
        db.load(self)

    def set_current_balance(self, balance):
        self.current_balance = float(balance)
        print(self.current_balance)

    def gen_uid(self):
        return uuid.uuid1().hex

    def create_month(self, name, transactions=None):
        id = self.gen_uid()
        if self.months == []:
            order = 0
        else:
            order = self.get_last_order() + 1
        month = Month(self, id, name, order)
        self.months.append(month)
        if transactions:
            transactions = map(self.get_transaction_from_name, transactions)
            for transaction in transactions:
                self.add_link_month_and_trans(month, transaction)
        return month

    def create_transaction(self, name, q, month=None):
        existing = self.get_transaction_from_name(name)
        if not existing:
            id = self.gen_uid()
            transaction = Trans(id, name, q)
            self.transactions.append(transaction)
        else:
            transaction = existing
        if month:
            month = self.get_month_from_name(month)
            self.add_link_month_and_trans(month, transaction)
        return transaction

    def add_link_month_and_trans(self, month, trans):
        month.trans_links.add(trans)
        trans.month_links.add(month)

    def rem_link_month_and_trans(self, month, trans):
        month.trans_links = {t for t in month.trans_links if not t.id == trans.id}
        trans.month_links = {m for m in trans.month_links if not m.id == month.id}

    def get_month_from_name(self, name):
        for month in self.months:
            if month.name == name:
                return month
        return None

    def get_transaction_from_name(self, name):
        for trans in self.transactions:
            if trans.name == name:
                return trans
        return None

    def get_month_from_id(self, id):
        for month in self.months:
            if month.id == id:
                return month
        return None

    def get_transaction_from_id(self, id):
        for trans in self.transactions:
            if trans.id == id:
                return trans
        return None

    def get_last_order(self):
        last_order = 0
        for month in self.months:
            last_order = max(month.order, last_order)
        return last_order

    def delete_transaction(self, transaction):
        transaction = self.get_transaction_from_name(transaction)
        self.transactions.remove(transaction)
        if not hasattr(self, "del_transactions"):
            self.del_transactions = []
        for month in self.months:
            self.rem_link_month_and_trans(month, transaction)
        self.del_transactions.append(transaction)

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
        if self.order > 0:
            prev_month = self.get_prev_month()
            if self != prev_month:
                return prev_month.get_total()
        return 0

    def get_total(self):
        total = self.get_balance()
        for t in self.trans_links:
            total += t.q
        return round(total, 2)

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
