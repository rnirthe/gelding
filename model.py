import uuid


class Model:
    def __init__(self, db):
        # self.months, self.ties, self.transactions, self.misc = db.load()
        # using test data for now:
        self.months = [
            Month(self.gen_uid(), 1, "June"),
            Month(self.gen_uid(), 2, "July"),
            Month(self.gen_uid(), 3, "August"),
            Month(self.gen_uid(), 4, "September"),
            Month(self.gen_uid(), 5, "October"),
            Month(self.gen_uid(), 6, "November"),
        ]
        self.transactions = [
            Trans(self.gen_uid(), "Freddy D", 500_00),
            Trans(self.gen_uid(), "Pizza", 10_00),
            Trans(self.gen_uid(), "Webflyx", 5_00),
        ]

        self.ties = [
            Tie(self.months[2], self.transactions[0]),
            Tie(self.months[2], self.transactions[1]),
            Tie(self.months[2], self.transactions[2]),
            Tie(self.months[3], self.transactions[2]),
            Tie(self.months[4], self.transactions[2]),
            Tie(self.months[5], self.transactions[2]),
            Tie(self.months[2], self.transactions[1]),
        ]
        self.misc = {
            "current_month": 3,
            "current_balance": 839_426_712,
        }

    def gen_uid(self):
        return uuid.uuid1().hex


class Month:
    def __init__(self, id, order, name):
        self.id = id
        self.order = order
        self.name = name

    def add_trans(self, trans):
        if not self.trans:
            self.trans = trans
        else:
            self.trans.append(trans)


class Tie:
    def __init__(self, month, trans):
        self.month = month
        self.trans = trans


class Trans:
    def __init__(self, id, name, q):
        self.id = id
        self.name = name
        self.q = q
