import requests
from time import sleep
from bs4 import BeautifulSoup
from random import randint
from tkinter import *
from tkinter import messagebox
import mysql.connector as mysql
from datetime import datetime
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, DatetimeTickFormatter
from bokeh.io import curdoc


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


def buy_or_not(current_price, product, best_price):
    if "de la " in current_price:
        new_current_price = current_price.replace("de la ", "")
    else:
        new_current_price = current_price
    count_points = new_current_price.count(".")
    if count_points == 1:
        new_current_price = new_current_price.replace(".", "")
    if float(new_current_price.split()[0].replace(",", ".")) < float(best_price):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        myDB = mysql.connect(host="localhost", user="root", passwd="mysqlPassword@", database="emag")
        mycursor = myDB.cursor(buffered=True)
        sql = "INSERT INTO outputs (product_name, target_price, current_price, date_time) VALUES (%s, %s, %s, %s)"
        val = (product, best_price, float(new_current_price.split()[0].replace(",", ".")), date_time)
        mycursor.execute(sql, val)
        myDB.commit()
        mycursor.execute(f"SELECT current_price FROM outputs WHERE product_name= '{product}' ORDER BY current_price")
        min_recorded = mycursor.fetchone()[0]
        mycursor.close()
        myDB.close()
        return "BUY", f"{product}", f"{float(new_current_price.split()[0].replace(',', '.'))} Lei", f"{best_price} Lei", f'{int(float(new_current_price.split()[0].replace(",", ".")) - float(best_price))} Lei ', f'{min_recorded} Lei'
    else:
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        myDB = mysql.connect(host="localhost", user="root", passwd="mysqlPassword@", database="emag")
        mycursor = myDB.cursor(buffered=True)
        sql = "INSERT INTO outputs (product_name, target_price, current_price, date_time) VALUES (%s, %s, %s, %s)"
        val = (product, best_price, float(new_current_price.split()[0].replace(",", ".")), date_time)
        mycursor.execute(sql, val)
        myDB.commit()
        mycursor.execute(f"SELECT current_price FROM outputs WHERE product_name= '{product}' ORDER BY current_price")
        min_recorded = mycursor.fetchone()[0]
        mycursor.close()
        myDB.close()
        return "Do not buy", f"{product}", f"{float(new_current_price.split()[0].replace(',', '.'))} Lei", f"{best_price} Lei", f'{int(float(new_current_price.split()[0].replace(",", ".")) - float(best_price))} Lei', f'{min_recorded} Lei'


def get_products_from_db():
    myDB = mysql.connect(host="localhost", user="root", passwd="mysqlPassword@", database="emag")
    mycursor = myDB.cursor(buffered=True)
    mycursor.execute("SELECT product_name, product_url, target_price FROM inputs")
    results = mycursor.fetchall()
    data = []
    for result in results:
        data.append(list(result))
    mycursor.close()
    myDB.close()
    return data


