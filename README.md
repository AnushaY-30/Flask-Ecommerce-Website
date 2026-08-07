# 🛍️ Flask E-Commerce Website

A full-stack E-Commerce web application built using Python Flask, HTML, CSS, and SQLite. The application provides a complete online shopping experience with user authentication, product management, cart, wishlist, checkout, orders, reviews, and an admin dashboard.

## 🚀 Live Website

https://flask-ecommerce-website-1n5r.onrender.com

## 📂 GitHub Repository

https://github.com/AnushaY-30/Flask-Ecommerce-Website

## ✨ Features

### 👤 User Features

- User Registration
- User Login and Logout
- Product Browsing
- Product Search
- Category Filtering
- Product Details
- Add to Cart
- Increase / Decrease Cart Quantity
- Remove Products from Cart
- Buy Now
- Checkout
- Order History
- Wishlist
- Product Reviews and Ratings

### 👨‍💼 Admin Features

- Admin Login
- Admin Dashboard
- Add Products
- Edit Products
- Delete Products
- Product Image Upload
- Stock Management
- Total Products Statistics
- Total Users Statistics
- Total Orders Statistics
- Total Reviews Statistics
- Recent Orders

## 🛠️ Technologies Used

- Python
- Flask
- HTML5
- CSS3
- SQLite
- Jinja2
- Git
- GitHub
- Render

## 🗄️ Database

The application uses SQLite to store:

- Users
- Products
- Cart Items
- Orders
- Reviews
- Wishlist Data

## 📁 Project Structure

```text
Flask-Ecommerce-Website/
│
├── app.py
├── database.db
├── add_products.py
├── requirements.txt
├── README.md
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── images/
│
└── templates/
    ├── home.html
    ├── login.html
    ├── register.html
    ├── product.html
    ├── cart.html
    ├── orders.html
    ├── wishlist.html
    ├── admin.html
    └── ...