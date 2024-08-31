class Transaction:
    def __init__(self, date, transaction_type, quantity, price):
        self.date = date
        self.type = transaction_type
        self.quantity = quantity
        self.price = price

    def get_date(self):
        return self.date