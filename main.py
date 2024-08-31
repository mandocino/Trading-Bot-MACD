from Account import Account
from CompletedTrades import CompletedTrades
import time
import pandas as pd
import pandas_ta as ta
from datetime import timedelta
import math
import requests
from datetime import datetime

@staticmethod
def timedelta_to_years(timedelta):
    days_in_year = 365.25

    total_days = timedelta.days
    total_seconds = timedelta.seconds + timedelta.microseconds / 1e6
    total_years = total_days / days_in_year + \
        total_seconds / (days_in_year * 24 * 60 * 60)
    return total_years

def calculate_percentage(part, whole):
    try:
        percentage = ((float(part) - float(whole)) / float(whole)) * 100
        return percentage
    except ZeroDivisionError:
        return "Cannot divide by zero."

def constant_Share_Purchase(symbol, date, day, perc, data_daily, data_macd, stop):

    df_daily = pd.DataFrame(data_daily['Time Series (Daily)']).T
    df_macd = pd.DataFrame(data_macd['Technical Analysis: MACD']).T

    df_daily.index = pd.to_datetime(df_daily.index)
    df_macd.index = pd.to_datetime(df_macd.index)

    df_merged = pd.merge(df_daily, df_macd, left_index=True, right_index=True, how='outer')

    pdDate = pd.to_datetime(date)
    df_merged.reset_index(inplace=True)
    df_merged = df_merged[df_merged['index'] >= pdDate]
    #pd.set_option('display.max_rows', None)
    #pd.set_option('display.max_columns', None)
    #pd.set_option('display.width', None)
    #print(df_merged)
    df_merged.columns = ['index', 'open', 'high', 'low', 'close', 'volume', 'MACD', 'MACD_Signal', 'MACD_Hist']
    lastUpConvergence = None
    lastDownConvergence = None
    last_five_values = []
    global previousState
    previousState = None
    global firstValueBuy
    global lastValueBuy
    global firstDateBuy
    global lastDateBuy
    earlyAction = False
    firstValueBuy = df_merged['close'].iloc[0]
    firstDateBuy = df_merged['index'].iloc[0]
    lastDateBuy = df_merged['index'].iloc[-1]
    lastValueBuy = df_merged['close'].iloc[-1]
    prices = []

    for index, row in df_merged.iterrows():
        if (len(account.stocks) != 0):
            if (account.stocks[symbol].get_quantity() > 0):
                prices.append(float(row['close']))
                high_price = max(prices)
                trailing_stop_loss = high_price * float(1 - float(stop) / 100)
                if (float(row['close']) <= trailing_stop_loss):
                    earlyAction = True
                    account.set_balance(account.stocks[symbol].get_quantity() * float(row['close']))
                    trade = account.sell_stock(symbol, account.stocks[symbol].get_quantity(), float(row['close']), row['index'])
                    roi = (trade.profits / abs(trade.bookCost)) * 100
                    completedTrade = CompletedTrades(trade.lengthOfTime, trade.bookCost, trade.profits, roi)
                    account.completedTrades.append(completedTrade)
                    account.stocks.pop(symbol)
                    prices = []
            elif (account.stocks[symbol].get_quantity() < 0):
                prices.append(float(row['close']))
                low_price = max(prices)
                trailing_stop_loss = low_price * float(1 - float(stop) / 100)
                if (float(row['close']) >= trailing_stop_loss):
                    earlyAction = True
                    account.set_balance(abs(account.stocks[symbol].get_quantity() * (account.stocks[symbol].get_avg_price()-(float(row['close'])-account.stocks[symbol].get_avg_price()))))
                    trade = account.cover_short(symbol, account.stocks[symbol].get_quantity(), float(row['close']), row['index'])
                    roi = (trade.profits / abs(trade.bookCost)) * 100
                    completedTrade = CompletedTrades(trade.lengthOfTime, trade.bookCost, trade.profits, roi)
                    account.completedTrades.append(completedTrade)
                    account.stocks.pop(symbol)
                    prices = []
        if (not math.isnan(float(row['MACD_Hist'])) and not math.isnan(float(row['close']))):
            if (len(last_five_values) >= day):
                smoothMacdPc = calculate_percentage(float(row['MACD']), last_five_values[0][1])
                diff = float(row['MACD']) - last_five_values[day-1][1]
                if (diff < 0): #can change around the % value as a threshold #and abs(smoothMacdPc)
                    downward_convergence = True
                    upward_convergence = False
                else:
                    downward_convergence = False
                    upward_convergence = True

                if (( upward_convergence!=lastUpConvergence) and ( downward_convergence != lastDownConvergence)):
                    if (downward_convergence and abs(smoothMacdPc) >  perc ):
                        df_merged.at[index, 'convergence'] = 'Downward'
                        previousState = "Downward"
                        if ((symbol in account.stocks)):
                            if (account.stocks[symbol].get_quantity() > 0):
                                account.set_balance(account.stocks[symbol].get_quantity() * float(row['close']))
                                trade = account.sell_stock(symbol, account.stocks[symbol].get_quantity(), float(row['close']), row['index'])
                                roi = (trade.profits / abs(trade.bookCost)) * 100
                                completedTrade = CompletedTrades(trade.lengthOfTime, trade.bookCost, trade.profits, roi)
                                account.completedTrades.append(completedTrade)
                                account.stocks.pop(symbol)
                                account.sell_stock_short(
                                symbol, float(account.get_balance())/float(row['close']), float(row['close']), row['index'])
                                account.set_balance(0)
                            else:
                                account.sell_stock_short(
                                symbol, float(account.get_balance())/float(row['close']), float(row['close']), row['index'])  
                                account.set_balance(0)
                        else:
                            account.sell_stock_short(
                            symbol, float(account.get_balance())/float(row['close']), float(row['close']), row['index']) 
                            account.set_balance(0)           

                    elif (upward_convergence and abs(smoothMacdPc) >  perc ):    
                        df_merged.at[index, 'convergence'] = 'Upward'
                        previousState = "Upward"   
                        date = pd.to_datetime(index)
                        if ((symbol in account.stocks)):    
                            if (account.stocks[symbol].get_quantity()<0):
                                account.set_balance(abs(account.stocks[symbol].get_quantity() * (account.stocks[symbol].get_avg_price()-(float(row['close'])-account.stocks[symbol].get_avg_price()))))
                                trade = account.cover_short(symbol, account.stocks[symbol].get_quantity(), float(row['close']), row['index'])
                                roi = (trade.profits / abs(trade.bookCost)) * 100
                                completedTrade = CompletedTrades(trade.lengthOfTime, trade.bookCost, trade.profits, roi)
                                account.completedTrades.append(completedTrade)
                                account.stocks.pop(symbol)
                                account.buy_stock(symbol, float(account.get_balance())/float(row['close']), float(row['close']), row['index'])
                                account.set_balance(0)
                            else:
                                account.buy_stock(symbol, float(account.get_balance())/float(row['close']), float(row['close']), row['index'])
                                account.set_balance(0)
                        else:
                            account.buy_stock(symbol, float(account.get_balance())/float(row['close']), float(row['close']), row['index'])     
                            account.set_balance(0)    
                else:
                    df_merged.at[index, 'convergence']  = previousState
                lastUpConvergence = upward_convergence
                lastDownConvergence = downward_convergence
            last_five_values.append([float(row['MACD_Hist']), float(row['MACD']), float(row['close'])])
            if len(last_five_values) > day:
                    last_five_values.pop(0)
        else:
            df_merged.at[index, 'convergence'] = 'NaN Case'

    sumOfProfit = 0
    tradesCount = 0
    time_difference = timedelta()

    for items in account.completedTrades:
        items.toString()
        sumOfProfit += items.get_profits()
        timeDiff = items.get_lengthOfTime()
        time_difference += timeDiff
        tradesCount += 1
                
    startingTotalCapitalRequired = float(50000)
    years = time_difference.days // 365
    months = (time_difference.days % 365) // 30
    days = time_difference.days % 30
    totalRoi = (sumOfProfit/startingTotalCapitalRequired) * 100
    years_decimal = timedelta_to_years(time_difference)
    totalAPY = (totalRoi/years_decimal)
    if (years_decimal != 0):
        totalAPY = (totalRoi/years_decimal)
    print(f"The sum of profits was ${sumOfProfit:,.2f} from ${abs(startingTotalCapitalRequired):,.2f} giving an ROI of {totalRoi:.2f}%, for an APY of {totalAPY:.2f}% The length of time was {years} years, {months} months, {days} days for a total of {tradesCount} trades.")
    message = f"APY of {totalAPY:.2f}% The length of time was {years} years, {months} months, {days} days for a total of {tradesCount} trades.\n"
    current_datetime = datetime.now()
    baseline_time_difference = timedelta()
    baseline_time_difference = current_datetime - pdDate
    years_decimal = timedelta_to_years(baseline_time_difference)
    baselineTotalAPY = (totalRoi/years_decimal)
    if (years_decimal != 0):
        baselineTotalAPY = (totalRoi/years_decimal)
    message += f"Baseline APY of {baselineTotalAPY:.2f}% for {years_decimal:.2f} years\n"
    return message
