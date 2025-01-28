import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
from PIL import Image, ImageTk

#encoding password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# starting a database
def init_db():
    conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
    cursor = conn.cursor()

    # create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PRODUCTS (
        product_id INTEGER PRIMARY KEY,
        product_category TEXT NOT NULL,
        product_name TEXT NOT NULL,
        product_price REAL NOT NULL,
        product_stock INTEGER NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS USERS (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ADMIN (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SALES (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_profit REAL NOT NULL,
        FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id)
    )
    """)
    conn.commit()

    # add custom admin
    admins = [
        ("admin1", hash_password("221203")),
        ("admin2", hash_password("130404"))
    ]
    cursor.executemany("INSERT OR IGNORE INTO ADMIN (username, password) VALUES (?, ?)", admins)
    conn.commit()
    conn.close()

# adding products
def insert_default_products():
    conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
    cursor = conn.cursor()
    products = [
        (10001, "Fashion", "Pants", 300, 25),
        (10002, "Fashion", "Pyjamas", 250, 10),
        (10003, "Fashion", "Top", 550, 5),
        (20001, "Accessories", "Hats", 400, 10),
        (20002, "Accessories", "Bags", 450, 7),
        (30001, "Souvenirs", "Cup", 100, 10),
        (30002, "Souvenirs", "Candles", 100, 20),
        (30003, "Souvenirs", "Decoration", 200, 55),
        (40001, "Food", "Organic Olive Oil", 500, 5),
        (40002, "Food", "Organic Jam", 150, 50),
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO PRODUCTS (product_id, product_category, product_name, product_price, product_stock)
    VALUES (?, ?, ?, ?, ?)
    """, products)
    conn.commit()
    conn.close()

# shopping cart
global cart
cart = []

