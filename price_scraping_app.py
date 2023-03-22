import requests
from time import sleep
from bs4 import BeautifulSoup
from random import randint
import customtkinter as ct
from tkinter import messagebox
from tkinter import PhotoImage
import mysql.connector as mysql
from datetime import datetime
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, DatetimeTickFormatter
from bokeh.io import curdoc
import itertools


def create_window(appearance="system", color_theme="green", title="AppTitle",
                  background_color="#1e1e1e"):
    appearance = appearance
    color_theme = color_theme
    title = title
    ct.set_appearance_mode(appearance)
    ct.set_default_color_theme(color_theme)
    window = ct.CTk()
    window.configure(fg_color=background_color)
    window.title(title)
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    window.geometry(f"{width}x{height}+0+0")
    window.resizable(True, True)
    app_logo = PhotoImage(file=r"C:\Users\georg\PycharmProjects\emagapp\app_logo_2.png")
    return window, width, height, app_logo


def create_frame(container, background_color="#1e1e1e"):
    return ct.CTkFrame(container, fg_color=background_color)


def scrapping_data(product, url, best_price):
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/109.0.0.0 Safari/537.36'}
    html_text = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_text, "lxml")
    try:
        _current_price = soup.find("p", class_="product-new-price").getText()
        return buy_or_not(_current_price, product, best_price)
    except AttributeError:
        _current_price = soup.find("p", class_="product-new-price has-deal").getText()
        return buy_or_not(_current_price, product, best_price)


def buy_or_not(current_price, product, best_price, mysql_user, mysql_password, db_name):
    # Handle scenario with text in price area
    if "de la " in current_price:
        new_current_price = current_price.replace("de la ", "")
    else:
        new_current_price = current_price
    # Handle scenario with multiple . symbols in price
    count_points = new_current_price.count(".")
    if count_points == 1:
        new_current_price = new_current_price.replace(".", "")
    if float(new_current_price.split()[0].replace(",", ".")) < float(best_price):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        myDB = mysql.connect(host="localhost", user=mysql_user, passwd=mysql_password, database=db_name)
        mycursor = myDB.cursor(buffered=True)
        sql = "INSERT INTO outputs (product_name, target_price, current_price, date_time) VALUES (%s, %s, %s, %s)"
        val = (product, best_price, float(new_current_price.split()[0].replace(",", ".")), date_time)
        mycursor.execute(sql, val)
        myDB.commit()
        mycursor.execute(f"SELECT current_price FROM outputs WHERE product_name= '{product}' ORDER BY current_price")
        min_recorded = mycursor.fetchone()[0]
        mycursor.close()
        myDB.close()
        return "BUY", f"{product}", f"{float(new_current_price.split()[0].replace(',', '.'))} Lei", f"{best_price} Lei", f'{float("{:.2f}".format(float(new_current_price.split()[0].replace(",", ".")) - float(best_price)))} Lei ', f'{min_recorded} Lei'
    else:
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        myDB = mysql.connect(host="localhost", user=mysql_user, passwd=mysql_password, database=db_name)
        mycursor = myDB.cursor(buffered=True)
        sql = "INSERT INTO outputs (product_name, target_price, current_price, date_time) VALUES (%s, %s, %s, %s)"
        val = (product, best_price, float(new_current_price.split()[0].replace(",", ".")), date_time)
        mycursor.execute(sql, val)
        myDB.commit()
        mycursor.execute(f"SELECT current_price FROM outputs WHERE product_name= '{product}' ORDER BY current_price")
        min_recorded = mycursor.fetchone()[0]
        mycursor.close()
        myDB.close()
        return "Do not buy", f"{product}", f"{float(new_current_price.split()[0].replace(',', '.'))} Lei", f"{best_price} Lei", f'{float("{:.2f}".format(float(new_current_price.split()[0].replace(",", ".")) - float(best_price)))} Lei ', f'{min_recorded} Lei'