account = Account()
firstValueBuy = 0
firstDateBuy = None
lastValueBuy = 0 
lastDateBuy = None
percentList = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14',
                '15','16','17','18','19','20','21','22','23','24','25','26','27','28']
daysList = ['5', '4' , '3']
dateList = ['2010-01-01',
            '2014-01-01',
            '2015-01-01',
            '2016-01-01',
            '2017-01-01',
            '2018-01-01',
            '2019-01-01',
            '2020-01-01',
            '2021-01-01',
            '2022-01-01',
            '2023-01-01',
            ]

stopPercentage = ['.2',
                '.5',
                '1',
                '1.5',
                '2',
                '2.5',
                '3',
                '3.5',
                '4',
                '4.5',
                '5',
                '5.5',
                '6',
                '6.5',
                '7',
                '7.5',
                '8',
            ]

symbol = 'SPY'
outputFile = ""
fileContent = ""
done = False

def main():
    try:
        global done
        start_time = time.time()
        start_time_ms = int(start_time * 1000)
        while (not done):
                global symbol
                global fileContent
                url_daily = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey=ZSUIV2I66JUFYTKP'
                response_daily = requests.get(url_daily)
                data_daily = response_daily.json()

                url_macd = f'https://www.alphavantage.co/query?function=MACD&symbol={symbol}&interval=daily&series_type=open&apikey=ZSUIV2I66JUFYTKP'
                response_macd = requests.get(url_macd)
                data_macd = response_macd.json()

                for date in dateList:
                    outputFile = "output"+symbol+"_"+str(date)+".txt"  
                    fileContent = ""        
                    with open(outputFile, 'w') as file:
                        file.write(f"Welcome to ALPHA MACD Backtest of {symbol} - {date}\n")
                    for day in daysList:
                        fileContent += day+"\n"
                        for perc in percentList:
                            fileContent += perc+"\n"
                            for stop in stopPercentage:
                                try:
                                    fileContent += stop+"\n"
                                    account.set_balance(50000)
                                    outputText = constant_Share_Purchase(symbol, date, int(day) , float(perc), data_daily, data_macd, stop)
                                    account.completedTrades.clear()
                                    account.stocks.clear()
                                    qtyBought = float(50000)/float(float(firstValueBuy))
                                    pnl = (float(lastValueBuy)-float(firstValueBuy))*(qtyBought)
                                    time_difference = timedelta()
                                    time_difference = lastDateBuy - firstDateBuy
                                    buyAndHoldRoi = (float(pnl) /  float(50000)) * 100
                                    years_decimal = timedelta_to_years(time_difference)
                                    totalAPY = 0
                                    if (years_decimal != 0):
                                        totalAPY = (buyAndHoldRoi/years_decimal)
                                    fileContent += outputText
                                    fileContent += f"Buy and Hold APY of {totalAPY:.2f}%. Buy Price:{firstValueBuy} Sell Price:{lastValueBuy}\n\n"
                                except Exception as e:
                                    fileContent += f"Error.\n"
                    with open(outputFile, 'a') as file:
                        file.write(fileContent)
                done = True
        current_time = time.time()
        current_time_seconds = int(current_time * 1000)
        timeDiff = current_time_seconds - start_time_ms
        timeDiffSec = float(timeDiff) / 1000
        with open(outputFile, 'a') as file:
            file.write("Execution Time: " + str(timeDiffSec) + " seconds")
    except Exception as e:
        print("Error." + e + "\n")
if __name__ == '__main__':
    main()
