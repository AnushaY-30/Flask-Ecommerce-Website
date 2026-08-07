from flask import Flask, render_template, request, redirect, session
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "ecommerce_secret_key"
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER,
    image TEXT,
    description TEXT,
    category TEXT,
    rating INTEGER DEFAULT 5,
    stock INTEGER DEFAULT 10
)
""")
conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity INTEGER
)
""")

conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    product_name TEXT,
    price INTEGER,
    quantity INTEGER,
    order_date TEXT
)
""")

conn.commit()

cursor.execute("SELECT COUNT(*) FROM products")
count = cursor.fetchone()[0]

if count == 0:
    cursor.execute("""
    INSERT INTO products(name, price, image, description, category)
    VALUES
    ('Wireless Mouse', 500, 'mouse.jpg', 'Smooth and wireless mouse.', 'Mouse'),
    ('Keyboard', 999, 'keyboard.jpg', 'Comfortable mechanical keyboard.', 'Keyboard'),
    ('Headphones', 1499, 'headphones.jpg', 'High quality sound with deep bass.', 'Headphones')
    """)

    conn.commit()
products = [
   {
    "id": 1,
    "name": "Wireless Mouse",
    "price": 500,
    "image": "mouse.jpg",
    "description": "Smooth and wireless mouse.",
    "quantity": 1,
    "category": "Mouse"
},
    {
    "id": 2,
    "name": "Keyboard",
    "price": 999,
    "image": "keyboard.jpg",
    "description": "Comfortable mechanical keyboard.",
    "quantity": 1,
    "category": "Keyboard"
},
   {
    "id": 3,
    "name": "Headphones",
    "price": 1499,
    "image": "headphones.jpg",
    "description": "High quality sound with deep bass.",
    "quantity": 1,
    "category": "Headphones"
}
]

@app.route("/")
def home():

    search = request.args.get("search", "").lower()
    category = request.args.get("category", "")

    # Get one product (temporary debug)
    cursor.execute("SELECT * FROM products LIMIT 1")
    print(cursor.fetchone())

    # Get all products
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "image": row[3],
            "description": row[4],
            "category": row[5],
            "rating": row[6],
            "stock": int(row[7]),
            "quantity": 1
        })

    # Search
    if search:
        filtered_products = []

        for product in products:
            if search in product["name"].lower():
                filtered_products.append(product)
    else:
        filtered_products = products

    # Category Filter
    if category:
        temp_products = []

        for product in filtered_products:
            if product["category"] == category:
                temp_products.append(product)

        filtered_products = temp_products

    return render_template(
        "home.html",
        products=filtered_products,
        search=search,
        category=category,
        user=session.get("user")
    )

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            session["user"] = user[2]
            print("Logged in user:", session["user"])
            return redirect("/")
        else:
            return render_template(
                "login.html",
                error="Invalid Email or Password!"
            )

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )

        conn.commit()

        print("User Registered Successfully!")
        cursor.execute("SELECT * FROM users")
        print(cursor.fetchall())
        return render_template(
            "login.html",
            success="Registration Successful! Please Login."
        )

    return render_template("register.html")

@app.route("/product/<int:id>")
def product(id):

    cursor.execute(
        "SELECT * FROM products WHERE id=?",
        (id,)
    )

    row = cursor.fetchone()

    if row:

        product = {
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "image": row[3],
            "description": row[4],
            "category": row[5],
            "quantity": 1
        }

        # Get Reviews
        cursor.execute("""
           SELECT user_email, rating, comment, review_date
            FROM reviews
            WHERE product_id=?
            ORDER BY id DESC
        """, (id,))

        reviews = cursor.fetchall()

        # Get Average Rating
        cursor.execute("""
            SELECT AVG(rating)
            FROM reviews
            WHERE product_id=?
        """, (id,))

        avg_rating = cursor.fetchone()[0]

        if avg_rating is None:
            avg_rating = 0

        return render_template(
            "product.html",
            product=product,
            reviews=reviews,
            avg_rating=round(avg_rating, 1)
        )

    return "Product Not Found"
@app.route("/cart")
def cart_page():
    if "user" not in session:
        return redirect("/login")

    cursor.execute("""
    SELECT products.id,
           products.name,
           products.price,
           products.image,
           products.description,
           cart.quantity
    FROM cart
    JOIN products
    ON cart.product_id = products.id
    WHERE cart.user_email = ?
