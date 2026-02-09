import sqlite3
from model import Model, Month, Tie, Trans


class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect("gelding.db")
        self.cur = self.conn.cursor()

    def load(self):
        months = self.__get_months()
        ties = self.__get_ties()
        transactions = self.__get_transactions()
        misc = self.__get_misc()
        return months, ties, transactions, misc

    def save(self, model):
        self.__upd_months(model.months)
        self.__upd_ties(model.ties)
        self.__upd_transactions(model.transactions)
        self.__upd_misc(model.misc)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def __upd_months(self, months):
        pass

    def __upd_ties(self, ties):
        pass

    def __upd_transactions(self, transactions):
        pass

    def __upd_misc(self, misc):
        pass

    def __get_ties(self):
        pass

    def __get_months(self):
        pass

    def __get_transactions(self):
        pass

    def __get_misc(self):
        pass
