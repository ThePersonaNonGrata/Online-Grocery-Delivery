# -----------------------------------------------
# Online Grocery Delivery System - Demo Version
# Single-file functional prototype using Flask
# Based on: Proposal, System Requirements, Functional Specs, UI Spec, and Diagrams
# -----------------------------------------------

from flask import Flask, render_template_string, request, redirect, url_for, session
from jinja2 import DictLoader

app = Flask(__name__)
app.secret_key = "demo123"

# -----------------------------
# Mock Data (in-memory)
# -----------------------------
users = {"customer@example.com": {"password": "1234", "role": "customer"}}
products = [
    {"id": 1, "name": "Apples", "price": 2.99, "stock": 10},
    {"id": 2, "name": "Bread", "price": 1.99, "stock": 15},
    {"id": 3, "name": "Milk", "price": 3.49, "stock": 8},
]
orders = {}
delivery_status = ["Confirmed", "Packed", "Out for Delivery", "Delivered"]

# -----------------------------
# Templates (HTML)
# -----------------------------
layout_html = """
<!DOCTYPE html>
<html>
<head>
  <title>Online Grocery Delivery System</title>
  <style>
    body { font-family: Arial; margin: 40px; background: #f8f9fa; color: #333; }
    h1, h2 { color: #2c3e50; }
    a { text-decoration: none; color: #3498db; }
    .btn { background: #3498db; color: white; padding: 6px 12px; border-radius: 4px; }
    .btn:hover { background: #2980b9; }
    .card { background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .nav { margin-bottom: 20px; }
  </style>
</head>
<body>
  <div class="nav">
    {% if session.get('user') %}
      Logged in as: {{session['user']}} | <a href="{{url_for('logout')}}">Logout</a>
    {% else %}
      <a href="{{url_for('login')}}">Login</a> | <a href="{{url_for('signup')}}">Sign Up</a>
    {% endif %}
  </div>
  {% block content %}{% endblock %}
</body>
</html>
"""

# Home / Browse Products
home_html = """
{% extends "layout" %}
{% block content %}
<h1>Welcome to Online Grocery Delivery</h1>
<p>Select products and add them to your cart.</p>
{% for p in products %}
  <div class="card">
    <b>{{p.name}}</b><br>
    Price: ${{p.price}} | Stock: {{p.stock}}<br>
    <a class="btn" href="{{url_for('add_to_cart', pid=p.id)}}">Add to Cart</a>
  </div>
{% endfor %}
<a href="{{url_for('view_cart')}}" class="btn">View Cart</a>
{% endblock %}
"""

# Cart
cart_html = """
{% extends "layout" %}
{% block content %}
<h2>Your Shopping Cart</h2>
{% if not cart %}
  <p>Your cart is empty.</p>
{% else %}
  {% for item in cart %}
    <div class="card">
      {{item['name']}} - ${{item['price']}}
    </div>
  {% endfor %}
  <p><b>Total:</b> ${{total}}</p>
  <a href="{{url_for('checkout')}}" class="btn">Checkout</a>
{% endif %}
{% endblock %}
"""

# Checkout & Pay
checkout_html = """
{% extends "layout" %}
{% block content %}
<h2>Checkout</h2>
<form method="POST">
  Address: <input type="text" name="address" required><br><br>
  Card Number: <input type="text" name="card" required><br><br>
  <button class="btn" type="submit">Confirm Payment</button>
</form>
{% if message %}<p>{{message}}</p>{% endif %}
{% endblock %}
"""

# Track Order
track_html = """
{% extends "layout" %}
{% block content %}
<h2>Track Order</h2>
<form method="POST">
  Order ID: <input type="text" name="oid" required>
  <button class="btn" type="submit">Track</button>
</form>
{% if status %}
  <p>Current Status: <b>{{status}}</b></p>
{% elif message %}
  <p>{{message}}</p>
{% endif %}
{% endblock %}
"""

# Login / Signup
login_html = """
{% extends "layout" %}
{% block content %}
<h2>Login</h2>
<form method="POST">
  Email: <input type="text" name="email" required><br><br>
  Password: <input type="password" name="password" required><br><br>
  <button class="btn" type="submit">Login</button>
</form>
<p>{{message}}</p>
{% endblock %}
"""

signup_html = """
{% extends "layout" %}
{% block content %}
<h2>Create an Account</h2>
<form method="POST">
  Email: <input type="text" name="email" required><br><br>
  Password: <input type="password" name="password" required><br><br>
  <button class="btn" type="submit">Sign Up</button>
</form>
<p>{{message}}</p>
{% endblock %}
"""

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(home_html, products=products)

@app.route("/add/<int:pid>")
def add_to_cart(pid):
    if "cart" not in session:
        session["cart"] = []
    for p in products:
        if p["id"] == pid and p["stock"] > 0:
            session["cart"].append(p)
            p["stock"] -= 1
    session.modified = True
    return redirect(url_for("view_cart"))

@app.route("/cart")
def view_cart():
    cart = session.get("cart", [])
    total = sum([c["price"] for c in cart])
    return render_template_string(cart_html, cart=cart, total=round(total, 2))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    message = ""
    if request.method == "POST":
        if not session.get("cart"):
            message = "Your cart is empty."
        else:
            oid = len(orders) + 1
            orders[oid] = {
                "user": session["user"],
                "items": session["cart"],
                "status": 0,
            }
            session["cart"] = []
            message = f"Payment Successful! Your Order ID: {oid}"
    return render_template_string(checkout_html, message=message)

@app.route("/track", methods=["GET", "POST"])
def track():
    status = None
    message = ""
    if request.method == "POST":
        oid = int(request.form["oid"])
        if oid in orders:
            order = orders[oid]
            step = order["status"]
            if step < len(delivery_status) - 1:
                order["status"] += 1
            status = delivery_status[order["status"]]
        else:
            message = "Order not found."
    return render_template_string(track_html, status=status, message=message)

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = users.get(email)
        if user and user["password"] == password:
            session["user"] = email
            session["cart"] = []
            return redirect(url_for("home"))
        else:
            message = "Invalid credentials."
    return render_template_string(login_html, message=message)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email in users:
            message = "User already exists."
        else:
            users[email] = {"password": password, "role": "customer"}
            message = "Account created successfully. You can now log in."
    return render_template_string(signup_html, message=message)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Template registration
from jinja2 import DictLoader
app.jinja_loader = DictLoader({"layout": layout_html})

# Run server
if __name__ == "__main__":
    app.run(debug=True)