""", (session["user"],))

    rows = cursor.fetchall()

    cart_items = []
    total = 0

    for row in rows:
        item = {
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "image": row[3],
            "description": row[4],
            "quantity": row[5]
        }

        total += row[2] * row[5]
        cart_items.append(item)

    return render_template(
        "cart.html",
        cart=cart_items,
        total=total
    )

@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):

    # User must be logged in
    if "user" not in session:
        return redirect("/login")

    # Get available stock
    cursor.execute(
        "SELECT stock FROM products WHERE id=?",
        (id,)
    )

    stock = cursor.fetchone()[0]

    # Check if product already exists in cart
    cursor.execute(
        "SELECT * FROM cart WHERE product_id=? AND user_email=?",
        (id, session["user"])
    )

    item = cursor.fetchone()
    current_quantity = 0

    if item:
        current_quantity = item[2]

    if current_quantity >= stock:
        return "Only limited stock available!"

    if item:
        cursor.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE product_id=? AND user_email=?",
            (id, session["user"])
        )
    else:
        cursor.execute(
            "INSERT INTO cart(product_id, quantity, user_email) VALUES (?, ?, ?)",
            (id, 1, session["user"])
        )

    conn.commit()

    return redirect("/cart")
@app.route("/wishlist/<int:id>")
def wishlist(id):

    if "user" not in session:
        return redirect("/login")

    cursor.execute(
        "SELECT * FROM wishlist WHERE user_email=? AND product_id=?",
        (session["user"], id)
    )

    item = cursor.fetchone()

    if not item:
        cursor.execute("""
            INSERT INTO wishlist(user_email, product_id)
            VALUES (?, ?)
        """, (session["user"], id))

        conn.commit()

    return redirect("/")
@app.route("/my_wishlist")
def my_wishlist():

    if "user" not in session:
        return redirect("/login")

    cursor.execute("""
        SELECT products.*
        FROM wishlist
        JOIN products
        ON wishlist.product_id = products.id
        WHERE wishlist.user_email = ?
    """, (session["user"],))

    rows = cursor.fetchall()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "image": row[3],
            "description": row[4],
            "category": row[5],
            "rating": row[6],
            "stock": row[7]
        })

    return render_template("wishlist.html", products=products)
@app.route("/remove_wishlist/<int:id>")
def remove_wishlist(id):

    if "user" not in session:
        return redirect("/login")

    cursor.execute("""
        DELETE FROM wishlist
        WHERE user_email=? AND product_id=?
    """, (session["user"], id))

    conn.commit()

    return redirect("/my_wishlist")
@app.route("/add_review/<int:id>", methods=["POST"])
def add_review(id):

    if "user" not in session:
        return redirect("/login")

    rating = request.form["rating"]
    comment = request.form["comment"]

    review_date = datetime.now().strftime("%d-%m-%Y %H:%M")

    cursor.execute("""
        INSERT INTO reviews
        (user_email, product_id, rating, comment, review_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session["user"],
        id,
        rating,
        comment,
        review_date
    ))

    conn.commit()

    return redirect(f"/product/{id}")
@app.route("/increase/<int:id>")
def increase(id):

    cursor.execute(
        "UPDATE cart SET quantity = quantity + 1 WHERE product_id=?",
        (id,)
    )

    conn.commit()

    return redirect("/cart")
@app.route("/decrease/<int:id>")
def decrease(id):

    cursor.execute(
        "SELECT quantity FROM cart WHERE product_id=?",
        (id,)
    )

    item = cursor.fetchone()

    if item:
        if item[0] > 1:
            cursor.execute(
                "UPDATE cart SET quantity = quantity - 1 WHERE product_id=?",
                (id,)
            )
        else:
            cursor.execute(
                "DELETE FROM cart WHERE product_id=?",
                (id,)
            )

        conn.commit()

    return redirect("/cart")

