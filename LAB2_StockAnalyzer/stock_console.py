import csv
from datetime import datetime
from stock_class import Stock, DailyData
from utilities import clear_screen, display_stock_chart
from os import path
import stock_data

def main_menu(stock_list):
    option_val = ""
    while option_val != "0":
        clear_screen()
        print("Stock Analyzer ---")
        print("1 - Manage Stocks ----> (Add, Update, Delete, List)")
        print("2 - Insert Daily Stock Data ----> (Date, Price, Volume)")
        print("3 - Show Full Report")
        print("4 - Display Chart")
        print("5 - Manage Data (Save, Load, Retrieve)")
        print("0 - Exit Program")
        option_val = input("Enter Menu Option: ").strip()

        if option_val == "1": 
            manage_stocks(stock_list)
        elif option_val == "2":
            add_stock_data(stock_list)
        elif option_val == "3":
            display_report(stock_list)
        elif option_val == "4":
            display_chart(stock_list)
        elif option_val == "5":
            manage_data(stock_list)
        elif option_val == "0":
            clear_screen()
            print("Goodbye")
        else:
            print("*** Invalid Option ***")
            input("Press Enter...")


def manage_stocks(stock_list):
    option_val = ""
    while option_val != "0":
        clear_screen()
        print("Manage Stocks ---")
        print("1 - Add Stock")
        print("2 - Update Shares")
        print("3 - Delete Stock")
        print("4 - List Stocks")
        print("0 - Exit Manage Stocks")
        option_val = input("Enter Menu Option: ").strip()

        if option_val == "1":
            add_stock(stock_list)
        elif option_val == "2":
            update_shares(stock_list)
        elif option_val == "3":
            delete_stock(stock_list)
        elif option_val == "4":
            list_stocks(stock_list)
        elif option_val == "0":
            return
        else:
            print("*** Invalid Option ***")
            input("Press Enter...")


def add_stock_data(stock_list):
    clear_screen()
    print("Add Daily Stock Data ----")

    if 0 == len(stock_list):
        print("No stocks available.")
        input("Press Enter...")
        return

    print("Stock List: [", end="")
    for st in stock_list:
        print(f"{st.symbol}  ", end="")
    print("]")

    stock_symbol = input("Which stock do you want to use?: ").upper().strip()

    stock = next((st for st in stock_list if st.symbol == stock_symbol), None)
    if stock is None:
        print("Symbol not found.")
        input("Press Enter...")
        return

    print(f"Ready to add data for:   {stock_symbol}")

    print("Enter Data Separated by Commas – Do Not use Spaces")
    print("Enter a Blank Line to Quit")
    print("Enter Date,Price,Volume")
    print("Example: 8/28/20,47.85,10550")

    while True:
        line = input("Enter Date,Price,Volume: ").strip()

        if "" == line:
            break

        try:
            date_str, price_str, volume_str = line.split(",")

            price = float(price_str)
            volume = int(volume_str)

            stock.add_data(DailyData(date_str, price, volume))

        except:
            print("Invalid entry. Use format: 8/28/20,47.85,10550")

    print("Daily Data Entry Complete.")
    input("Press Enter to Continue ***")


def update_shares(stock_list):
    option_val = ""
    while option_val != "0":
        clear_screen()
        print("Update Shares ---")
        print("1 - Buy Shares")
        print("2 - Sell Shares")
        print("0 - Exit Update Shares")
        option_val = input("Enter Menu Option: ").strip()

        if "1" == option_val:
            buy_stock(stock_list)
        elif "2" == option_val:
            sell_stock(stock_list)
        elif "0" == option_val:
            return
        else:
            print("*** Invalid Option ***")
            input("Press Enter...")


def buy_stock(stock_list):
    clear_screen()
    print("Buy Shares ---")

    if 0 == len(stock_list):
        print("No stocks available.")
        input("Press Enter...")
        return

    print("Stock List: ", [st.symbol for st in stock_list])
    symbol = input("Enter Stock Symbol to Buy: ").upper().strip()

    stock = next((st for st in stock_list if st.symbol == symbol), None)
    if stock is None:
        print("Symbol not found.")
        input("Press Enter...")
        return

    shares_count = input("How many shares to BUY? ")
    try:
        shares_count = int(shares_count)
        if shares_count <= 0:
            raise ValueError
    except:
        print("Invalid number.")
        input("Press Enter...")
        return

    stock.buy(shares_count)
    print("Shares updated.")
    input("Press Enter...")


