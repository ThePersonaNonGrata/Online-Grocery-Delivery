# -----------------------------------------------
# Online Grocery Delivery System - Demo Version
# Single-file functional prototype using Flask
# Based on: Proposal, System Requirements, Functional Specs, UI Spec, and Diagrams
#
# Updates added:
#  - Cart supports add/remove items
#  - Cart supports changing quantity per item
#  - Checkout collects customer info (name, email, phone) + address + card
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

# orders[order_id] = { user, customer_info, items:[{id,name,price,qty,subtotal}], total, status:int }
orders = {}
delivery_status = ["Confirmed", "Packed", "Out for Delivery", "Delivered"]

# -----------------------------
# Helpers
# -----------------------------
def get_product(pid: int):
    for p in products:
        if p["id"] == pid:
            return p
    return None

def ensure_cart():
    # session["cart"] is a dict: {product_id(str): qty(int)}
    if "cart" not in session or not isinstance(session.get("cart"), dict):
        session["cart"] = {}

def cart_items_and_total():
    """Returns (items, total)."""
    ensure_cart()
    items = []
    total = 0.0
    for pid_str, qty in session["cart"].items():
        try:
            pid = int(pid_str)
            qty = int(qty)
        except ValueError:
            continue
        if qty <= 0:
            continue
        p = get_product(pid)
        if not p:
            continue
        subtotal = round(p["price"] * qty, 2)
        items.append({
            "id": pid,
            "name": p["name"],
            "price": p["price"],
            "qty": qty,
            "subtotal": subtotal
        })
        total += subtotal
    return items, round(total, 2)

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
    .btn { background: #3498db; color: white; padding: 6px 12px; border-radius: 4px; display:inline-block; }
    .btn:hover { background: #2980b9; }
    .btn-danger { background: #c0392b; }
    .btn-danger:hover { background: #a93226; }
    .btn-secondary { background: #7f8c8d; }
    .btn-secondary:hover { background: #707b7c; }
    .card { background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .nav { margin-bottom: 20px; }
    input[type="number"], input[type="text"], input[type="email"], input[type="tel"] { padding: 8px; width: 320px; max-width: 100%; }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
    th, td { padding: 10px; border-bottom: 1px solid #eee; text-align: left; }
    th { background: #ecf0f1; }
    .msg { padding: 10px; background: #eafaf1; border: 1px solid #d5f5e3; border-radius: 6px; margin: 10px 0; }
    .err { padding: 10px; background: #fdecea; border: 1px solid #f5c6cb; border-radius: 6px; margin: 10px 0; }
  </style>
</head>
<body>
  <div class="nav">
    {% if session.get('user') %}
      Logged in as: {{session['user']}} |
      <a href="{{url_for('home')}}">Home</a> |
      <a href="{{url_for('view_cart')}}">Cart</a> |
      <a href="{{url_for('track')}}">Track Order</a> |
      <a href="{{url_for('logout')}}">Logout</a>
    {% else %}
      <a href="{{url_for('login')}}">Login</a> | <a href="{{url_for('signup')}}">Sign Up</a>
    {% endif %}
  </div>
  {% block content %}{% endblock %}
</body>
</html>
"""

home_html = """
{% extends "layout" %}
{% block content %}
<h1>Welcome to Online Grocery Delivery</h1>
<p>Select products and add them to your cart.</p>

{% if message %}
  <div class="{{ 'err' if error else 'msg' }}">{{message}}</div>
{% endif %}

{% for p in products %}
  <div class="card">
    <b>{{p.name}}</b><br>
    Price: ${{"%.2f"|format(p.price)}} | Stock: {{p.stock}}<br><br>
    {% if p.stock > 0 %}
      <a class="btn" href="{{url_for('add_to_cart', pid=p.id)}}">Add to Cart</a>
    {% else %}
      <span class="btn btn-secondary">Out of Stock</span>
    {% endif %}
  </div>
{% endfor %}

<a href="{{url_for('view_cart')}}" class="btn">View Cart</a>
{% endblock %}
"""

cart_html = """
{% extends "layout" %}
{% block content %}
<h2>Your Shopping Cart</h2>

{% if message %}
  <div class="{{ 'err' if error else 'msg' }}">{{message}}</div>
{% endif %}

{% if not items %}
  <p>Your cart is empty.</p>
  <a class="btn" href="{{url_for('home')}}">Back to Products</a>
{% else %}
  <form method="POST" action="{{url_for('update_cart')}}">
    <table>
      <thead>
        <tr>
          <th style="width:35%;">Item</th>
          <th style="width:15%;">Price</th>
          <th style="width:15%;">Qty</th>
          <th style="width:15%;">Subtotal</th>
          <th style="width:20%;">Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for item in items %}
        <tr>
          <td>{{item.name}}</td>
          <td>${{"%.2f"|format(item.price)}}</td>
          <td>
            <input type="number" name="qty_{{item.id}}" min="0" value="{{item.qty}}" />
          </td>
          <td>${{"%.2f"|format(item.subtotal)}}</td>
          <td>
            <a class="btn btn-danger" href="{{url_for('remove_from_cart', pid=item.id)}}">Remove</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <p style="margin-top:15px;"><b>Total:</b> ${{"%.2f"|format(total)}}</p>
    <button class="btn" type="submit">Update Quantities</button>
    <a href="{{url_for('checkout')}}" class="btn">Checkout</a>
    <a class="btn btn-secondary" href="{{url_for('home')}}">Continue Shopping</a>
  </form>
{% endif %}
{% endblock %}
"""

checkout_html = """
{% extends "layout" %}
{% block content %}
<h2>Checkout</h2>

{% if message %}
  <div class="{{ 'err' if error else 'msg' }}">{{message}}</div>
{% endif %}

{% if not items %}
  <p>Your cart is empty.</p>
  <a class="btn" href="{{url_for('home')}}">Back to Products</a>
{% else %}
  <div class="card">
    <b>Order Summary</b><br>
    {% for item in items %}
      {{item.name}} (x{{item.qty}}) - ${{"%.2f"|format(item.subtotal)}}<br>
    {% endfor %}
    <br><b>Total:</b> ${{"%.2f"|format(total)}}
  </div>

  <form method="POST">
    <h3>Customer Information</h3>
    Full Name:<br>
    <input type="text" name="full_name" required><br><br>

    Email:<br>
    <input type="email" name="email" required><br><br>

    Phone:<br>
    <input type="tel" name="phone" required><br><br>

    <h3>Delivery & Payment</h3>
    Delivery Address:<br>
    <input type="text" name="address" required><br><br>

    Card Number:<br>
    <input type="text" name="card" required><br><br>

    <button class="btn" type="submit">Confirm Payment</button>
    <a class="btn btn-secondary" href="{{url_for('view_cart')}}">Back to Cart</a>
  </form>
{% endif %}
{% endblock %}
"""

track_html = """
{% extends "layout" %}
{% block content %}
<h2>Track Order</h2>
<form method="POST">
  Order ID: <input type="text" name="oid" required>
  <button class="btn" type="submit">Track</button>
</form>

{% if status %}
  <div class="card">
    <p>Current Status: <b>{{status}}</b></p>
    {% if details %}
      <p><b>Customer:</b> {{details.customer_info.full_name}} ({{details.customer_info.email}})</p>
      <p><b>Total:</b> ${{"%.2f"|format(details.total)}}</p>
    {% endif %}
  </div>
{% elif message %}
  <div class="err">{{message}}</div>
{% endif %}
{% endblock %}
"""

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
    if "user" not in session:
        return redirect(url_for("login"))

    ensure_cart()
    p = get_product(pid)
    if not p:
        return render_template_string(home_html, products=products, message="Product not found.", error=True)

    if p["stock"] <= 0:
        return render_template_string(home_html, products=products, message="That item is out of stock.", error=True)

    pid_str = str(pid)
    session["cart"][pid_str] = int(session["cart"].get(pid_str, 0)) + 1
    p["stock"] -= 1
    session.modified = True
    return redirect(url_for("view_cart"))

@app.route("/remove/<int:pid>")
def remove_from_cart(pid):
    if "user" not in session:
        return redirect(url_for("login"))

    ensure_cart()
    pid_str = str(pid)
    if pid_str in session["cart"]:
        removed_qty = int(session["cart"].get(pid_str, 0))
        p = get_product(pid)
        if p:
            p["stock"] += max(removed_qty, 0)
        session["cart"].pop(pid_str, None)
        session.modified = True

    return redirect(url_for("view_cart"))

@app.route("/update_cart", methods=["POST"])
def update_cart():
    if "user" not in session:
        return redirect(url_for("login"))

    ensure_cart()

    message = "Cart updated."
    error = False

    cart_copy = dict(session["cart"])
    for pid_str, old_qty in cart_copy.items():
        try:
            pid = int(pid_str)
            old_qty = int(old_qty)
        except ValueError:
            continue

        new_qty_raw = request.form.get(f"qty_{pid}", str(old_qty))
        try:
            new_qty = int(new_qty_raw)
        except ValueError:
            new_qty = old_qty

        if new_qty < 0:
            new_qty = 0

        p = get_product(pid)
        if not p:
            continue

        diff = new_qty - old_qty

        if diff > 0:
            if p["stock"] >= diff:
                p["stock"] -= diff
                session["cart"][pid_str] = new_qty
            else:
                session["cart"][pid_str] = old_qty + p["stock"]
                p["stock"] = 0
                message = "Some quantities were reduced due to limited stock."
                error = True
        elif diff < 0:
            p["stock"] += abs(diff)
            if new_qty == 0:
                session["cart"].pop(pid_str, None)
            else:
                session["cart"][pid_str] = new_qty

    session.modified = True
    items, total = cart_items_and_total()
    return render_template_string(cart_html, items=items, total=total, message=message, error=error)

@app.route("/cart")
def view_cart():
    if "user" not in session:
        return redirect(url_for("login"))
    items, total = cart_items_and_total()
    return render_template_string(cart_html, items=items, total=total)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user" not in session:
        return redirect(url_for("login"))

    items, total = cart_items_and_total()
    message = ""
    error = False

    if request.method == "POST":
        ensure_cart()
        items, total = cart_items_and_total()
        if not items:
            message = "Your cart is empty."
            error = True
        else:
            customer_info = {
                "full_name": request.form.get("full_name", "").strip(),
                "email": request.form.get("email", "").strip(),
                "phone": request.form.get("phone", "").strip(),
                "address": request.form.get("address", "").strip(),
                "card": request.form.get("card", "").strip(),
            }

            if not customer_info["full_name"] or not customer_info["email"] or not customer_info["address"] or not customer_info["card"]:
                message = "Please complete all required fields."
                error = True
            else:
                oid = len(orders) + 1
                orders[oid] = {
                    "user": session["user"],
                    "customer_info": customer_info,
                    "items": items,
                    "total": total,
                    "status": 0,
                }
                session["cart"] = {}
                session.modified = True
                message = f"Payment Successful! Your Order ID: {oid}"

    return render_template_string(checkout_html, items=items, total=total, message=message, error=error)

@app.route("/track", methods=["GET", "POST"])
def track():
    if "user" not in session:
        return redirect(url_for("login"))

    status = None
    message = ""
    details = None

    if request.method == "POST":
        oid_raw = request.form.get("oid", "").strip()
        try:
            oid = int(oid_raw)
        except ValueError:
            oid = None

        if oid and oid in orders:
            order = orders[oid]
            if order["status"] < len(delivery_status) - 1:
                order["status"] += 1
            status = delivery_status[order["status"]]
            details = order
        else:
            message = "Order not found."

    return render_template_string(track_html, status=status, message=message, details=details)

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = users.get(email)
        if user and user["password"] == password:
            session["user"] = email
            session["cart"] = {}
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
app.jinja_loader = DictLoader({"layout": layout_html})

# Run server
if __name__ == "__main__":
    app.run(debug=True)