# registering the user
def register_user():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Error!", "Please fill all the places.")
        return

    hashed_password = hash_password(password)

    try:
        conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO USERS (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        messagebox.showinfo("Succeed!", "Signed up successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error!", "This username has already taken!")

# Log in process
def login_user():
    username = entry_login_username.get()
    password = entry_login_password.get()

    hashed_password = hash_password(password)

    conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Succeed!", "Logged in successfully!")
        root.withdraw()  # hide the main page
        open_customer_app(username)
    else:
        messagebox.showerror("Error!", "Incorrect username or password!")

# deleting and updating items from the shopping cart
def remove_from_cart(item, cart_window):
    if item in cart:
        cart.remove(item)
        messagebox.showinfo("Shopping cart", f"{item[0]} item has deleted from the shopping cart!")
        # updating the shopping cart page
        for widget in cart_window.winfo_children():
            widget.destroy()
        view_cart(cart_window)


# view shopping cart 
def view_cart(existing_window=None):
    if existing_window:
        cart_window = existing_window
    else:
        cart_window = tk.Toplevel()
        cart_window.title("Your Shopping Cart")
        cart_window.geometry("800x700")
        cart_window.configure(bg="#E6E6FA")  # makes the background color levander.

    if not cart:
        tk.Label(cart_window, text="Empty Shopping Cart!", font=("Arial", 14),  bg="#E6E6FA").pack(pady=20)
        return

    canvas = tk.Canvas(cart_window, bg="#E6E6FA") # Canvas background
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(cart_window, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    scrollable_frame = tk.Frame(canvas,  bg="#E6E6FA") # Scrollable Frame background
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    total_price = 0

    for idx, item in enumerate(cart):
        product_name, image_path, product_price, size = item
        total_price += product_price

        try:
            img = ImageTk.PhotoImage(Image.open(image_path).resize((100, 100)))
            img_label = tk.Label(scrollable_frame, image=img, bg="#E6E6FA")
            img_label.image = img
            img_label.grid(row=idx, column=0, padx=10, pady=10)
        except FileNotFoundError:
            tk.Label(scrollable_frame, text="Image not found", font=("Arial", 12), bg="#E6E6FA").grid(row=idx, column=0, padx=10, pady=10)

        tk.Label(scrollable_frame, text=product_name, font=("Arial", 12), bg="#E6E6FA").grid(row=idx, column=1, padx=10, pady=10)
        tk.Label(scrollable_frame, text=f"{product_price}₺", font=("Arial", 12), bg="#E6E6FA").grid(row=idx, column=2, padx=10, pady=10)
        tk.Label(scrollable_frame, text=f"Beden: {size}", font=("Arial", 12), bg="#E6E6FA").grid(row=idx, column=3, padx=10, pady=10)

        # remove button
        remove_button = tk.Button(scrollable_frame, text="Remove From Cart", command=lambda i=item: remove_from_cart(i, cart_window))
        remove_button.grid(row=idx, column=4, padx=10, pady=10)

    tk.Label(cart_window, text=f"Total Price: {total_price}₺", font=("Arial", 14)).pack(pady=10)
    tk.Button(cart_window, text="Buy Now", command=lambda: open_payment_window(total_price)).pack(pady=20)


# Payment window
def open_payment_window(total_price):
    payment_window = tk.Toplevel()
    payment_window.title("Payment Information")
    payment_window.geometry("600x600")
    payment_window.configure(bg="#9FB9BF")


    tk.Label(payment_window, text=f"Total price: {total_price}₺", font=("Arial", 14)).pack(pady=10)

    # Name and surname
    tk.Label(payment_window, text="Name Surname:").pack(pady=5)
    entry_name = tk.Entry(payment_window)
    entry_name.pack(pady=5)

    # e-mail
    tk.Label(payment_window, text="e-mail:").pack(pady=5)
    entry_email = tk.Entry(payment_window)
    entry_email.pack(pady=5)

    # Phone Number
    tk.Label(payment_window, text="Phone Number:").pack(pady=5)
    entry_phone = tk.Entry(payment_window)
    entry_phone.pack(pady=5)

    tk.Label(payment_window, text="Card Number:").pack(pady=5)
    entry_card_number = tk.Entry(payment_window)
    entry_card_number.pack(pady=5)

    tk.Label(payment_window, text="Expiration Date (MM/YY):").pack(pady=5)
    entry_expiry_date = tk.Entry(payment_window)
    entry_expiry_date.pack(pady=5)

    tk.Label(payment_window, text="CVV:").pack(pady=5)
    entry_cvv = tk.Entry(payment_window, show="*")
    entry_cvv.pack(pady=5)

    # Address info
    tk.Label(payment_window, text="Delivery Address:").pack(pady=5)
    entry_address = tk.Entry(payment_window, width=50)  # wide entry space for addreess info
    entry_address.pack(pady=5)

    def process_payment():
        name=entry_name.get()
        email = entry_email.get()
        phone = entry_phone.get()
        card_number = entry_card_number.get()
        expiry_date = entry_expiry_date.get()
        cvv = entry_cvv.get()
        address = entry_address.get()

        #check info
        if not all([name, email, phone, address, card_number, expiry_date, cvv]):
            messagebox.showwarning("Error!", "Please fill all necessery informations!")
            return

        try:
            update_stock()  # update stock call
            messagebox.showinfo("Succeed", f"Payment succeed! Your order will be delivered to:\n\nName and Surname: {name}\n\nAddress: {address}")
            cart.clear()  # clear cart
            payment_window.destroy()  # close payment window
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong: {e}")

    tk.Button(payment_window, text="Complete Payment", command=process_payment).pack(pady=20)


# Update stock and payment record
def update_stock():
    conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
    cursor = conn.cursor()

    for item in cart:
        product_name = item[0]  # Item name
        quantity = 1  # Each purchase is considered 1 piece (can be changed upon request)

        # get current stock and product price
        cursor.execute("SELECT product_stock, product_price, product_id FROM PRODUCTS WHERE product_name = ?", (product_name,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", f"{product_name} Couldn't found in current database")
            continue

        current_stock, product_price, product_id = result

        # Calculate the new stock quantity
        new_stock = current_stock - quantity

        if new_stock < 0:
            messagebox.showwarning("Error", f"{product_name} Not enough stock!")
            continue

        # update stock
        cursor.execute("UPDATE PRODUCTS SET product_stock = ? WHERE product_name = ?", (new_stock, product_name))

        # add sales table
        total_profit = product_price * quantity
        cursor.execute("""
            INSERT INTO SALES (product_id, quantity, total_profit)
            VALUES (?, ?, ?)
        """, (product_id, quantity, total_profit))

    conn.commit()
    conn.close()
    messagebox.showinfo("Succeed", "Stocks updated and sales recorded!")



def open_product_details(product_name, category):
    details_window = tk.Toplevel()
    details_window.title(f"Details of {product_name}")
    details_window.geometry("1000x800")  # wider window size
    details_window.configure(bg="#AEC8CE")  # background color

    # image frame
    img_frame = tk.Frame(details_window,bg="#AEC8CE")
    img_frame.pack(pady=20)

    # get price from databese
    conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
    cursor = conn.cursor()
    cursor.execute("SELECT product_price FROM PRODUCTS WHERE product_name = ?", (product_name,))
    product_price = cursor.fetchone()[0]
    conn.close()

    # paths of images
    image_files = {
        "Pants": ["images/pants1.png", "images/pants2.png", "images/pants3.png", "images/pants4.png",
                  "images/pants5.png", "images/pants6.png", "images/pants7.png", "images/pants8.png"],
        "Pyjamas": ["images/pyjamas1.png", "images/pyjamas2.png", "images/pyjamas3.png", "images/pyjamas4.png",
                    "images/pyjamas5.png", "images/pyjamas6.png", "images/pyjamas7.png", "images/pyjamas8.png"],
        "Top": ["images/top1.png", "images/top2.png", "images/top3.png", "images/top4.png",
                "images/top5.png", "images/top6.png", "images/top7.png", "images/top8.png"],
        "Hats": ["images/hats1.png", "images/hats2.png", "images/hats3.png", "images/hats4.png",
                 "images/hats5.png", "images/hats6.png", "images/hats7.png", "images/hats8.png"],
        "Bags": ["images/bags1.png", "images/bags2.png", "images/bags3.png", "images/bags4.png",
                 "images/bags5.png", "images/bags6.png", "images/bags7.png", "images/bags8.png"],
        "Cup": ["images/cup1.png", "images/cup2.png", "images/cup3.png", "images/cup4.png",
                "images/cup5.png", "images/cup6.png", "images/cup7.png","images/cup8.png"],
        "Candles": ["images/candles1.png", "images/candles2.png", "images/candles3.png", "images/candles4.png",
                    "images/candles5.png", "images/candles6.png", "images/candles7.png", "images/candles8.png"],
        "Decoration": ["images/decoration1.png", "images/decoration2.png", "images/decoration3.png", "images/decoration4.png",
                       "images/decoration5.png", "images/decoration6.png", "images/decoration7.png", "images/decoration8.png"],
        "Organic Olive Oil": ["images/oliveoil1.png", "images/oliveoil2.png", "images/oliveoil3.png", "images/oliveoil4.png"],
        "Organic Jam": ["images/jam1.png", "images/jam2.png", "images/jam3.png", "images/jam4.png"]

    }

    images = []
    if product_name in image_files:
        for i, file in enumerate(image_files[product_name]):
            try:
                # upload image and resize
                img = ImageTk.PhotoImage(Image.open(file).resize((100, 100)))

                # put image in grid
                row, col = divmod(i, 4)  # 4 images each row
                img_label = tk.Label(img_frame, image=img)
                img_label.grid(row=row * 4, column=col, padx=10, pady=10)

                # price info under the image
                price_label = tk.Label(img_frame, text=f"Price: {product_price}₺", font=("Arial", 10))
                price_label.grid(row=row * 4 + 1, column=col, padx=10, pady=5)

                # Size selection below the image (only for Fashion category)
                if category == "Fashion":
                    size_var = tk.StringVar(value="M")
                    size_options = ["XS", "S", "M", "L", "XL", "XXL"]
                    size_menu = ttk.OptionMenu(img_frame, size_var, *size_options)
                    size_menu.grid(row=row * 4 + 2, column=col, padx=10, pady=5)

                    # put buy now button under the image
                    buy_button = tk.Button(
                        img_frame,
                        text="Buy Now",
                        command=lambda f=file, s=size_var: add_to_cart(product_name, f, product_price, s.get())
                    )
                    buy_button.grid(row=row * 4 + 3, column=col, padx=10, pady=5)
                else:
                    # price and button (other than fashion)
                    buy_button = tk.Button(
                        img_frame,
                        text="Buy Now",
                        command=lambda f=file: add_to_cart(product_name, f, product_price, None)
                    )
                    buy_button.grid(row=row * 4 + 2, column=col, padx=10, pady=5)

                # hide image references
                images.append(img)

            except FileNotFoundError:
                tk.Label(img_frame, text=f"Image {i + 1} not found").grid(row=row * 4, column=col, padx=10, pady=10)

    # hold image references
    details_window.image_refs = images



# add items to shopping cart
def add_to_cart(product_name, file, price, size=None):
    size = size if size else "No Size"  # If size is None it defaults to 'No Size'
    cart.append((product_name, file, price, size))
    messagebox.showinfo("Shopping Cart", f"{product_name} item ({size}) added to shopping cart")


# buy
def checkout():
    if not cart:
        messagebox.showwarning("Shopping Cart Is Empty!", "Add items to your shopping cart!")
        return

    total_price = sum(item[2] for item in cart)

    try:
        update_stock()  # update sales and stocks
        messagebox.showinfo("Buy Now", f"Payment Successfull! Total Price: {total_price:.2f}₺")
        cart.clear()  # clear shopping cart
    except Exception as e:
        messagebox.showerror("Error", f"Something Went Wrong!: {e}")

# User interface
def open_customer_app(username):
    customer_window = tk.Toplevel()
    customer_window.title(f"Welcome {username}!")
    customer_window.geometry("900x700")
    customer_window.configure(bg="#AEC8CE")  # background color 

    # defining style
    style = ttk.Style()
    style.configure("Treeview", background="#AEC8CE", fieldbackground="#AEC8CE", foreground="black")
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#4682B4", foreground="black")

    columns = ("Product ID", "Category", "Name", "Price", "Stock")
    customer_tree = ttk.Treeview(customer_window, columns=columns, show="headings")
    for col in columns:
        customer_tree.heading(col, text=col)
        customer_tree.column(col, width=100)

    customer_tree.pack(fill="both", expand=True)

    def refresh_customer_products():
        customer_tree.delete(*customer_tree.get_children())
        conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PRODUCTS")
        for product in cursor.fetchall():
            customer_tree.insert("", "end", values=product)
        conn.close()

    # upload products first
    refresh_customer_products()


    # connect event for row selection
    def on_item_select(event):
        selected_item = customer_tree.selection()
        if selected_item:
            product_name = customer_tree.item(selected_item, 'values')[2]
            product_category = customer_tree.item(selected_item, 'values')[1]
            open_product_details(product_name, product_category)

    customer_tree.bind("<Double-1>", on_item_select)

    # button frame
    button_frame = tk.Frame(customer_window, bg="#AEC8CE")
    button_frame.pack(pady=10)

    # view shopping cart button
    tk.Button(
        button_frame, text="View Shopping Cart", bg="#DDADAD", fg="black",
        font=("Arial", 10, "bold"), command=view_cart
    ).pack(pady=5, padx=10, side=tk.TOP, fill="x")

    # refresh products button
    tk.Button(
        button_frame, text="Refresh Items", bg="#D6C7C7", fg="black",
        font=("Arial", 10, "bold"), command=refresh_customer_products
    ).pack(pady=5, padx=10, side=tk.TOP, fill="x")

    # Log out button
    tk.Button(
        button_frame, text="Log out", bg="#B88C8C", fg="black",
        font=("Arial", 10, "bold"), command=customer_window.destroy
    ).pack(pady=5, padx=10, side=tk.TOP, fill="x")



# admin entry
def admin_login():
    admin_username = entry_admin_username.get()
    admin_password = entry_admin_password.get()

    hashed_password = hash_password(admin_password)

    conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ADMIN WHERE username = ? AND password = ?", (admin_username, hashed_password))
    admin = cursor.fetchone()
    conn.close()

    if admin:
        messagebox.showinfo("Succeed", "Admin logged in successfully!")
        root.withdraw()  # hide main window
        open_admin_app()  # open admin window
    else:
        messagebox.showerror("Error", "Incorrect admin name or password!")


def open_admin_app():
    admin_window = tk.Toplevel()
    admin_window.title("Admin Panel")
    admin_window.geometry("900x800")
    admin_window.configure(bg="#D6C7C7")

    columns = ("Product ID", "Category", "Name", "Price", "Stock")
    admin_tree = ttk.Treeview(admin_window, columns=columns, show="headings")
    for col in columns:
        admin_tree.heading(col, text=col)
        admin_tree.column(col, width=100)

    admin_tree.pack(fill="both", expand=True)

    # refresh product list
    def refresh_products():
        admin_tree.delete(*admin_tree.get_children())
        conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PRODUCTS")
        for product in cursor.fetchall():
            admin_tree.insert("", "end", values=product)
        conn.close()

    refresh_products()

    # log out button
    tk.Button(admin_window, text="Log out", command=lambda: (admin_window.destroy(), root.deiconify())).pack(pady=10)

    # calculate and show total revenue
    def show_total_revenue():
        conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total_profit) FROM SALES")
        total_revenue = cursor.fetchone()[0]
        conn.close()

        if total_revenue is None:
            total_revenue = 0.0  # if no sales recorded, show 0

        messagebox.showinfo("Total Revenue", f"Total revenue of saled products: {total_revenue:.2f}₺")

    # show sales report
    def show_sales_report():
        sales_window = tk.Toplevel(admin_window)
        sales_window.title("Sales Report")
        sales_window.geometry("800x600")
        sales_window.configure(bg="#D6C7C7")

        sales_columns = ("Sale ID", "Product ID", "Quantity", "Total Profit")
        sales_tree = ttk.Treeview(sales_window, columns=sales_columns, show="headings")
        for col in sales_columns:
            sales_tree.heading(col, text=col)
            sales_tree.column(col, width=100)

        sales_tree.pack(fill="both", expand=True)

        conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SALES")
        for sale in cursor.fetchall():
            sales_tree.insert("", "end", values=sale)
        conn.close()
            # show total revenue button
    tk.Button(admin_window, text="Show total revenue", command=show_total_revenue).pack(pady=10)

    # show sales report buton 
    tk.Button(admin_window, text="View Sales Report", command=show_sales_report).pack(pady=10)
    
    # Open stock and price update fields when product is selected
    def on_item_select(event):
        selected_item = admin_tree.selection()
        if selected_item:
            product_id = admin_tree.item(selected_item, 'values')[0]
            product_name = admin_tree.item(selected_item, 'values')[2]
            product_price = admin_tree.item(selected_item, 'values')[3]
            product_stock = admin_tree.item(selected_item, 'values')[4]

            # update product window
            update_window = tk.Toplevel(admin_window)
            update_window.title(f"Update Product: {product_name}")
            update_window.geometry("500x400")

            tk.Label(update_window, text=f"Product: {product_name}", font=("Arial", 12)).pack(pady=5)

            tk.Label(update_window, text="New Price:").pack(pady=5)
            new_price_entry = tk.Entry(update_window)
            new_price_entry.insert(0, product_price)
            new_price_entry.pack(pady=5)

            tk.Label(update_window, text="New Stock:").pack(pady=5)
            new_stock_entry = tk.Entry(update_window)
            new_stock_entry.insert(0, product_stock)
            new_stock_entry.pack(pady=5)

            def update_product():
                new_price = new_price_entry.get()
                new_stock = new_stock_entry.get()

                try:
                    
                    new_price = float(new_price)  
                    new_stock = int(new_stock)  
                except ValueError:
                    # show error if invalid operation occurs
                    messagebox.showerror("Error", "Please enter a valid number")
                    return

                try:
                    conn = sqlite3.connect('E-Commerce_Inventory_Management_System.db')
                    cursor = conn.cursor()
                    cursor.execute("""
                    UPDATE PRODUCTS
                    SET product_price = ?, product_stock = ?
                    WHERE product_id = ?
                    """, (new_price, new_stock, product_id))
                    conn.commit()
                    conn.close()

                    messagebox.showinfo("Succeed", f"{product_name} product updated!")
                    update_window.destroy()
                    refresh_products()  # refresh updated products
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Database Error: {e}")

            tk.Button(update_window, text="Update", command=update_product).pack(pady=10)

    admin_tree.bind("<Double-1>", on_item_select)

    refresh_products()




# main page
def main():
    global root
    root = tk.Tk()
    root.title("E-Commerce Inventory Management System")
    root.geometry("600x700")
    root.configure(bg="#AEC8CE")  # background color

    # Bilgi Çerçevesi (Info Frame)
    info_frame = tk.Frame(root, relief="groove", bd=1, padx=10, pady=10, bg="#854442")
    info_frame.pack(pady=10, fill="x", padx=200)

    info_text = """Hello there! 👋
Welcome to our little shop! 🛒
Looking to reflect your style, make your loved ones happy, try new flavors 
or add a touch of color to your living space? You're in the right place!😊

Discover your favorite products, add them to your cart, 
and enjoy the joy of shopping! 💖

Let's get started! You can log in or create a new account below.
Happy shopping! 🎉"""

    tk.Label(info_frame, text=info_text, font=("Arial", 10, "italic"), justify="center", bg="#854442", wraplength=450).pack()

    # user register area
    register_frame = tk.Frame(root, bg="#DDADAD", relief="raised", bd=1, padx=10, pady=10)
    register_frame.pack(pady=10, fill="x", padx=500)

    tk.Label(register_frame, text="Username", bg="#DDADAD").pack()
    global entry_username
    entry_username = tk.Entry(register_frame)
    entry_username.pack()

    tk.Label(register_frame, text="Password", bg="#DDADAD").pack()
    global entry_password
    entry_password = tk.Entry(register_frame, show="*")
    entry_password.pack()

    tk.Button(register_frame, text="Sign Up", command=register_user).pack(pady=5)

    # user log in area
    login_frame = tk.Frame(root, bg="#D6C7C7", relief="raised", bd=1, padx=10, pady=10)
    login_frame.pack(pady=10, fill="x", padx=500)

    tk.Label(login_frame, text="Username(log in)", bg="#D6C7C7").pack()
    global entry_login_username
    entry_login_username = tk.Entry(login_frame)
    entry_login_username.pack()

    tk.Label(login_frame, text="Password(log in)", bg="#D6C7C7").pack()
    global entry_login_password
    entry_login_password = tk.Entry(login_frame, show="*")
    entry_login_password.pack()

    tk.Button(login_frame, text="Log In", command=login_user).pack(pady=5)

    # Admin log in page
    admin_frame = tk.Frame(root, bg="#B88C8C", relief="raised", bd=1, padx=10, pady=10)
    admin_frame.pack(pady=10, fill="x", padx=500)

    tk.Label(admin_frame, text="Admin Username", bg="#B88C8C").pack()
    global entry_admin_username
    entry_admin_username = tk.Entry(admin_frame)
    entry_admin_username.pack()

    tk.Label(admin_frame, text="Admin Password", bg="#B88C8C").pack()
    global entry_admin_password
    entry_admin_password = tk.Entry(admin_frame, show="*")
    entry_admin_password.pack()

    tk.Button(admin_frame, text="Admin Log In", command=admin_login).pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    init_db()
    insert_default_products()
    main()
