import sqlite3
from model import Month, Trans


class DataBase:
    def __init__(self):
        self.con = sqlite3.connect("gelding.db")
        self.cur = self.con.cursor()
        self.init_tables()

    def load(self, model):
        self.__load_months(model)
        self.__load_transactions(model)
        self.__load_ties(model)
        self.__load_misc(model)

    def save(self, model):
        self.__upd_months(model)
        self.__upd_transactions(model)
        self.__upd_ties(model)
        self.__upd_misc(model)
        self.con.commit()

    def close(self):
        self.con.close()

    def __upd_months(self, model):
        for month in model.months:
            self.cur.execute(
                "INSERT OR IGNORE INTO months (id, name, month_order) VALUES (?, ?, ?)",
                (month.id, month.name, month.order),
            )
        # remove removed months too
        # change changed months too

    def __upd_ties(self, model):
        for month in model.months:
            for trans in month.trans_links:
                self.cur.execute(
                    "INSERT OR IGNORE INTO ties (month_id, trans_id) VALUES (?, ?) ",
                    (month.id, trans.id),
                )
        # remove removed ties too

    def __upd_transactions(self, model):
        for trans in model.transactions:
            self.cur.execute(
                "INSERT OR IGNORE INTO transactions (id, name, q) VALUES (?, ?, ?)",
                (trans.id, trans.name, trans.q),
            )
        # remove removed transactinos too
        # change changed transactions too

    def __upd_misc(self, model):
        self.cur.execute(
            "INSERT OR IGNORE INTO misc (name, value) VALUES (?, ?)",
            ("current_balance", model.current_balance),
        )
        self.cur.execute(
            "INSERT OR IGNORE INTO misc (name, value) VALUES (?, ?)",
            ("current_month", model.current_month),
        )
        # remove removed misc too
        # change changed misc too

    def __load_ties(self, model):
        self.cur.execute("SELECT month_id, trans_id FROM ties")
        for month_id, trans_id in self.cur.fetchall():
            month = model.get_month_from_id(month_id)
            trans = model.get_trans_from_id(trans_id)
            model.add_link_month_and_trans(month, trans)

    def __load_months(self, model):
        self.cur.execute("SELECT id, name, month_order FROM months")
        for id, name, order in self.cur.fetchall():
            model.months.append(Month(model, id, name, int(order)))

    def __load_transactions(self, model):
        self.cur.execute("SELECT id, name, q FROM transactions")
        for id, name, q in self.cur.fetchall():
            model.transactions.append(Trans(id, name, q))

    def __load_misc(self, model):
        self.cur.execute("SELECT name, value FROM misc")
        for name, value in self.cur.fetchall():
            match name:
                case "current_balance":
                    model.current_balance = int(value)
                case "current_month":
                    model.current_month = int(value)

    def init_tables(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS months (
          id TEXT PRIMARY KEY NOT NULL,
          name TEXT NOT NULL UNIQUE,
          month_order INTEGER NOT NULL
        )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
          id TEXT PRIMARY KEY NOT NULL,
          name TEXT NOT NULL UNIQUE,
          q INTEGER
        )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS ties (
          month_id TEXT NOT NULL,
          trans_id TEXT NOT NULL,
          PRIMARY KEY (month_id, trans_id),
          FOREIGN KEY (month_id) REFERENCES months(id),
          FOREIGN KEY (trans_id) REFERENCES transactions(id)
        )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS misc (
          name TEXT PRIMARY KEY NOT NULL,
          value TEXT NOT NULL
        )
        """)
        self.con.commit()
