from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import check_password_hash
from models import db, User
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/users")
def get_users():
    users = User.query.all()
    user_list = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]
    return jsonify(user_list)

@app.route("/register", methods=["GET", "POST"])
def register_user():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if not username or not email or not password:
        flash("Missing required fields", "danger")
        return render_template("register.html")

    if User.query.filter_by(email=email).first():
        flash("Email already registered", "danger")
        return render_template("register.html")

    if User.query.filter_by(username=username).first():
        flash("Username already taken", "danger")
        return render_template("register.html")

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    flash("Registration successful! Please log in.", "success")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        session["username"] = user.username
        flash("Logged in successfully!", "success")
        return redirect("/items")
    else:
        flash("Invalid email or password", "danger")
        return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You’ve been logged out.", "info")
    return redirect("/login")

@app.route("/about")
def about():
    return "This is a student-built backend for YU Marketplace."

@app.route("/items")
def get_items():
    if "username" not in session:
        flash("Please log in to view products.", "warning")
        return redirect("/login")

    category = request.args.get("category")
    search_query = request.args.get("search")
    sort_option = request.args.get("sort")

    conn = sqlite3.connect("marketplace.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    base_query = """SELECT id, product_name, price, category, image_url, seller, 
                           location, description, timestamp FROM products"""
    filters = []
    params = []

    if category:
        filters.append("LOWER(category) = ?")
        params.append(category.lower())

    if search_query:
        filters.append("(LOWER(product_name) LIKE ? OR LOWER(seller) LIKE ?)")
        search_term = f"%{search_query.lower()}%"
        params.extend([search_term, search_term])

    query = base_query
    if filters:
        query += " WHERE " + " AND ".join(filters)

    if sort_option == "newest":
        query += " ORDER BY timestamp DESC"
    elif sort_option == "price_asc":
        query += " ORDER BY price ASC"
    elif sort_option == "price_desc":
        query += " ORDER BY price DESC"
    elif sort_option == "category":
        query += " ORDER BY category ASC"

    cursor.execute(query, params)
    items = cursor.fetchall()
    conn.close()

    return render_template("items.html", items=items, selected_category=category)

@app.route("/item/<int:item_id>")
def view_item(item_id):
    if "username" not in session:
        flash("Please log in to view product details.", "warning")
        return redirect("/login")

    conn = sqlite3.connect("marketplace.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()

    if not item:
        flash("Product not found.", "danger")
        return redirect("/items")

    return render_template("item_detail.html", item=item)

@app.route("/add", methods=["GET", "POST"])
def add_product():
    if "username" not in session:
        flash("Please log in to upload products.", "warning")
        return redirect("/login")

    if request.method == "POST":
        name = request.form['product_name']
        price = request.form['price']
        category = request.form['category']
        image_url = request.form['image_url']
        location = request.form['location']
        description = request.form['description']
        seller = session["username"]
        timestamp = datetime.now().isoformat()

        if not name or not price:
            flash("Missing product name or price", "danger")
            return render_template("add.html")

        conn = sqlite3.connect("marketplace.db")
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO products 
               (product_name, price, category, image_url, seller, location, description, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, price, category, image_url, seller, location, description, timestamp)
        )
        conn.commit()
        conn.close()
        flash("Product uploaded successfully!", "success")
        return redirect("/items")

    return render_template("add.html")

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    conn = sqlite3.connect("marketplace.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":
        new_name = request.form['product_name']
        new_price = request.form['price']
        new_category = request.form['category']
        new_image_url = request.form['image_url']
        cursor.execute(
            "UPDATE products SET product_name = ?, price = ?, category = ?, image_url = ? WHERE id = ?",
            (new_name, new_price, new_category, new_image_url, item_id)
        )
        conn.commit()
        conn.close()
        flash("Product updated successfully!", "success")
        return redirect("/items")

    cursor.execute("SELECT product_name, price, category, image_url FROM products WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return render_template("edit.html", item=item, item_id=item_id)

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Product deleted successfully!", "info")
    return redirect("/items")

@app.route("/inbox")
def inbox():
    if "username" not in session:
        flash("Please log in to view your inbox.", "warning")
        return redirect("/login")

    conn = sqlite3.connect("marketplace.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT messages.sender, products.product_name, messages.content, messages.timestamp, messages.item_id
        FROM messages
        JOIN products ON messages.item_id = products.id
        WHERE messages.receiver = ?
        ORDER BY messages.item_id, messages.sender, messages.timestamp ASC
    """, (session["username"],))

    raw_messages = cursor.fetchall()
    conn.close()

    threads = {}
    for sender, item_name, content, timestamp, item_id in raw_messages:
        key = (item_id, sender, item_name)
        if key not in threads:
            threads[key] = []
        threads[key].append((content, timestamp))

    return render_template("inbox.html", threads=threads)

@app.route("/message/<int:item_id>", methods=["POST"])
def send_message(item_id):
    if "username" not in session:
        flash("Please log in to send messages.", "warning")
        return redirect("/login")

    content = request.form["content"]
    sender = session["username"]
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()

    cursor.execute("SELECT seller FROM products WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    if not result:
        flash("Product not found.", "danger")
        conn.close()
        return redirect("/items")

    receiver = result[0]

    cursor.execute("""
        INSERT INTO messages (sender, receiver, item_id, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (sender, receiver, item_id, content, timestamp))

    conn.commit()
    conn.close()

    flash("Message sent to seller!", "success")
    return redirect("/items")

if __name__ == "__main__":
    app.run(debug=True, port=5050)
