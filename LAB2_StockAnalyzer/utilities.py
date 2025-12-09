import matplotlib.pyplot as plt

from os import system, name
from datetime import datetime as _dt


def clear_screen():
    if name == "nt": 
        _ = system('cls')
    else: 
        _ = system('clear')


def sortStocks(stock_list):

    pass



def sortDailyData(stock_list):
    pass


def display_stock_chart(stock_or_list, symbol=None):

    stock_val = None

    if hasattr(stock_or_list, "symbol") and hasattr(stock_or_list, "DataList"):
        stock_val = stock_or_list
    else:
        if not symbol:
            raise ValueError("Please provide a Stock object or stock_list with symbol")
        for sto in stock_or_list:
            if symbol == sto.symbol:
                stock_val = sto
                break
        if not stock_val:
            raise ValueError(f"Symbol '{symbol}' is not found in the provided stock list")

    if not getattr(stock_val, "DataList", None):
        print(f"No available daily data to chart for {stock_val.symbol}.")
        return

    def date_helper(date_val):
        if hasattr(date_val, "strftime"):
            return date_val
        
        for fmt in ("%m/%d/%y", "%Y-%m-%d", "%b %d, %Y"):
            try:
                return _dt.strptime(str(date_val), fmt)
            except Exception:
                pass

        try:
            return _dt.fromtimestamp(float(date_val))
        except Exception:
            raise ValueError(f"Unrecognized date format: {date_val}")

    data_sorted_vals = sorted(stock_val.DataList, key=lambda d: date_helper(d.date))

    dates = []
    closes = []
    for d in data_sorted_vals:
        dates.append(date_helper(d.date))
    
    for d in data_sorted_vals:
        closes.append(float(d.close))

    plt.figure(figsize=(10, 5))
    plt.plot(dates, closes, marker="o", linestyle="-", color="#1f77b4")
    plt.title(f"{stock_val.symbol} Closing Prices")

    plt.xlabel("Date")
    plt.ylabel("Close Price (USD)")

    plt.grid(alpha=0.4)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()
