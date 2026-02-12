from model import Trans


class ToolSet:
    def __init__(self, model):
        self.model = model

    def create_transaction(self, trans_name, q, month_name):
        month = self.model.get_month_from_name(month_name)
        id = self.model.gen_uid()
        trans = Trans(id, trans_name, q)
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

    def get_total_prev(self, month):
        prev = next(m for m in self.model.months if m.order == month.order - 1)
        return prev.get_total()

    def delete_transaction(self, trans_name):
        trans = self.model.get_transaction_from_name(trans_name)
        self.model.delete_transaction(trans)

    def exit(self, event):
        self.model.save_and_close(event)