def sell_stock(stock_list):
    clear_screen()
    print("Sell Shares ---")

    if 0 == len(stock_list):
        print("No stocks available.")
        input("Press Enter...")
        return

    print("Stock List: ", [st.symbol for st in stock_list])
    symbol = input("Enter Stock Symbol to Sell: ").upper().strip()

    stock = next((st for st in stock_list if st.symbol == symbol), None)
    if stock is None:
        print("Symbol not found.")
        input("Press Enter...")
        return

    shares_count = input("How many shares to SELL? ")
    try:
        shares_count = int(shares_count)
        if shares_count <= 0:
            raise ValueError
    except:
        print("Invalid number.")
        input("Press Enter...")
        return

    if shares_count > stock.shares:
        print("Not enough shares to sell.")
        input("Press Enter...")
        return

    stock.sell(shares_count)
    print("Shares updated.")
    input("Press Enter...")


def delete_stock(stock_list):
    clear_screen()
    print("Delete Stock ---")

    if 0 == len(stock_list):
        print("No stocks to delete.")
        input("Press Enter...")
        return

    print("Stock List: ", [st.symbol for st in stock_list])
    symbol = input("Enter Stock Symbol to Delete: ").upper().strip()

    for st in stock_list:
        if st.symbol == symbol:
            stock_list.remove(st)
            print("Stock deleted.")
            input("Press Enter...")
            return

    print("Symbol not found.")
    input("Press Enter...")


def list_stocks(stock_list):
    clear_screen()
    print("Stock List ----")
    print(f"{'SYMBOL':<12}{'NAME':<20}{'SHARES':<10}")
    print("+" * 40)

    if 0 == len(stock_list):
        print("No stocks found.")
    else:
        for st in stock_list:
            print(f"{st.symbol:<12}{st.name:<20}{st.shares:<10}")
    input("\nPress Enter to Continue ***")


def add_stock(stock_list):
    option_value = ""

    while option_value != "0":
        clear_screen()
        print("Add Stock ----")

        symbol = input("Enter Ticker Symbol: ").upper().strip()
        if "" == symbol:
            print("Ticker Symbol cannot be blank.")
            input("Press Enter...")
            return

        for st in stock_list:
            if st.symbol == symbol:
                print("Stock already exists.")
                input("Press Enter...")
                break
        else:
            name = input("Enter Company Name: ").strip()
            shares = input("Enter Number of Shares: ").strip()

            try:
                shares = int(shares)
            except:
                print("Invalid number of shares.")
                input("Press Enter...")
                continue

            newstock = Stock(symbol, name, shares)
            stock_list.append(newstock)

        option_value = input("Stock Added – Enter to Add Another Stock or 0 to Stop: ").strip()

    return

      
def display_report(stock_list):
    clear_screen()
    print("Stock Report ---")

    if 0 == len(stock_list):
        print("No stocks found.")
        print("\n--- Report Complete ---")
        input("Press Enter to Continue")
        return

    for st in stock_list:
        print(f"Report for:   {st.symbol} {st.name}")
        print(f"Shares:   {float(st.shares)}")

        if 0 == len(st.DataList):
            print("*** No daily history.")
        else:
            print(f"Daily records: {len(st.DataList)}")

        print()

    print("--- Report Complete ---")
    input("Press Enter to Continue")


def display_chart(stock_list):
    clear_screen()

    print("Stock List: ", [st.symbol for st in stock_list])
    symbol = input("Enter Symbol to Chart: ").upper().strip()

    stock = next((st for st in stock_list if st.symbol == symbol), None)
    if not stock:
        print("Symbol not found.")
        input("Press Enter...")
        return

    display_stock_chart(stock)


