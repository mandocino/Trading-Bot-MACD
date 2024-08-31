class CompletedTrades:
    def __init__(self, lengthOfTime, bookCost, profit, roi):
        self.lengthOfTime = lengthOfTime
        self.bookCost = bookCost
        self.profits = profit
        self.roi = roi

    def get_profits(self):
        return self.profits
    
    def get_bookCost(self):
        return self.bookCost
    
    def get_lengthOfTime(self):
        return self.lengthOfTime
    
    def set_balance(self, balance):
        self.balance = balance

    def has_trade(self, trade_id):
        return trade_id in self.trades

    def get_trade(self, trade_id):
        if self.has_trade(trade_id):
            return self.trades[trade_id]
        else:
            return None

    def set_trade(self, trade_id, trade):
        self.trades[trade_id] = trade

    def toString(self):
        years = self.lengthOfTime.days // 365
        months = (self.lengthOfTime.days % 365) // 30
        days = self.lengthOfTime.days % 30
        #print(f"Profit: ${self.profits:,.2f} from ${self.bookCost:,.2f} the length of the trade was: {years} years, {months} months, {days} days. The roi was: {self.roi:.2f}%.")
