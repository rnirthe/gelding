from model import Trans


class ToolSet:
    def __init__(self, model):
        self.model = model

    def create_transaction(self, name, q, month_name):
        month = self.model.get_month_from_name(month_name)
        id = self.model.gen_uid()
        trans = Trans(id, name, q)
        self.model.transactions.append(trans)
        self.model.add_link_month_and_trans(month, trans)

    def change_balance(self, new_balance):
        self.model.current_balance = new_balance

    def get_current_balance(self):
        return self.model.current_balance

    def get_current_month(self):
        return self.model.current_month

    def get_all_months(self):
        return self.model.months

    def exit(self, event):
        self.model.save_and_close(event)