def manage_data(stock_list):
    option_value = ""

    while option_value != "0":
        clear_screen()
        print("Manage Data ---")
        print("1 - Save the data to Sqlite database")
        print("2 - Load Data from the sqlite database")
        print("3 - Retrieve Data from the Web")
        print("4 - Import from CSV File")
        print("5 - Export to CSV File")
        print("0 - Exit Manage Data")
        option_value = input("Enter Menu Option: ").strip()

        if option_value == "1":
            stock_data.save_stock_data(stock_list)
            print("Data saved to database.")
            input("Press Enter...")

        elif option_value == "2":
            stock_data.load_stock_data(stock_list)
            print("Data loaded from database.")
            input("Press Enter...")

        elif option_value == "3":
            retrieve_from_web(stock_list)

        elif option_value == "4":
            import_csv(stock_list)

        elif option_value == "5":
            export_csv_helper(stock_list)

        elif option_value == "0":
            return

        else:
            print("*** Invalid Option ***")
            input("Press Enter...")


def retrieve_from_web(stock_list):
    print("Retrieving Stock Data from Yahoo! Finance ---")
    print("This will retrieve data from all stocks in your stock list.")

    dateFrom = input("Enter starting date (MM/DD/YY): ")
    dateTo = input("Enter ending date (MM/DD/YY): ")

    try:
        records = stock_data.retrieve_stock_web(dateFrom, dateTo, stock_list)
        print(f"Records Retrieved: {records}")
    except RuntimeWarning as e:
        print("Error:", e)
        input("Press Enter to continue...")
        return
    except Exception as e:
        print("An unexpected error occurred:", e)
        input("Press Enter to continue...")
        return

    input("Press Enter to continue...")


def import_csv(stock_list):
    clear_screen()
    print("Import CSV ---")

    print("Stock List: ", [st.symbol for st in stock_list])
    symbol = input("Enter Stock Symbol/Ticker: ").upper().strip()
    filename = input("Enter CSV Filename (full path): ").strip()

    if "" == filename:
        print("No file given.")
        input("Press Enter...")
        return

    if not path.exists(filename):
        print("File not found:", filename)
        input("Press Enter...")
        return

    target_val = next((st for st in stock_list if symbol == st.symbol), None)
    if not target_val:
        print("Symbol not found in current stock list we have:", symbol)
        print("Add the stock first [Manage Stocks -> Add Stock], then re run import CSV")
        input("Press Enter...")
        return

    try:
        rows_vals = stock_data.import_stock_web_csv(stock_list, symbol, filename)
        print(f"CSV Imported Successfully! All Rows are imported: {rows_vals}")
    except Exception as e:
        print("Error importing the CSV:", e)

    input("Press Enter...")

def export_csv_helper(stock_list):
    clear_screen()
    print("Export CSV ---")

    if not stock_list:
        print("There are no stocks available to export")
        input("Press Enter...")
        return

    print("Stock List: ", [sto.symbol for sto in stock_list])
    symbol_val = input("Please enter stock Symbol/Ticker to Export: ").upper().strip()

    stock_val = next((sto for sto in stock_list if symbol_val == sto.symbol), None)
    if not stock_val:
        print("Symbol has not been found")
        input("Press Enter...")
        return

    if not stock_val.DataList:
        print(f"No historical data is available for {symbol_val}.")
        input("Press Enter...")
        return

    filename_val = input("Enter CSV Filename to Save (full path): ").strip()

    if not filename_val:
        print("No filename provided.")
        input("Press Enter...")
        return

    try:
        with open(filename_val, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["date", "close", "volume"])
            
            for daily_data_val in stock_val.DataList:
                writer.writerow([
                    daily_data_val.date.strftime("%Y-%m-%d"),
                    daily_data_val.close,
                    daily_data_val.volume
                ])
        
        print(f"Successfully exported count {len(stock_val.DataList)} records to {filename_val}")
    
    except Exception as e:
        print(f"Got error while exporting to CSV file: {e}")

    input("Press Enter...")

def main():
    if path.exists("stocks.db") == False:
        stock_data.create_database()

    stock_list = []
    stock_data.load_stock_data(stock_list)

    main_menu(stock_list)


# Program Starts Here
if __name__ == "__main__":
    main()