def get_products_from_db(mysql_user, mysql_password, db_name):
    myDB = mysql.connect(host="localhost", user=mysql_user, passwd=mysql_password, database=db_name)
    mycursor = myDB.cursor(buffered=True)
    mycursor.execute(f"SELECT product_name, product_url, target_price FROM inputs")
    results = mycursor.fetchall()
    data = []
    for result in results:
        data.append(list(result))
    mycursor.close()
    myDB.close()
    return data


class App():
    def __init__(self, mysql_user, mysql_password, db_name):
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.db_name = db_name
        self.window, self.width, self.height, self.app_logo = create_window(title="priceZ",
                                                                            color_theme="blue")
        self.main_frame = create_frame(container=self.window)
        self.main_frame.pack()
        self.check_prices_btn = ct.CTkButton(self.main_frame, text=" Check prices ",
                                             font=("Calibri", 20), fg_color="green")
        self.check_prices_btn.bind("<ButtonRelease-1>", self.check_prices)
        self.see_products_btn = ct.CTkButton(self.main_frame, text=" See products ",
                                             font=("Calibri", 20))
        self.see_products_btn.bind("<ButtonRelease-1>", self.read_page)
        self.add_product_btn = ct.CTkButton(self.main_frame, text=" Add product  ",
                                            font=("Calibri", 20))
        self.add_product_btn.bind("<ButtonRelease-1>", self.insert_page)
        self.delete_product_btn = ct.CTkButton(self.main_frame, text="Delete product",
                                               font=("Calibri", 20))
        self.delete_product_btn.bind("<ButtonRelease-1>", self.delete_page)
        self.exit_btn = ct.CTkButton(self.main_frame, text="     Exit     ", fg_color="#BC544B",
                                     command=lambda: self.exit_func(), font=("Calibri", 20))
        self.update_btn = ct.CTkButton(self.main_frame, text="Update details", font=("Calibri", 20))
        self.update_btn.bind("<ButtonRelease-1>", self.update_page)
        self.statistics_btn = ct.CTkButton(self.main_frame, text="      Statistics    ",
                                           font=("Calibri", 20))
        self.statistics_btn.bind("<ButtonRelease-1>", self.statistics_page)
        self.check_prices_btn.grid(column=0, row=0, padx=10, pady=5)
        self.see_products_btn.grid(column=1, row=0, padx=10, pady=5)
        self.add_product_btn.grid(column=2, row=0, padx=10, pady=5)
        self.delete_product_btn.grid(column=3, row=0, padx=10, pady=5)
        self.exit_btn.grid(column=4, row=0, padx=10, pady=5)
        self.update_btn.grid(column=2, row=1, padx=10, pady=5)
        self.statistics_btn.grid(column=2, row=2, padx=10, pady=5)
        self.logo = ct.CTkLabel(self.window, image=self.app_logo, text=" ")
        self.logo.pack(pady=100)
        self.window.mainloop()

    def exit_func(self):
        if messagebox.askyesno(title="Exit?", message="Are you sure you want to exit?"):
            self.window.quit()

    def insert_page(self, event):
        self.add_frame = ct.CTkFrame(self.window, fg_color="#1e1e1e", height=self.height, width=self.width)
        self.add_frame.place(x=0, y=0)
        self.product_name = ct.CTkLabel(self.add_frame, text="Product name:", font=("Serif", 20))
        self.product_name_box = ct.CTkEntry(self.add_frame, width=400, font=("Serif", 20))
        self.product_url = ct.CTkLabel(self.add_frame, text="Product URL: ", font=("Serif", 20))
        self.product_url_box = ct.CTkEntry(self.add_frame, width=400, font=("Serif", 20))
        self.target_price = ct.CTkLabel(self.add_frame, text=" Target price:", font=("Serif", 20))
        self.target_price_box = ct.CTkEntry(self.add_frame, width=400, font=("Serif", 20))
        self.insert_details_button = ct.CTkButton(self.add_frame, text="--> Submit   ", font=("Calibri", 20))
        self.insert_details_button.bind("<ButtonRelease-1>", self.add_to_db)
        self.product_name.place(x=40, y=200)
        self.product_name_box.place(x=350, y=200)
        self.product_url.place(x=40, y=250)
        self.product_url_box.place(x=350, y=250)
        self.target_price.place(x=40, y=300)
        self.target_price_box.place(x=350, y=300)
        self.insert_details_button.place(x=200, y=400)
        self.back_button = ct.CTkButton(self.add_frame, text="<--Back to main menu", font=("Calibri", 20),
                                        command=lambda: self.add_frame.destroy())
        self.back_button.place(x=1400, y=60)

    def add_to_db(self, event):
        _product_name = self.product_name_box.get()
        _product_url = self.product_url_box.get()
        _target_price = self.target_price_box.get()
        try:
            myDB = mysql.connect(host="localhost", user=self.mysql_user, passwd=self.mysql_password,
                                 database=self.db_name)
            mycursor = myDB.cursor(buffered=True)
            sql = "INSERT INTO inputs (product_name, product_url, target_price) VALUES (%s, %s, %s)"
            val = (_product_name, _product_url, _target_price)
            mycursor.execute(sql, val)
            myDB.commit()
            messagebox.showinfo("Success", "New product added")
            self.product_name_box.delete(0, ct.END)
            self.product_url_box.delete(0, ct.END)
            self.target_price_box.delete(0, ct.END)
            mycursor.close()
            myDB.close()
        except:
            messagebox.showinfo("Error", "Please contact developer")

    def read_page(self, event):
        self.add_frame = ct.CTkFrame(self.window, fg_color="#1e1e1e", height=self.height, width=self.width)
        self.add_frame.place(x=0, y=0)
        self.back_button = ct.CTkButton(self.add_frame, text="<--Back to main menu", font=("Calibri", 20),
                                        command=lambda: self.add_frame.destroy())
        self.back_button.place(x=1400, y=60)
        self.read_intro = ct.CTkLabel(self.add_frame, text="Current products in scope:", fg_color="#1e1e1e",
                                      font=("Calibri", 20, "bold"))
        self.read_intro.place(x=40, y=60)
        self.tabel_widget = ct.CTkFrame(self.add_frame)
        self.tabel_widget.place(x=40, y=110)
        table_content = get_products_from_db(self.mysql_user, self.mysql_password, self.db_name)
        array = [["Product_name", "Target_price"]]
        _temp_list = []
        for item in table_content:
            array.append([item[0], (str(item[2]) + " lei")])
        for x, y in itertools.product(range(len(array)), range(len(array[0]))):
            self.t = ct.CTkTextbox(self.tabel_widget, fg_color="#1e1e1e", font=("Calibri", 18), width=500, height=1,
                                   border_width=1)
            self.t.grid(row=2 + x, column=y)
            self.t.insert(ct.END, array[x][y])

    def delete_page(self, event):
        self.file_products = get_products_from_db(self.mysql_user, self.mysql_password, self.db_name)
        product_names = [item[0] for item in self.file_products]
        self.add_frame = ct.CTkFrame(self.window, fg_color="#1e1e1e", height=self.height, width=self.width)
        self.add_frame.place(x=0, y=0)
        self.back_button = ct.CTkButton(self.add_frame, text="<--Back to main menu", font=("Calibri", 20),
                                        command=lambda: self.add_frame.destroy())
        self.back_button.place(x=1400, y=60)
        self.read_intro = ct.CTkLabel(self.add_frame, text="Current products in scope:",
                                      fg_color="#1e1e1e",
                                      font=("Calibri", 20, "bold"))
        self.read_intro.place(x=40, y=60)
        self.clicked = ct.StringVar()
        self.clicked.set("Select product...")
        drop = ct.CTkOptionMenu(self.add_frame, variable=self.clicked, values=product_names, font=("Calibri", 20))
        drop.place(x=40, y=150)
        self.delete_selected_button = ct.CTkButton(self.add_frame, text="--> Delete", font=("Calibri", 20),
                                                   fg_color="#BC544B")
        self.delete_selected_button.bind("<ButtonRelease-1>", self.delete_from_db)
        self.delete_selected_button.place(x=1400, y=400)

    def delete_from_db(self, event):
        choice = self.clicked.get()
        try:
            myDB = mysql.connect(host="localhost", user=self.mysql_user, passwd=self.mysql_password,
                                 database=self.db_name)
            mycursor = myDB.cursor(buffered=True)
            sql = f"DELETE FROM inputs WHERE product_name = '{choice}'"
            mycursor.execute(sql)
            myDB.commit()
            messagebox.showinfo("Success", "Product deleted")
            self.add_frame.destroy()
            self.delete_page("event")
            mycursor.close()
            myDB.close()
        except:
            messagebox.showinfo("Error", "Please contact developer")

    def check_prices(self, event):
        self.file_products = get_products_from_db(self.mysql_user, self.mysql_password, self.db_name)
        self.add_frame = ct.CTkFrame(self.window, fg_color="#1e1e1e", height=self.height, width=self.width)
        self.add_frame.place(x=0, y=0)
        self.read_intro = ct.CTkLabel(self.add_frame, text="Current status:", fg_color="#1e1e1e",
                                      font=("Calibri", 20, "bold"))
        self.read_intro.place(x=40, y=60)
        self.back_button = ct.CTkButton(self.add_frame, text="<--Back to main menu", font=("Calibri", 20),
                                        command=lambda: self.add_frame.destroy())
        self.back_button.place(x=1400, y=60)
        self.tabel_widget = ct.CTkLabel(self.add_frame)
        self.tabel_widget.place(x=10, y=110)
        array = [["Advice", "Product name", "Current price", "Target price", "Difference", "Min_Recorded"]]
        for item in self.file_products:
            try:
                array.append(scrapping_data(item[0], item[1], item[2]))
                sleep(randint(11, 20))
            except AttributeError:
                messagebox.showinfo("Error", "Capcha error")
        for x, y in itertools.product(range(len(array)), range(len(array[0]))):
            self.t = ct.CTkTextbox(self.tabel_widget, fg_color="#1e1e1e", font=("Calibri", 14), width=270, height=1,
                                   border_width=1)
            self.t.grid(row=x, column=y)
            self.t.insert(ct.END, array[x][y])
        # for x in range(len(array)):
        #     for y in range(len(array[0])):
        #         self.t = ct.CTkTextbox(self.tabel_widget, fg_color="#1e1e1e", font=("Calibri", 14), width=260, height=1)
        #         self.t.grid(row=x, column=y)
        #         self.t.insert(ct.END, array[x][y])

    def statistics_page(self, event):
        self.file_products = get_products_from_db(self.mysql_user, self.mysql_password, self.db_name)
        product_names = [item[0] for item in self.file_products]
        self.add_frame = ct.CTkFrame(self.window, fg_color="#1e1e1e", height=self.height, width=self.width)
        self.add_frame.place(x=0, y=0)
        self.back_button = ct.CTkButton(self.add_frame, text="<--Back to main menu", font=("Calibri", 20),
                                        command=lambda: self.add_frame.destroy())
        self.back_button.place(x=1400, y=60)
        self.read_intro = ct.CTkLabel(self.add_frame, text="Current products in scope:",
                                      fg_color="#1e1e1e",
                                      font=("Calibri", 20, "bold"))
        self.read_intro.place(x=40, y=60)
        self.clicked = ct.StringVar()
        self.clicked.set("Select product...")
        drop = ct.CTkOptionMenu(self.add_frame, variable=self.clicked, values=product_names, font=("Calibri", 20))
        drop.place(x=40, y=150)
        self.get_info_button = ct.CTkButton(self.add_frame, text="--> Get info", font=("Calibri", 20))
        self.get_info_button.bind("<ButtonRelease-1>", self.additional_info)
        self.get_info_button.place(x=1400, y=150)

    def additional_info(self, event):
        self.choice = self.clicked.get()
        self.get_info_button.destroy()
        try:
            myDB = mysql.connect(host="localhost", user=self.mysql_user, passwd=self.mysql_password,
                                 database=self.db_name)
            mycursor = myDB.cursor(buffered=True)
            mycursor.execute(
                f"SELECT current_price FROM outputs WHERE product_name= '{self.choice}' ORDER BY current_price")
            min_recorded = mycursor.fetchone()[0]
            self.min_price = ct.CTkLabel(self.add_frame, text=f" Min price recorded: {min_recorded} Lei",
                                         font=("Serif", 20))
            self.min_price.place(x=40, y=300)
            mycursor.execute(
                f"SELECT current_price FROM outputs WHERE product_name= '{self.choice}' ORDER BY current_price DESC")
            max_recorded = mycursor.fetchone()[0]
            self.max_price = ct.CTkLabel(self.add_frame, text=f" Max price recorded: {max_recorded} Lei",
                                         font=("Serif", 20))
            self.max_price.place(x=40, y=350)
            mycursor.execute(
                f"SELECT current_price FROM outputs WHERE product_name= '{self.choice}' ORDER BY date_time DESC")
            recent_recorded = mycursor.fetchone()[0]
            self.recent_price = ct.CTkLabel(self.add_frame, text=f" Most recent price recorded: {recent_recorded} Lei",
                                            font=("Serif", 20))
            self.recent_price.place(x=40, y=450)
            mycursor.execute(f"SELECT current_price FROM outputs WHERE product_name= '{self.choice}'")
            results = mycursor.fetchall()
            sum = 0
            items = 0
            for index, result in enumerate(results):
                sum += result[0]
                items = index + 1
            average = sum / items
            self.average_price = ct.CTkLabel(self.add_frame, text=f" Average price recorded: {'%.2f' % average} Lei",
                                             font=("Serif", 20))
            self.average_price.place(x=40, y=400)
            for product_detail in self.file_products:
                if product_detail[0] == self.choice:
                    target_price = product_detail[2]
                    self.target_price_lbl = ct.CTkLabel(self.add_frame, text=f" Target price: {target_price} Lei",
                                                        font=("Serif", 20))
                    self.target_price_lbl.place(x=40, y=250)
            self.get_graph_button = ct.CTkButton(self.add_frame, text="--> Get graph", font=("Calibri", 20))
            self.get_graph_button.bind("<ButtonRelease-1>", self.graph_from_db)
            self.get_graph_button.place(x=800, y=550)
            mycursor.close()
            myDB.close()
        except:
            messagebox.showinfo("Error", "Please contact developer")

    def graph_from_db(self, event):
        myDB = mysql.connect(host="localhost", user=self.mysql_user, passwd=self.mysql_password, database=self.db_name)
        mycursor = myDB.cursor(buffered=True)
        mycursor.execute(f"SELECT current_price, date_time FROM outputs WHERE product_name= '{self.choice}'")
        myresult = mycursor.fetchall()
        data = []
        for item in myresult:
            data.append((item[0], item[1]))
        df = pd.DataFrame(data, columns=["Price", "Date"])
        curdoc().theme = "dark_minimal"
        tooltips = HoverTool(tooltips=[
            ("index", "$index"),
            ("Date", "$x{%F}"), ("Price", "@Price"),
        ], formatters={"$x": "datetime"})
        p = figure(title="Historical data", x_axis_label="Date", x_axis_type="datetime", y_axis_label="Price",
                   tools=[tooltips], width=self.width - 50,
                   height=self.height - 120)
        p.circle("Date", "Price", size=10, source=df)
        p.line(source=df, x="Date", y="Price", color="red", line_width=1)
        p.xaxis[0].formatter = DatetimeTickFormatter(months="%Y-%m-%d")
        show(p)
        mycursor.close()
        myDB.close()

    def update_page(self, event):
        self.add_frame = ct.CTkFrame(self.window, fg_color="#1e1e1e", height=self.height, width=self.width)
        self.add_frame.place(x=0, y=0)
        self.update_button = ct.CTkButton(self.add_frame, text="Update details",
                                          font=("Calibri", 20), fg_color="green")
        self.update_button.bind("<ButtonRelease-1>", self.update_func)
        self.update_button.place(x=1400, y=500)
        self.back_button = ct.CTkButton(self.add_frame, text="<--Back to main menu", font=("Calibri", 20),
                                        command=lambda: self.add_frame.destroy())
        self.back_button.place(x=1400, y=60)
        self.file_products = get_products_from_db(self.mysql_user, self.mysql_password, self.db_name)
        product_names = [item[0] for item in self.file_products]
        self.read_intro = ct.CTkLabel(self.add_frame, text="Current products in scope:",
                                      fg_color="#1e1e1e",
                                      font=("Calibri", 20, "bold"))
        self.read_intro.place(x=40, y=80)
        self.clicked = ct.StringVar()
        self.clicked.set("Select product...")
        drop = ct.CTkOptionMenu(self.add_frame, variable=self.clicked, values=product_names, font=("Calibri", 20))
        drop.place(x=40, y=140)
        self.fetch_button = ct.CTkButton(self.add_frame, text="Fetch data",
                                         font=("Calibri", 20))
        self.fetch_button.bind("<ButtonRelease-1>", self.option_menu_answer)
        self.fetch_button.place(x=1400, y=110)

    def update_func(self, event):
        _product_name = self.product_name_box.get()
        _product_url = self.product_url_box.get()
        _target_price = self.target_price_box.get()
        try:
            myDB = mysql.connect(host="localhost", user=self.mysql_user, passwd=self.mysql_password,
                                 database=self.db_name)
            mycursor = myDB.cursor(buffered=True)
            sql = f"UPDATE inputs SET product_name = '{_product_name}', product_url= '{_product_url}', target_price = '{_target_price}' WHERE ID = '{self.id}'"
            mycursor.execute(sql)
            myDB.commit()
            messagebox.showinfo("Success", "Details updated")
            self.product_name_box.delete(0, ct.END)
            self.product_url_box.delete(0, ct.END)
            self.target_price_box.delete(0, ct.END)
            mycursor.close()
            myDB.close()
        except:
            messagebox.showinfo("Error", "Please contact developer")

    def option_menu_answer(self, event):
        choice = self.clicked.get()
        try:
            myDB = mysql.connect(host="localhost", user=self.mysql_user, passwd=self.mysql_password,
                                 database=self.db_name)
            mycursor = myDB.cursor(buffered=True)
            sql = f"SELECT *  FROM inputs WHERE product_name = '{choice}'"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            self.product_name = ct.CTkLabel(self.add_frame, text="Product name:", font=("Serif", 20))
            self.product_name_box = ct.CTkEntry(self.add_frame, width=400, font=("Serif", 20))
            self.product_url = ct.CTkLabel(self.add_frame, text="Product URL: ", font=("Serif", 20))
            self.product_url_box = ct.CTkEntry(self.add_frame, width=400, font=("Serif", 20))
            self.target_price = ct.CTkLabel(self.add_frame, text=" Target price:", font=("Serif", 20))
            self.target_price_box = ct.CTkEntry(self.add_frame, width=400, font=("Serif", 20))
            self.product_name.place(x=40, y=200)
            self.product_name_box.place(x=350, y=200)
            self.product_url.place(x=40, y=250)
            self.product_url_box.place(x=350, y=250)
            self.target_price.place(x=40, y=300)
            self.target_price_box.place(x=350, y=300)
            for item in myresult:
                self.id = item[0]
                self.product_name_box.delete(0, ct.END)
                self.product_name_box.insert(0, f"{item[1]}")
                self.product_url_box.delete(0, ct.END)
                self.product_url_box.insert(0, f"{item[2]}")
                self.target_price_box.delete(0, ct.END)
                self.target_price_box.insert(0, f"{item[3]}")
            mycursor.close()
            myDB.close()
        except:
            messagebox.showinfo("Error", "Please contact developer")


if __name__ == '__main__':
    app = App(mysql_user="", mysql_password="", db_name="")
