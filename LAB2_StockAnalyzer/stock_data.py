import sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import csv
import time
from datetime import datetime
from utilities import clear_screen
from utilities import sortDailyData
from stock_class import Stock, DailyData


def create_database():
    stockDB = "stocks.db"
    conn = sqlite3.connect(stockDB)
    cur = conn.cursor()
    createStockTableCmd = """CREATE TABLE IF NOT EXISTS stocks (
                            symbol TEXT NOT NULL PRIMARY KEY,
                            name TEXT,
                            shares REAL
                        );"""
    createDailyDataTableCmd = """CREATE TABLE IF NOT EXISTS dailyData (
                                symbol TEXT NOT NULL,
                                date TEXT NOT NULL,
                                price REAL NOT NULL,
                                volume REAL NOT NULL,
                                PRIMARY KEY (symbol, date)
                        );"""   
    cur.execute(createStockTableCmd)
    cur.execute(createDailyDataTableCmd)


def save_stock_data(stock_list):
    stockDB = "stocks.db"
    conn = sqlite3.connect(stockDB)
    cur = conn.cursor()
    insertStockCmd = """INSERT INTO stocks
                            (symbol, name, shares)
                            VALUES
                            (?, ?, ?); """
    insertDailyDataCmd = """INSERT INTO dailyData
                                    (symbol, date, price, volume)
                                    VALUES
                                    (?, ?, ?, ?);"""
    for stock in stock_list:
        insertValues = (stock.symbol, stock.name, stock.shares)
        try:
            cur.execute(insertStockCmd, insertValues)
            cur.execute("COMMIT;")
        except:
            pass
        for daily_data in stock.DataList: 
            insertValues = (stock.symbol,daily_data.date.strftime("%m/%d/%y"),daily_data.close,daily_data.volume)
            try:
                cur.execute(insertDailyDataCmd, insertValues)
                cur.execute("COMMIT;")
            except:
                pass
    

def load_stock_data(stock_list):
    stock_list.clear()
    stockDB = "stocks.db"
    conn = sqlite3.connect(stockDB)
    stockCur = conn.cursor()
    stockSelectCmd = """SELECT symbol, name, shares
                    FROM stocks; """
    stockCur.execute(stockSelectCmd)
    stockRows = stockCur.fetchall()
    for row in stockRows:
        new_stock = Stock(row[0],row[1],row[2])
        dailyDataCur = conn.cursor()
        dailyDataCmd = """SELECT date, price, volume
                        FROM dailyData
                        WHERE symbol=?; """
        selectValue = (new_stock.symbol)
        dailyDataCur.execute(dailyDataCmd,(selectValue,))
        dailyDataRows = dailyDataCur.fetchall()
        for dailyRow in dailyDataRows:
            daily_data = DailyData(datetime.strptime(dailyRow[0],"%m/%d/%y"),float(dailyRow[1]),float(dailyRow[2]))
            new_stock.add_data(daily_data)
        stock_list.append(new_stock)
    sortDailyData(stock_list)

def retrieve_stock_web(dateStart,dateEnd,stock_list):
    dateFrom = str(int(time.mktime(time.strptime(dateStart,"%m/%d/%y"))))
    dateTo = str(int(time.mktime(time.strptime(dateEnd,"%m/%d/%y"))))
    recordCount = 0
    for stock in stock_list:
        stockSymbol = stock.symbol
        url = "https://finance.yahoo.com/quote/"+stockSymbol+"/history?period1="+dateFrom+"&period2="+dateTo+"&interval=1d&filter=history&frequency=1d"

        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches',['enable-logging'])
        options.add_experimental_option("prefs",{'profile.managed_default_content_settings.javascript': 2})
        try:
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(60)
            driver.get(url)
        except:
            raise RuntimeWarning("Chrome Driver Not Found")

        soup = BeautifulSoup(driver.page_source,"html.parser")
        row = soup.find('table',class_="W(100%) M(0)")
        dataRows = soup.find_all('tr')
        for row in dataRows:
            td = row.find_all('td')
            rowList = [i.text for i in td]
            columnCount = len(rowList)
            if columnCount == 7:
                daily_data = DailyData(datetime.strptime(rowList[0],"%b %d, %Y"),float(rowList[5].replace(',','')),float(rowList[6].replace(',','')))
                stock.add_data(daily_data)
                recordCount += 1
    return recordCount

def import_stock_web_csv(stock_list, symbol, filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Error: CSV file is not found: {filename}")

    target_val = next((st for st in stock_list if st.symbol == symbol), None)
    if not target_val:
        raise ValueError(f"Symbol '{symbol}' not found in the stock_list")

    imported_val = 0
    with open(filename, newline='', encoding='utf-8') as stockdata:
        datareader = csv.reader(stockdata, delimiter=',')
        header = next(datareader, None)
        for row in datareader:
            if not row or 7 > len(row):
                continue
            try:
                dat = datetime.strptime(row[0].strip(), "%Y-%m-%d")
                close_val = float(row[4])
                vol_val = row[6].strip()
                volume_val = int(float(vol_val)) if vol_val != "" else 0
                daily_data_value = DailyData(dat, close_val, volume_val)
                target_val.add_data(daily_data_value)
                imported_val = imported_val + 1
            except Exception:
                continue
    return imported_val

def main():
    clear_screen()
    print("This module will handle data storage and retrieval.")

if __name__ == "__main__":

    main()