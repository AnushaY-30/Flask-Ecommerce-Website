from flask import Flask, render_template, request, redirect, session
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
    category TEXT
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

    # Get products from database
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
            "stock": row[7],
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
        category=category
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

        return render_template("product.html", product=product)

    return "Product Not Found"

@app.route("/cart")
def cart_page():

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
    """)

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

    # Check if product already exists in cart
    cursor.execute(
        "SELECT * FROM cart WHERE product_id=?",
        (id,)
    )

    item = cursor.fetchone()

    if item:
        cursor.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE product_id=?",
            (id,)
        )
    else:
        cursor.execute(
            "INSERT INTO cart(product_id, quantity) VALUES (?, ?)",
            (id, 1)
        )

    conn.commit()

    return redirect("/cart")
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
            "category": row[5]
        })

    return render_template("admin.html", products=products)

@app.route("/add_product", methods=["POST"])
def add_product():

    name = request.form["name"]
    price = request.form["price"]
    category = request.form["category"]

    image = request.files["image"]
    filename = secure_filename(image.filename)
    image.save(os.path.join("static", "images", filename))

    description = request.form["description"]

    cursor.execute(
        """
        INSERT INTO products(name, price, image, description, category)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, price, filename, description, category)
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

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")

if __name__ == "__main__":
    app.run(debug=True)