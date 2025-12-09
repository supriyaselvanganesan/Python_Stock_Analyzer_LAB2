from datetime import datetime
from os import path
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog, filedialog
import csv
import stock_data
from stock_class import Stock, DailyData
from utilities import clear_screen, display_stock_chart, sortStocks, sortDailyData
import setproctitle

class StockApp:
    def __init__(self):
        self.stock_list = []

        if path.exists("stocks.db") == False:
            stock_data.create_database()




        self.root = Tk()
        self.root.title("Supriya's Stock Manager")
        setproctitle.setproctitle("Supriya Stock Manager Application")


        self.gui_menubar = Menu(self.root)


        self.gui_filemenu_options = Menu(self.gui_menubar, tearoff=0)
        self.gui_filemenu_options.add_command(command=self.load, label="Load Data")
        self.gui_filemenu_options.add_command(command=self.save, label="Save Data")
        self.gui_filemenu_options.add_separator()
        self.gui_filemenu_options.add_command(command=self.root.quit, label="Exit")
        self.gui_menubar.add_cascade(menu=self.gui_filemenu_options, label="File")
        

        self.gui_webmenu = Menu(self.gui_menubar, tearoff=0)
        self.gui_webmenu.add_command(
            command=self.scrape_web_data,
            label="Retrieve Data from Web",
            )
        self.gui_webmenu.add_command(
            command=self.importCSV_web_data,
            label="Import from CSV File",
            )
        self.gui_menubar.add_cascade(menu=self.gui_webmenu, label="Web")


        self.gui_chartmenu = Menu(self.gui_menubar, tearoff=0)
        self.gui_chartmenu.add_command(
            label="Show Chart for Stock",
            command=self.display_chart
            )
        self.gui_menubar.add_cascade(label="Chart", menu=self.gui_chartmenu)
 


        self.root.config(menu=self.gui_menubar)
        self.gui_heading_label = Label(self.root, font=("Arial", 14), text="Stock Not Selected")
        self.gui_heading_label.pack(pady=5.5)

        content = Frame(self.root)
        content.pack(fill=BOTH, pady=5.5, padx=5.5, expand=True)

        gui_left_frame = Frame(content)
        gui_left_frame.pack(fill=Y, side=LEFT)

        self.gui_stock_list = Listbox(width=19, master=gui_left_frame)
        self.gui_stock_list.pack(fill=Y, padx=(0,3.5), side=LEFT)
        list_scroll = Scrollbar(command=self.gui_stock_list.yview, master=gui_left_frame)
        list_scroll.pack(fill=Y, side=RIGHT)
        self.gui_stock_list.config(yscrollcommand=list_scroll.set)
        self.gui_stock_list.bind('<<ListboxSelect>>', self.update_data)

        gui_right_frame = Frame(content)
        gui_right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        self.gui_tabs = ttk.Notebook(gui_right_frame)
        self.gui_tabs.pack(fill=BOTH, expand=True)

        gui_main_tab = Frame(self.gui_tabs)
        gui_history_tab = Frame(self.gui_tabs)
        gui_report_tab = Frame(self.gui_tabs)
        self.gui_tabs.add(gui_main_tab, text="Main")
        self.gui_tabs.add(gui_history_tab, text="History")
        self.gui_tabs.add(gui_report_tab, text="Report")

        Label(gui_main_tab, text="Symbol:").grid(row=0, column=0, sticky=W, padx=3.5, pady=2.5)
        self.gui_addSymbolEntry = Entry(gui_main_tab)
        self.gui_addSymbolEntry.grid(row=0, column=1, padx=3.5, pady=2.5)

        Label(gui_main_tab, text="Name:").grid(sticky=W, padx=3.5, row=1, column=0, pady=2.5)
        self.gui_addNameEntry = Entry(gui_main_tab)
        self.gui_addNameEntry.grid(padx=3.5, pady=2.5, row=1, column=1)

        Label(gui_main_tab, text="Shares:").grid(sticky=W, padx=3.5, pady=2.5, row=2, column=0)
        self.gui_addSharesEntry = Entry(gui_main_tab)
        self.gui_addSharesEntry.grid(padx=3.5, pady=2.5, row=2, column=1)

        Button(gui_main_tab, text="Add Stock", command=self.add_stock).grid(row=3, column=0, columnspan=2, pady=5.5)

        Label(gui_main_tab, text="Update Shares:").grid(row=4, column=0, sticky=W, padx=3.5, pady=2.5)
        self.gui_updateSharesEntry = Entry(gui_main_tab)
        self.gui_updateSharesEntry.grid(row=4, column=1, padx=3.5, pady=2.5)

        Button(gui_main_tab, text="Buy", command=self.buy_shares).grid(pady=3.5, padx=3.5, row=5, column=0)
        Button(gui_main_tab, text="Sell", command=self.sell_shares).grid(pady=3.5, padx=3.5, row=5, column=1)
        Button(gui_main_tab, text="Delete", command=self.delete_stock).grid(columnspan=2, row=6, column=0, pady=5.5)

        self.gui_dailyDataList = Text(gui_history_tab, wrap=NONE, height=19.5)
        self.gui_dailyDataList.pack(side=LEFT, fill=BOTH, expand=True)
        hist_scroll = Scrollbar(gui_history_tab, command=self.gui_dailyDataList.yview)
        hist_scroll.pack(fill=Y, side=RIGHT)
        self.gui_dailyDataList.config(yscrollcommand=hist_scroll.set)

        self.gui_stockReport = Text(height=20, master=gui_report_tab, wrap=WORD)
        self.gui_stockReport.pack(expand=True, fill=BOTH)



        summary_frame = Frame(self.root)
        summary_frame.pack(padx=5.5, pady=(0,6), fill=X)

        self.gui_totalStocksLabel = Label(summary_frame, anchor=W, text="Total Stocks: 0")
        self.gui_totalStocksLabel.pack(side=LEFT, padx=(0, 7.5))

        self.gui_totalValueLabel = Label(summary_frame, anchor=W, text="Total Value: $0.00")
        self.gui_totalValueLabel.pack(side=LEFT, padx=(0, 7.5))
        self.gui_lastUpdatedLabel = Label(summary_frame, anchor=E, text="Last Updated: N/A")
        self.gui_lastUpdatedLabel.pack(side=RIGHT)

        def update_heading_summary():
            total = len(self.stock_list)
            self.gui_totalStocksLabel.config(text=f"Total Stocks: {total}")
            total_value = 0.0
            for s in self.stock_list:
                try:
                    if s.DataList and hasattr(s, 'DataList'):
                        price = s.DataList[-1].close
                    else:
                        price = 0.0
                    total_value += getattr(s, 'shares', 0) * float(price)
                except Exception:
                    continue
            self.gui_totalValueLabel.config(text=f"Total Value: ${total_value:,.2f}")
            self.gui_lastUpdatedLabel.config(text="Last Updated: " + datetime.now().strftime("%m/%d/%y %H:%M"))

        self.update_heading_summary = update_heading_summary
        self.update_heading_summary()

        


        self.gui_stock_list_menu = Menu(self.root, tearoff=0)
        self.gui_stock_list_menu.add_command(command=self.display_chart, label="Show Chart")
        self.gui_stock_list_menu.add_command(command=self.importCSV_web_data, label="Import CSV...")
        self.gui_stock_list_menu.add_separator()
        self.gui_stock_list_menu.add_command(command=self.delete_stock, label="Delete Stock")

        def gui_populate_stock_list():
            self.gui_stock_list.delete(0, END)
            sortStocks(self.stock_list)
            for stock in self.stock_list:
                self.gui_stock_list.insert(END, stock.symbol)
            try:
                self.update_heading_summary()
            except Exception:
                pass

        self.gui_populate_stock_list = gui_populate_stock_list

        self.gui_stock_list.bind('<Double-1>', lambda e: self.display_chart())
        def gui_show_list_menu(event):
            try:
                self.gui_stock_list.selection_clear(0, END)
                index = self.gui_stock_list.nearest(event.y)
                if not index:
                    self.gui_stock_list.selection_set(index)
                self.gui_stock_list_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.gui_stock_list_menu.grab_release()
        self.gui_stock_list.bind('<Button-3>', gui_show_list_menu)
        self.gui_stock_list.bind('<Button-2>', gui_show_list_menu)

        self.gui_populate_stock_list()
        
        




        self.gui_add_symbol_var = StringVar()
        self.gui_add_name_var   = StringVar()
        self.gui_add_shares_var = StringVar()
        self.gui_update_shares_var = StringVar()

        self.gui_addSymbolEntry.config(textvariable=self.gui_add_symbol_var)
        self.gui_addNameEntry.config(textvariable=self.gui_add_name_var)
        self.gui_addSharesEntry.config(textvariable=self.gui_add_shares_var)
        self.gui_updateSharesEntry.config(textvariable=self.gui_update_shares_var)

        def gui_validate_numeric(p_val):
            if p_val == "-" or p_val == "." or p_val == "":
                return True
            try:
                float(p_val)
                return True
            except Exception:
                return False

        vcmd_val = self.root.register(gui_validate_numeric)
        self.gui_addSharesEntry.config(validate="key", validatecommand=(vcmd_val, "%P"))
        self.gui_updateSharesEntry.config(validate="key", validatecommand=(vcmd_val, "%P"))

        self.gui_addSharesEntry.bind("<Return>", lambda e: self.add_stock())
        self.gui_updateSharesEntry.bind("<Return>", lambda e: self.buy_shares())

        try:
            self.gui_addSymbolEntry.focus_set()
        except Exception:
            pass



        history_toolbar = Frame(gui_history_tab)
        history_toolbar.pack(fill=X, padx=3.5, pady=(4,0))
        Button(history_toolbar, text="Import CSV", command=self.importCSV_web_data).pack(padx=3.5, side=LEFT)
        Button(history_toolbar, text="Show Chart", command=self.display_chart).pack(padx=3.5, side=LEFT)
        Button(history_toolbar, text="Sort ↑", command=lambda: application_gui_sort_history(False)).pack(padx=3.5, side=LEFT)
        Button(history_toolbar, text="Sort ↓", command=lambda: application_gui_sort_history(True)).pack(padx=3.5, side=LEFT)
        Button(history_toolbar, text="Export CSV", command=lambda: application_gui_export_history()).pack(padx=3.5, side=LEFT)
        Button(history_toolbar, text="Clear", command=lambda: application_gui_clear_history()).pack(padx=3.5, side=LEFT)

        def application_gui_selected_stock():
            try:
                symbol = self.gui_stock_list.get(self.gui_stock_list.curselection())
            except Exception:
                return None
            for st in self.stock_list:
                if symbol == st.symbol:
                    return st
            return None

        def application_gui_sort_history(desc=False):
            st = application_gui_selected_stock()
            if not st or not getattr(st, "DataList", None): return
            st.DataList.sort(key=lambda d: getattr(d, "date", None), reverse=desc)
            self.display_stock_data()

        def application_gui_export_history():
            st = application_gui_selected_stock()
            if not st or not getattr(st, "DataList", None): return
            fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
            if not fn: return
            with open(fn, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["date","close","volume"])
                for d in st.DataList:
                    w.writerow([getattr(d,"date",""), getattr(d,"close",""), getattr(d,"volume","")])

        def application_gui_clear_history():
            st = application_gui_selected_stock()
            if not st: return
            if messagebox.askyesno("Clear History", f"Remove all history for {st.symbol}?"):
                st.DataList = []
                self.display_stock_data()

        
        

        report_toolbar = Frame(gui_report_tab)
        report_toolbar.pack(fill=X, padx=3.5, pady=(4,0))
        Button(report_toolbar, text="Generate Report", command=lambda: app_gui_generate_report()).pack(side=LEFT, padx=4)
        Button(report_toolbar, text="Export Report", command=lambda: app_gui_export_report()).pack(side=LEFT, padx=4)
        Button(report_toolbar, text="Clear Report", command=lambda: self.gui_stockReport.delete("1.0", END)).pack(side=LEFT, padx=4)

        def app_gui_generate_report():
            try:
                symbol = self.gui_stock_list.get(self.gui_stock_list.curselection())
            except Exception:
                messagebox.showwarning("No Stock Selected", "Select a stock first."); return
            st = next((sto for sto in self.stock_list if sto.symbol == symbol), None)
            if not st:
                messagebox.showwarning("Not Found", "Selected stock not found."); return
            lines = [f"Report for {st.symbol} - {getattr(st,'name','')}", "-"*40, f"Shares: {getattr(st,'shares',0)}"]
            if getattr(st,"DataList",None):
                latest = st.DataList[-1]; price = getattr(latest,"close",0)
                lines += [f"Latest Price: ${price:0,.2f}", f"Market Value: ${(getattr(st,'shares',0)*price):0,.2f}", ""]
                for d in reversed(st.DataList[-10:]): lines.append(f"{getattr(d,'date','')}  Close: {getattr(d,'close','')}")
            else:
                lines.append("No historical data available.")
            self.gui_stockReport.delete("1.0", END); self.gui_stockReport.insert(END, "\n".join(lines))

        def app_gui_export_report():
            content = self.gui_stockReport.get("1.0", END).strip()
            if not content:
                messagebox.showinfo("Empty", "Generate a report first"); return

            fn = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")])

            if not fn: return
            with open(fn, "w", encoding="utf-8") as fi: fi.write(content)



        self.root.mainloop()


    def load(self):
        self.gui_stock_list.delete(0,END)
        stock_data.load_stock_data(self.stock_list)
        sortStocks(self.stock_list)
        for stock in self.stock_list:
            self.gui_stock_list.insert(END,stock.symbol)
        self.update_heading_summary()
        messagebox.showinfo("Load Data","Data Loaded")


    def save(self):
        stock_data.save_stock_data(self.stock_list)
        messagebox.showinfo("Save Data","Data Saved")

  
    def update_data(self, evt):
        self.display_stock_data()


    def display_stock_data(self):
        symbol = self.gui_stock_list.get(self.gui_stock_list.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                self.gui_heading_label['text'] = stock.name + " - " + str(stock.shares) + " Shares"
                self.gui_dailyDataList.delete("1.0",END)
                self.gui_stockReport.delete("1.0",END)
                self.gui_dailyDataList.insert(END,"- Date -   - Price -   - Volume -\n")
                self.gui_dailyDataList.insert(END,"=================================\n")
                for daily_data in stock.DataList:
                    row = daily_data.date.strftime("%m/%d/%y") + "   " +  '${:0,.2f}'.format(daily_data.close) + "   " + str(daily_data.volume) + "\n"
                    self.gui_dailyDataList.insert(END,row)




                    

    

    def add_stock(self):
        new_stock = Stock(self.gui_addSymbolEntry.get(),self.gui_addNameEntry.get(),float(str(self.gui_addSharesEntry.get())))
        self.stock_list.append(new_stock)
        self.gui_stock_list.insert(END,self.gui_addSymbolEntry.get())
        self.gui_addSymbolEntry.delete(0,END)
        self.gui_addNameEntry.delete(0,END)
        self.gui_addSharesEntry.delete(0,END)


    def buy_shares(self):
        symbol = self.gui_stock_list.get(self.gui_stock_list.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                stock.buy(float(self.gui_updateSharesEntry.get()))
                self.gui_heading_label['text'] = stock.name + " - " + str(stock.shares) + " Shares"
        messagebox.showinfo("Buy Shares","Shares Purchased")
        self.gui_updateSharesEntry.delete(0,END)


    def sell_shares(self):
        symbol = self.gui_stock_list.get(self.gui_stock_list.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                stock.sell(float(self.gui_updateSharesEntry.get()))
                self.gui_heading_label['text'] = stock.name + " - " + str(stock.shares) + " Shares"
        messagebox.showinfo("Sell Shares","Shares Sold")
        self.gui_updateSharesEntry.delete(0,END)

    def delete_stock(self):
        if not self.stock_list:
            messagebox.showwarning("Nothing available to delete.")
            return

        try:
            symbol = self.gui_stock_list.get(self.gui_stock_list.curselection())
        except TclError:
            messagebox.showwarning("Select a stock/ticker")
            return
        
        if not messagebox.askyesno("Confirm Delete Operation", 
                                f"Are you sure about deleting {symbol} stock"):
            return
        
        for s in self.stock_list:
            if symbol == s.symbol:
                self.stock_list.remove(s)
                break
        
        self.gui_populate_stock_list()
        self.gui_heading_label.config(text="Stock Not Selected")
        self.gui_dailyDataList.delete("1.0", END)
        self.gui_stockReport.delete("1.0", END)
        
        messagebox.showinfo("Deleted Stock {symbol}")


    # Get data from web scraping.
    def scrape_web_data(self):
        dateFrom = simpledialog.askstring("Starting Date","Enter Starting Date (m/d/yy)")
        dateTo = simpledialog.askstring("Ending Date","Enter Ending Date (m/d/yy")
        try:
            stock_data.retrieve_stock_web(dateFrom,dateTo,self.stock_list)
        except:
            messagebox.showerror("Cannot Get Data from Web","Check Path for Chrome Driver")
            return
        self.display_stock_data()
        messagebox.showinfo("Get Data From Web","Data Retrieved")
 

    def importCSV_web_data(self):
        try:
            symbol = self.gui_stock_list.get(self.gui_stock_list.curselection())
        except TclError:
            messagebox.showwarning("No Stock has been selected please select a stock.")
            return
        
        filename = filedialog.askopenfilename(
            title=f"Select {symbol} CSV File to Import",
            filetypes=[('Yahoo Finance CSV','*.csv'), ('All Files','*.*')]
        )
        if not filename:
            return
        
        try:
            imported_count = stock_data.import_stock_web_csv(self.stock_list, symbol, filename)
            
            self.display_stock_data()
            messagebox.showinfo(
                "Import has been Completed Successfully", f"Successfully imported {imported_count} records for {symbol}"
            )
            
        except FileNotFoundError as er:
            messagebox.showerror("Got File Error", str(er))
        except ValueError as er:
            messagebox.showerror("Got Data Error", str(er))
        except Exception as er:
            messagebox.showerror("An unexpected error has happened: ", str(er))
    

    def display_chart(self):
        symbol = self.gui_stock_list.get(self.gui_stock_list.curselection())
        display_stock_chart(self.stock_list,symbol)


def main():
        app = StockApp()
        

if __name__ == "__main__":

    main()