class App():
    def __init__(self):
        self.window = Tk()
        self.window.title("eMAG priceZ")
        self.width = self.window.winfo_screenwidth()
        self.height = self.window.winfo_screenheight()
        self.window.geometry("%dx%d" % (self.width, self.height))
        self.window.state('zoomed')
        self.window.resizable(True, True)
        self.window.configure(bg="#31473A")
        cat_icon = PhotoImage(file=r"C:\Users\georg\PycharmProjects\emagapp\cat.png")
        app_logo = PhotoImage(file=r"C:\Users\georg\PycharmProjects\emagapp\app_logo_2.png")
        self.window.iconphoto(False, cat_icon)
        self.check_prices_btn = Button(self.window, text=" Check prices ", bg="#7C8363", fg="#EDF4F2",
                                       font=("Calibri", 14))
        self.check_prices_btn.bind("<ButtonRelease-1>", self.check_prices)
        self.see_products_btn = Button(self.window, text=" See products ", bg="#A36A00", fg="#EDF4F2",
                                       font=("Calibri", 14))
        self.see_products_btn.bind("<ButtonRelease-1>", self.read_page)
        self.add_product_btn = Button(self.window, text=" Add product  ", bg="#A36A00", fg="#EDF4F2",
                                      font=("Calibri", 14))
        self.add_product_btn.bind("<ButtonRelease-1>", self.insert_page)
        self.delete_product_btn = Button(self.window, text="Delete product", bg="#A36A00", fg="#EDF4F2",
                                         font=("Calibri", 14))
        self.delete_product_btn.bind("<ButtonRelease-1>", self.delete_page)
        self.exit_btn = Button(self.window, text="     Exit     ", command=lambda: self.exit_func(), bg="#7C8363",
                               fg="#EDF4F2", font=("Calibri", 14))
        self.statistics_btn = Button(self.window, text="      Statistics    ", bg="#7C8363", fg="#EDF4F2",
                                     font=("Calibri", 14))
        self.statistics_btn.bind("<ButtonRelease-1>", self.statistics_page)
        self.update_btn = Button(self.window, text="Update details",bg="#A36A00", fg="#EDF4F2", font=("Calibri", 14))
        self.update_btn.bind("<ButtonRelease-1>", self.update_page)
        self.check_prices_btn.place(x=500, y=60)
        self.see_products_btn.place(x=650, y=60)
        self.add_product_btn.place(x=800, y=60)
        self.update_btn.place(x=800, y=110)
        self.statistics_btn.place(x=800, y=160)
        self.delete_product_btn.place(x=950, y=60)
        self.exit_btn.place(x=1110, y=60)
        self.image_frame = Label(self.window, image=app_logo, bg="#31473A")
        self.image_frame.place(x=575, y=200)
        self.window.mainloop()

    def exit_func(self):
        if messagebox.askyesno(title="Exit?", message="Are you sure you want to exit?"):
            self.window.quit()

    def insert_page(self, event):
        self.add_frame = Frame(self.window, bg="#31473A")
        self.add_frame.place(x=0, y=0, height=self.height, width=self.width)
        self.product_name = Label(self.add_frame, text="Product name:", font=("Serif", 15))
        self.product_name_box = Entry(self.add_frame, width=50, font=("Serif", 15))
        self.product_url = Label(self.add_frame, text="Product URL: ", font=("Serif", 15))
        self.product_url_box = Entry(self.add_frame, width=50, font=("Serif", 15))
        self.target_price = Label(self.add_frame, text=" Target price:", font=("Serif", 15))
        self.target_price_box = Entry(self.add_frame, width=50, font=("Serif", 15))
        self.insert_details_button = Button(self.add_frame, text="--> Submit   ", font=("Calibri", 15), bg="#A36A00",
                                            fg="#EDF4F2")
        self.insert_details_button.bind("<ButtonRelease-1>", self.add_to_db)
        self.product_name.place(x=40, y=200)
        self.product_name_box.place(x=350, y=200)
        self.product_url.place(x=40, y=250)
        self.product_url_box.place(x=350, y=250)
        self.target_price.place(x=40, y=300)
        self.target_price_box.place(x=350, y=300)
        self.insert_details_button.place(x=200, y=400)
        self.back_button = Button(self.add_frame, text="<--Back to main menu", font=("Calibri", 15),
                                  command=lambda: self.add_frame.destroy(), bg="#7C8363", fg="#EDF4F2")
        self.back_button.place(x=800, y=60)

    def add_to_db(self, event):
        _product_name = self.product_name_box.get()
        _product_url = self.product_url_box.get()
        _target_price = self.target_price_box.get()
        try:
            myDB = mysql.connect(host="localhost", user="root", passwd="mysqlPassword@", database="emag")
            mycursor = myDB.cursor(buffered=True)
            sql = "INSERT INTO inputs (product_name, product_url, target_price) VALUES (%s, %s, %s)"
            val = (_product_name, _product_url, _target_price)
            mycursor.execute(sql, val)
            myDB.commit()
            messagebox.showinfo("Success", "New product added")
            self.product_name_box.delete(0, END)
            self.product_url_box.delete(0, END)
            self.target_price_box.delete(0, END)
            mycursor.close()
            myDB.close()
        except:
            messagebox.showinfo("Error", "Please contact developer")

    def read_page(self, event):
        self.add_frame = Frame(self.window, bg="#31473A")
        self.add_frame.place(x=0, y=0, height=self.height, width=self.width)
        self.back_button = Button(self.add_frame, text="<--Back to main menu", font=("Calibri", 15),
                                  command=lambda: self.add_frame.destroy(), bg="#7C8363", fg="#EDF4F2")
        self.back_button.place(x=800, y=60)
        self.read_intro = Label(self.add_frame, text="Current products in scope:",
                                fg="white", bg="#31473A",
                                font=("Calibri", 15, "bold"))
        self.read_intro.place(x=40, y=60)
        self.tabel_widget = Label(self.add_frame)
        self.tabel_widget.place(x=40, y=110)
        table_content = get_products_from_db()
        array = [["Product_name", "Target_price"]]
        _temp_list = []
        for item in table_content:
            array.append([item[0], (str(item[2]) + " lei")])
        for x in range(len(array)):
            for y in range(len(array[0])):
                self.t = Text(self.tabel_widget, bg="#1B2121", fg="white", font=("Calibri", 14), width=30, height=1)
                self.t.grid(row=x, column=y)
                self.t.insert(END, array[x][y])

    def delete_page(self, event):
        self.file_products = get_products_from_db()
        product_names = [item[0] for item in self.file_products]
        self.add_frame = Frame(self.window, bg="#31473A")
        self.add_frame.place(x=0, y=0, height=self.height, width=self.width)
        self.back_button = Button(self.add_frame, text="<--Back to main menu", font=("Calibri", 15),
                                  command=lambda: self.add_frame.destroy(), bg="#7C8363", fg="#EDF4F2")
        self.back_button.place(x=800, y=60)
        self.read_intro = Label(self.add_frame, text="Current products in scope:",
                                fg="white", bg="#31473A",
                                font=("Calibri", 15, "bold"))
        self.read_intro.place(x=40, y=60)
        self.clicked = StringVar()
        self.clicked.set("Select product...")
        drop = OptionMenu(self.add_frame, self.clicked, *product_names)
        drop.config(font=("Calibri", 15))
        drop.place(x=40, y=150)
        self.delete_selected_button = Button(self.add_frame, text="--> Delete", font=("Calibri", 15), bg="#A36A00",
                                             fg="#EDF4F2")
        self.delete_selected_button.bind("<ButtonRelease-1>", self.delete_from_db)
        self.delete_selected_button.place(x=800, y=400)

    def delete_from_db(self, event):
        choice = self.clicked.get()
        try:
            myDB = mysql.connect(host="localhost", user="root", passwd="mysqlPassword@", database="emag")
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
        self.file_products = get_products_from_db()
        self.add_frame = Frame(self.window, bg="#31473A")
        self.add_frame.place(x=0, y=0, height=self.height, width=self.width)
        self.read_intro = Label(self.add_frame, text="Current status:",
                                fg="white", bg="#31473A",
                                font=("Calibri", 15, "bold"))
        self.read_intro.place(x=40, y=60)
        self.back_button = Button(self.add_frame, text="<--Back to main menu", font=("Calibri", 15),
                                  command=lambda: self.add_frame.destroy())
        self.back_button.place(x=800, y=60)
        self.tabel_widget = Label(self.add_frame)
        self.tabel_widget.place(x=40, y=110)
        array = [["Advice", "Product name", "Current price", "Target price", "Difference", "Min_Recorded"]]
        for item in self.file_products:
            try:
                array.append(scrapping_data(item[0], item[1], item[2]))
                sleep(randint(11, 20))
            except AttributeError:
                messagebox.showinfo("Error", "Capcha error")
        for x in range(len(array)):
            for y in range(len(array[0])):
                self.t = Text(self.tabel_widget, bg="#1B2121", fg="white", font=("Calibri", 14), width=25, height=1)
                self.t.grid(row=x, column=y)
                self.t.insert(END, array[x][y])

    def statistics_page(self, event):
        self.file_products = get_products_from_db()
        product_names = [item[0] for item in self.file_products]
        self.add_frame = Frame(self.window, bg="#31473A")
        self.add_frame.place(x=0, y=0, height=self.height, width=self.width)
        self.back_button = Button(self.add_frame, text="<--Back to main menu", font=("Calibri", 15),
                                  command=lambda: self.add_frame.destroy(), bg="#7C8363", fg="#EDF4F2")
        self.back_button.place(x=800, y=60)
        self.read_intro = Label(self.add_frame, text="Current products in scope:",
                                fg="white", bg="#31473A",
                                font=("Calibri", 15, "bold"))
        self.read_intro.place(x=40, y=60)
        self.clicked = StringVar()
        self.clicked.set("Select product...")
        drop = OptionMenu(self.add_frame, self.clicked, *product_names)
        drop.config(font=("Calibri", 15))
        drop.place(x=40, y=150)
        self.get_info_button = Button(self.add_frame, text="--> Get info", font=("Calibri", 15), bg="#A36A00",
                                      fg="#EDF4F2")
        self.get_info_button.bind("<ButtonRelease-1>", self.additional_info)
        self.get_info_button.place(x=800, y=150)

    def additional_info(self, event):
        self.choice = self.clicked.get()
        self.get_info_button.destroy()
        try:
            myDB = mysql.connect(host="localhost", user="root", passwd="mysqlPassword@", database="emag")
            mycursor = myDB.cursor(buffered=True)
            mycursor.execute(f"SELECT current_price FROM outputs WHERE product_name= '{self.choice}' ORDER BY current_price")
            min_recorded = mycursor.fetchone()[0]
            self.min_price = Label(self.add_frame, text=f" Min price recorded: {min_recorded} Lei", font=("Serif", 15))
            self.min_price.place(x=40, y=300)
            mycursor.execute(
                f"SELECT current_price FROM outputs WHERE product_name= '{self.choice}' ORDER BY current_price DESC")
            max_recorded = mycursor.fetchone()[0]
            self.max_price = Label(self.add_frame, text=f" Max price recorded: {max_recorded} Lei", font=("Serif", 15))
            self.max_price.place(x=40, y=350)
            mycursor.execute(
                f"SELECT current_price FROM outputs WHERE product_name= '{self.choice}' ORDER BY date_time DESC")
            recent_recorded = mycursor.fetchone()[0]
            self.recent_price = Label(self.add_frame, text=f" Most recent price recorded: {recent_recorded} Lei",
                                      font=("Serif", 15))
            self.recent_price.place(x=40, y=450)
            mycursor.execute(f"SELECT current_price FROM outputs WHERE product_name= '{self.choice}'")
            results = mycursor.fetchall()
            sum = 0
            items = 0
            for index, result in enumerate(results):
                sum += result[0]
                items = index + 1
            average = sum / items
            self.average_price = Label(self.add_frame, text=f" Average price recorded: {'%.2f' % average} Lei",
                                       font=("Serif", 15))
            self.average_price.place(x=40, y=400)
            for product_detail in self.file_products:
                if product_detail[0] == self.choice:
                    target_price = product_detail[2]
                    self.target_price_lbl = Label(self.add_frame, text=f" Target price: {target_price} Lei",
                                      font=("Serif", 15))
                    self.target_price_lbl.place(x=40, y=250)
            self.get_graph_button = Button(self.add_frame, text="--> Get graph", font=("Calibri", 15), bg="#A36A00",
                                          fg="#EDF4F2")
            self.get_graph_button.bind("<ButtonRelease-1>", self.graph_from_db)
            self.get_graph_button.place(x=800, y=550)
            mycursor.close()
            myDB.close()
        except:
            messagebox.showinfo("Error", "Please contact developer")


    def graph_from_db(self, event):
        myDB = mysql.connect(host="localhost", user="root", passwd="mysqlPassword@", database="emag")
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
                   tools=[tooltips], width=self.width-50,
                   height=self.height-120)
        p.circle("Date", "Price", size=10, source=df)
        p.line(source=df, x="Date", y="Price", color="red", line_width=1)
        p.xaxis[0].formatter = DatetimeTickFormatter(months="%Y-%m-%d")
        show(p)
        mycursor.close()
        myDB.close()


    def update_page(self, event):
        self.add_frame = Frame(self.window, bg="#31473A")
        self.add_frame.place(x=0, y=0, height=self.height, width=self.width)
        self.update_button = Button(self.add_frame, text="Update details", bg="#DAA7A2", fg="white",
                                    font=("Calibri", 15))
        self.update_button.bind("<ButtonRelease-1>", self.update_func)
        self.update_button.place(x=170, y=500)
        self.back_button = Button(self.add_frame, text="<--Back to main menu", font=("Calibri", 15),
                                  command=lambda: self.add_frame.destroy(), bg="#7C8363", fg="#EDF4F2")
        self.back_button.place(x=800, y=60)
        self.file_products = get_products_from_db()
        product_names = [item[0] for item in self.file_products]
        self.read_intro = Label(self.add_frame, text="Current products in scope:",
                                fg="white", bg="#31473A",
                                font=("Calibri", 15, "bold"))
        self.read_intro.place(x=40, y=80)
        self.clicked = StringVar()
        self.clicked.set("Select product...")
        drop = OptionMenu(self.add_frame, self.clicked, *product_names)
        drop.config(font=("Calibri", 15))
        drop.place(x=40, y=140)
        self.fetch_button = Button(self.add_frame, text="Fetch data", bg="#A36A00", fg="#EDF4F2",
                                         font=("Calibri", 15))
        self.fetch_button.bind("<ButtonRelease-1>", self.option_menu_answer)
        self.fetch_button.place(x=800, y=110)


    def update_func(self, event):
        _product_name = self.product_name_box.get()
        _product_url = self.product_url_box.get()
        _target_price = self.target_price_box.get()
        try:
            myDB = mysql.connect(host="localhost", user="root", passwd="mysqlPassword@", database="emag")
            mycursor = myDB.cursor(buffered=True)
            sql = f"UPDATE inputs SET product_name = '{_product_name}', product_url= '{_product_url}', target_price = '{_target_price}' WHERE ID = '{self.id}'"
            mycursor.execute(sql)
            myDB.commit()
            messagebox.showinfo("Success", "Details updated")
            self.product_name_box.delete(0, END)
            self.product_url_box.delete(0, END)
            self.target_price_box.delete(0, END)
            mycursor.close()
            myDB.close()
        except:
            messagebox.showinfo("Error", "Please contact developer")

    def option_menu_answer(self, event):
        choice = self.clicked.get()
        try:
            myDB = mysql.connect(host="localhost", user="root", passwd="mysqlPassword@", database="emag")
            mycursor = myDB.cursor(buffered=True)
            sql = f"SELECT *  FROM inputs WHERE product_name = '{choice}'"
            mycursor.execute(sql)
            myresult=mycursor.fetchall()
            self.product_name = Label(self.add_frame, text="Product name:", font=("Serif", 15))
            self.product_name_box = Entry(self.add_frame, width=50, font=("Serif", 15))
            self.product_url = Label(self.add_frame, text="Product URL: ", font=("Serif", 15))
            self.product_url_box = Entry(self.add_frame, width=50, font=("Serif", 15))
            self.target_price = Label(self.add_frame, text=" Target price:", font=("Serif", 15))
            self.target_price_box = Entry(self.add_frame, width=50, font=("Serif", 15))
            self.product_name.place(x=40, y=200)
            self.product_name_box.place(x=350, y=200)
            self.product_url.place(x=40, y=250)
            self.product_url_box.place(x=350, y=250)
            self.target_price.place(x=40, y=300)
            self.target_price_box.place(x=350, y=300)
            for item in myresult:
                self.id = item[0]
                self.product_name_box.delete(0,END)
                self.product_name_box.insert(0, f"{item[1]}")
                self.product_url_box.delete(0,END)
                self.product_url_box.insert(0, f"{item[2]}")
                self.target_price_box.delete(0,END)
                self.target_price_box.insert(0, f"{item[3]}")
            mycursor.close()
            myDB.close()
        except:
            messagebox.showinfo("Error", "Please contact developer")

if __name__ == '__main__':
    app = App()
