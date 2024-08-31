from Stock import Stock
from Transaction import Transaction
from CompletedTrades import CompletedTrades
import pandas as pd

class Account:
    def __init__(self):
        self.stocks = {}
        self.completedTrades = []
        self.balance = 0
    
    def get_balance(self):
        return self.balance
    
    def set_balance(self, balance):
        self.balance = balance

    def buy_stock(self, stock_symbol, quantity, price, date):
        if stock_symbol in self.stocks:
            if (self.stocks[stock_symbol].get_quantity() == 0):
                self.stocks[stock_symbol].dateBought = date
            currentValue = self.stocks[stock_symbol].get_quantity() * self.stocks[stock_symbol].get_avg_price()
            newBuyTotal = quantity * price
            newTotalValue =currentValue + newBuyTotal
            newTotalShares = self.stocks[stock_symbol].get_quantity() + quantity
            newAveragePrice = newTotalValue / newTotalShares
            self.stocks[stock_symbol].add_quantity(quantity)
            self.stocks[stock_symbol].set_avg_price(newAveragePrice)
            self.stocks[stock_symbol].transactions.append(Transaction(date, "buy", quantity, price))
            newBookCost = self.stocks[stock_symbol].get_quantity() * self.stocks[stock_symbol].get_avg_price()
            #print(f"{date} Bought {quantity:.2f} more shares for {price:,.2f} each, totaling ${newBuyTotal:,.2f}. The investment book cost is now worth ${newBookCost:,.2f} with a quantity of: {self.stocks[stock_symbol].get_quantity()}. Avg Share Price: ${self.stocks[stock_symbol].get_avg_price():,.2f}. PnL: ${(price-self.stocks[stock_symbol].get_avg_price())*self.stocks[stock_symbol].get_quantity():,.2f}")

        else:
            new_stock = Stock(stock_symbol, price, quantity, date)
            new_stock.transactions.append(Transaction(date, "buy", quantity, price))
            self.stocks[stock_symbol] = new_stock
            self.stocks[stock_symbol].set_avg_price(price)
            self.stocks[stock_symbol].set_quantity(quantity)
            newBookCost = self.stocks[stock_symbol].get_quantity() * self.stocks[stock_symbol].get_avg_price()
            #print(f"Started a LONG position on: {date}. Bought {quantity:.2f} shares for ${price:,.2f} each, totaling ${price * quantity:,.2f}. The investment book cost is now worth ${newBookCost:,.2f} with a quantity of: {self.stocks[stock_symbol].get_quantity()}. Avg Share Price: ${self.stocks[stock_symbol].get_avg_price():,.2f}")

    def cover_short(self, stock_symbol, quantity, price, date):
        absQty = abs(quantity)
        profit = ((price - self.stocks[stock_symbol].get_avg_price()) * quantity)
        bookCost = self.stocks[stock_symbol].get_avg_price() * quantity
        self.stocks[stock_symbol].set_quantity(0)
        self.stocks[stock_symbol].set_avg_price(0)
        self.stocks[stock_symbol].transactions.append(Transaction(date, "cover", quantity, price))
        newBookCost = self.stocks[stock_symbol].get_quantity() * self.stocks[stock_symbol].get_avg_price()
        #print(f"{date}: COVERED {absQty:.2f} shares for ${price:,.2f} each, totaling ${absQty * price:,.2f}. The investment book cost is now worth ${newBookCost:,.2f} with a quantity of: {self.stocks[stock_symbol].get_quantity()}. Avg Share Price: ${self.stocks[stock_symbol].get_avg_price():,.2f}")
        date_bought_str = self.stocks[stock_symbol].get_dateBought()  # Replace with your actual method
        date_bought = pd.to_datetime(date_bought_str)
        date_obj = pd.to_datetime(date)
        time_difference = date_obj - date_bought

        years = time_difference.days // 365
        months = (time_difference.days % 365) // 30  # Approximate calculation
        days = time_difference.days % 30  # Approximate calculation
        #print(f"The profit made was: ${profit:.2f} and the length of the trade was: {years} years, {months} months, {days} days")
        return CompletedTrades(time_difference, bookCost, profit, None)
        #roi = (profit/total_cost)*100
        #years_decimal = self.timedelta_to_years(time_difference)
        #apy = (roi/years_decimal)
        #print("The %ROI was: " + str(roi) + ". Apy: " + str(apy))
        #print(str(price - self.stocks[stock_symbol].get_avg_price() * quantity))
    def sell_stock(self, stock_symbol, quantity, price, date):
        profit = ((price - self.stocks[stock_symbol].get_avg_price()) * quantity)
        bookCost = self.stocks[stock_symbol].get_avg_price() * quantity
        self.stocks[stock_symbol].set_quantity(0)
        self.stocks[stock_symbol].set_avg_price(0)
        self.stocks[stock_symbol].transactions.append(Transaction(date, "sell", quantity, price))
        newBookCost = self.stocks[stock_symbol].get_quantity() * self.stocks[stock_symbol].get_avg_price()
        #print(f"{date}: SOLD {quantity:.2f} shares for {price:,.2f} each, totaling {quantity * price:,.2f}. The investment book cost is now worth {newBookCost:,.2f} with a quantity of: {self.stocks[stock_symbol].get_quantity()}. Avg Share Price: {self.stocks[stock_symbol].get_avg_price():,.2f}")
        date_bought_str = self.stocks[stock_symbol].get_dateBought()  # Replace with your actual method
        date_bought = pd.to_datetime(date_bought_str)
        date_obj = pd.to_datetime(date)
        time_difference = date_obj - date_bought

        years = time_difference.days // 365
        months = (time_difference.days % 365) // 30  # Approximate calculation
        days = time_difference.days % 30  # Approximate calculation
        #print(f"The profit made was: ${profit:,.2f} and the length of the trade was: {years} years, {months} months, {days} days")
        return CompletedTrades(time_difference, bookCost, profit, None)
        #roi = (profit/total_cost)*100
        #years_decimal = self.timedelta_to_years(time_difference)
        #apy = (roi/years_decimal)
        #print("The %ROI was: " + str(roi) + ". Apy: " + str(apy))
        #print(str(price - self.stocks[stock_symbol].get_avg_price() * quantity))

    def sell_stock_short(self, stock_symbol, quantity, price, date):
        if stock_symbol in self.stocks:
            if (self.stocks[stock_symbol].get_quantity() == 0):
                self.stocks[stock_symbol].dateBought = date
            currentValue = self.stocks[stock_symbol].get_quantity() * self.stocks[stock_symbol].get_avg_price()
            newBuyTotal = quantity * price
            newTotalValue = abs(currentValue) + newBuyTotal
            newTotalShares = abs(self.stocks[stock_symbol].get_quantity()) + quantity
            newAveragePrice = newTotalValue / newTotalShares
            self.stocks[stock_symbol].add_quantity(-quantity)
            self.stocks[stock_symbol].set_avg_price(newAveragePrice)
            self.stocks[stock_symbol].transactions.append(Transaction(date, "short", quantity, price))
            newBookCost = self.stocks[stock_symbol].get_quantity() * self.stocks[stock_symbol].get_avg_price()
            #print(f"{date} Shorted {quantity:.2f} more shares for {price:.2f} each, totaling ${newBuyTotal:,.2f}. The investment book cost is now worth ${newBookCost:,.2f} with a quantity of: {self.stocks[stock_symbol].get_quantity()}. Avg Share Price: ${self.stocks[stock_symbol].get_avg_price():,.2f}. PnL: ${(self.stocks[stock_symbol].get_avg_price()-price)*-self.stocks[stock_symbol].get_quantity():,.2f}")
        else:
            new_stock = Stock(stock_symbol, price, quantity, date)
            new_stock.transactions.append(Transaction(date, "short", quantity, price))
            self.stocks[stock_symbol] = new_stock
            self.stocks[stock_symbol].set_quantity(-quantity)
            self.stocks[stock_symbol].set_avg_price(price)
            newBookCost = self.stocks[stock_symbol].get_quantity() * self.stocks[stock_symbol].get_avg_price()
            #print(f"Started a SHORT position on: {date}. Shorted {quantity:.2f} shares for ${price:,.2f} each, totaling ${price * quantity:,.2f}. The investment book cost is now worth ${newBookCost:,.2f} with a quantity of: {self.stocks[stock_symbol].get_quantity()}. Avg Share Price: ${self.stocks[stock_symbol].get_avg_price():,.2f}")


    def get_completedTrades(self):
        return self.completedTrades
    