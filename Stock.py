class Stock:
    def __init__(self, symbol, price, quantity, date):
        self.symbol = symbol
        self.avg_price = price
        self.quantity = quantity
        self.dateBought = date
        self.transactions = []

    def get_symbol (self):
        return self.symbol

    def get_quantity (self):
        return self.quantity

    def get_transactions(self):
        return self.transactions
    
    def get_avg_price (self):
        return self.avg_price
    
    def get_dateBought (self):
        return self.dateBought
    
    def add_quantity (self, quantity):
        self.quantity += quantity

    def set_quantity (self, quantity):
        self.quantity = quantity

    def set_avg_price (self, avg_price):
        self.avg_price = avg_price        