@app.route("/remove_from_cart/<int:id>")
def remove_from_cart(id):

    cursor.execute(
        "DELETE FROM cart WHERE product_id=?",
        (id,)
    )

    conn.commit()

    return redirect("/cart")

@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect("/login")

    if session["user"] != "admin@gmail.com":
        return "Access Denied"

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "image": row[3],
            "description": row[4],
            "category": row[5],
            "rating": row[6],
            "stock": row[7]
        })

    # Dashboard Statistics
    total_products = len(products)

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = cursor.fetchone()[0]

    # Recent Orders
    cursor.execute("""
        SELECT *
        FROM orders
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_orders = cursor.fetchall()

    return render_template(
        "admin.html",
        products=products,
        total_products=total_products,
        total_users=total_users,
        total_orders=total_orders,
        total_reviews=total_reviews,
        recent_orders=recent_orders
    )
@app.route("/add_product", methods=["POST"])
def add_product():

    name = request.form["name"]
    price = int(request.form["price"])
    category = request.form["category"]

    image = request.files["image"]
    filename = secure_filename(image.filename)
    image.save(os.path.join("static", "images", filename))

    description = request.form["description"]
    stock = int(request.form["stock"])

    cursor.execute(
        """
        INSERT INTO products(name, price, image, description, category, stock)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, price, filename, description, category, stock)
    )

    conn.commit()

    return redirect("/admin")

@app.route("/edit_product/<int:id>")
def edit_product(id):

    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    row = cursor.fetchone()

    product = {
    "id": row[0],
    "name": row[1],
    "price": row[2],
    "image": row[3],
    "description": row[4],
    "category": row[5],
    "stock": row[7]
}

    return render_template("edit_product.html", product=product)

    return "Product Not Found"
@app.route("/delete_product/<int:id>")
def delete_product(id):

    cursor.execute(
        "DELETE FROM products WHERE id=?",
        (id,)
    )

    conn.commit()

    return redirect("/admin")

@app.route("/update_product/<int:id>", methods=["POST"])
def update_product(id):

    name = request.form["name"]
    price = request.form["price"]
    category = request.form["category"]
    image = request.form["image"]
    description = request.form["description"]
    stock = request.form["stock"]

    cursor.execute("""
    UPDATE products
    SET name=?, price=?, category=?, image=?, description=?, stock=?
    WHERE id=?
""", (name, price, category, image, description, stock, id))

    conn.commit()

    return redirect("/admin")

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")

from datetime import datetime

@app.route("/checkout")
def checkout():

    if "user" not in session:
        return redirect("/login")

    cursor.execute("""
        SELECT products.name,
               products.price,
               cart.quantity
        FROM cart
        JOIN products
        ON cart.product_id = products.id
        WHERE cart.user_email = ?
    """, (session["user"],))

    items = cursor.fetchall()

    for item in items:
        cursor.execute("""
            INSERT INTO orders
            (user_email, product_name, price, quantity, order_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session["user"],
            item[0],
            item[1],
            item[2],
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ))
        
        cursor.execute("""
    UPDATE products
    SET stock = stock - ?
    WHERE name = ?
""", (
    item[2],   # quantity
    item[0]    # product name
))

    cursor.execute(
        "DELETE FROM cart WHERE user_email=?",
        (session["user"],)
    )

    conn.commit()

    return render_template("checkout.html")

@app.route("/orders")
def orders():

    if "user" not in session:
        return redirect("/login")

    cursor.execute("""
        SELECT product_name,
               price,
               quantity,
               order_date
        FROM orders
        WHERE user_email=?
        ORDER BY id DESC
    """, (session["user"],))

    rows = cursor.fetchall()

    orders = []

    for row in rows:
        orders.append({
            "name": row[0],
            "price": row[1],
            "quantity": row[2],
            "date": row[3]
        })

    return render_template(
        "orders.html",
        orders=orders
    )
if __name__ == "__main__":
    app.run(debug=True)