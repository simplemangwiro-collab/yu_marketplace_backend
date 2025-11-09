from flask import Flask, render_template, request, redirect, session, flash, jsonify, url_for
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Item
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Image upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

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

    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    items = cursor.fetchall()

    count_query = "SELECT COUNT(*) FROM products"
    if filters:
        count_query += " WHERE " + " AND ".join(filters)
    cursor.execute(count_query, params[:-2])  # exclude LIMIT/OFFSET
    total_items = cursor.fetchone()[0]
    conn.close()

    total_pages = (total_items + per_page - 1) // per_page

    return render_template("items.html", items=items, selected_category=category,
                           current_page=page, total_pages=total_pages)

@app.route("/item/<int:item_id>")
def view_item(item_id):
    if "username" not in session:
        flash("Please log in to view product details.", "warning")
        return redirect("/login")

    conn = sqlite3.connect("marketplace.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch the item
    cursor.execute("SELECT * FROM products WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        flash("Product not found.", "danger")
        return redirect("/items")

    # Fetch messages where current user is sender or receiver
    cursor.execute("""
        SELECT * FROM messages
        WHERE item_id = ?
        AND (sender = ? OR receiver = ?)
        ORDER BY timestamp ASC
    """, (item_id, session['username'], session['username']))
    messages = cursor.fetchall()

    conn.close()

    return render_template("item_detail.html", item=item, messages=messages)


@app.route("/add", methods=["GET", "POST"])
def add_product():
    if "username" not in session:
        flash("Please log in to upload products.", "warning")
        return redirect("/login")

    if request.method == "POST":
        name = request.form['product_name']
        price = request.form['price']
        category = request.form['category']
        location = request.form['location']
        description = request.form['description']
        seller = session["username"]
        timestamp = datetime.now().isoformat()

        file = request.files.get('image')
        image_url = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_url = url_for('static', filename='uploads/' + filename)

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

    # Get all messages where user is sender or receiver
    cursor.execute("""
        SELECT sender, receiver, products.product_name, content, timestamp, item_id
        FROM messages
        JOIN products ON messages.item_id = products.id
        WHERE sender = ? OR receiver = ?
        ORDER BY item_id, timestamp ASC
    """, (session["username"], session["username"]))
    raw_messages = cursor.fetchall()

    threads = {}
    unread_counts = {}

    for sender, receiver, item_name, content, timestamp, item_id in raw_messages:
        # Skip broken or orphaned rows
        if not item_id or not item_name or not sender or not receiver:
            continue

        other = receiver if sender == session["username"] else sender
        key = (item_id, other, item_name)

        if key not in threads:
            threads[key] = []
            unread_counts[key] = 0

        threads[key].append((sender, content, timestamp))

        try:
            if receiver == session["username"]:
                cursor.execute("""
                    SELECT COUNT(*) FROM messages
                    WHERE item_id = ? AND sender = ? AND receiver = ? AND read = 0
                """, (item_id, other, session["username"]))
                unread_counts[key] = cursor.fetchone()[0]
        except Exception as e:
            print("Unread count error:", e)
            unread_counts[key] = 0

    # Mark all received messages as read
    cursor.execute("""
        UPDATE messages SET read = 1
        WHERE receiver = ? AND read = 0
    """, (session["username"],))
    conn.commit()
    conn.close()

    return render_template("inbox.html", threads=threads, unread_counts=unread_counts)


@app.route("/dashboard")
def seller_dashboard():
    if "username" not in session:
        flash("Please log in to view your dashboard.", "warning")
        return redirect("/login")

    seller = session["username"]
    conn = sqlite3.connect("marketplace.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get seller's products
    cursor.execute("""
        SELECT id, product_name, price, category, timestamp
        FROM products
        WHERE seller = ?
        ORDER BY timestamp DESC
    """, (seller,))
    products = cursor.fetchall()

    # Get message counts per product
    cursor.execute("""
        SELECT item_id, COUNT(*) as message_count
        FROM messages
        WHERE receiver = ?
        GROUP BY item_id
    """, (seller,))
    raw_counts = cursor.fetchall()
    message_counts = {row["item_id"]: row["message_count"] for row in raw_counts}

    conn.close()
    return render_template("dashboard.html", products=products, message_counts=message_counts)


@app.route("/message/<int:item_id>", methods=["POST"])
def send_message(item_id):
    if "username" not in session:
        flash("Please log in to send messages.", "warning")
        return redirect("/login")

    content = request.form.get("content")
    sender = session["username"]
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()

    # Get the receiver (seller of the item)
    cursor.execute("SELECT seller FROM products WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    if not result:
        flash("Product not found.", "danger")
        conn.close()
        return redirect("/items")

    receiver = result[0]

    # Insert message with read = 0
    cursor.execute("""
        INSERT INTO messages (sender, receiver, item_id, content, timestamp, read)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sender, receiver, item_id, content, timestamp, 0))

    conn.commit()
    conn.close()

    flash("Message sent to seller!", "success")
    return redirect("/inbox")

if __name__ == "__main__":
    app.run(debug=True, port=5050)
