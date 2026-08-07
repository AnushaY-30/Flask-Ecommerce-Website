import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

products = [
    ("Dell Laptop", 55000, "laptop.jpg", "Dell Core i5 Laptop", "Laptop"),
    ("HP Laptop", 60000, "laptop.jpg", "HP Core i7 Laptop", "Laptop"),
    ("Lenovo Laptop", 52000, "laptop.jpg", "Lenovo Ryzen 5 Laptop", "Laptop"),
    ("Asus Laptop", 58000, "laptop.jpg", "Asus Gaming Laptop", "Laptop"),
    ("Acer Laptop", 50000, "laptop.jpg", "Acer Slim Laptop", "Laptop"),

    ("Logitech Mouse", 1200, "mouse.jpg", "Wireless Mouse", "Mouse"),
    ("Dell Mouse", 900, "mouse.jpg", "USB Optical Mouse", "Mouse"),
    ("HP Mouse", 1000, "mouse.jpg", "Wireless HP Mouse", "Mouse"),

    ("Mechanical Keyboard", 2500, "keyboard.jpg", "RGB Mechanical Keyboard", "Keyboard"),
    ("Gaming Keyboard", 3200, "keyboard.jpg", "Gaming RGB Keyboard", "Keyboard")
]

for product in products:
    cursor.execute("""
        SELECT * FROM products
        WHERE name = ?
    """, (product[0],))

    exists = cursor.fetchone()

    if not exists:
        cursor.execute("""
            INSERT INTO products
            (name, price, image, description, category)
            VALUES (?, ?, ?, ?, ?)
        """, product)

conn.commit()

print("Products Added Successfully! ✅")