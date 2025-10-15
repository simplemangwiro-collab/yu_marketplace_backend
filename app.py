from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import check_password_hash
from models import db, User
import sqlite3

app = Flask(__name__)
app.secret_key = "super_secret_key_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def home():
    return "Welcome to YU Marketplace!"

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

@app.route('/about')
def about():
    return "This is a student-built backend for YU Marketplace."

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()

    if request.method == 'POST':
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
        return redirect('/items')

    cursor.execute("SELECT product_name, price, category, image_url FROM products WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return render_template("edit.html", item=item, item_id=item_id)

@app.route('/items')
def get_items():
    if "username" not in session:
        flash("Please log in to view products.", "warning")
        return redirect("/login")

    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_name, price, category, image_url FROM products")
    items = cursor.fetchall()
    conn.close()
    return render_template("items.html", items=items)

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Product deleted successfully!", "info")
    return redirect('/items')

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if "username" not in session:
        flash("Please log in to upload products.", "warning")
        return redirect("/login")

    if request.method == 'POST':
        name = request.form['product_name']
        price = request.form['price']
        category = request.form['category']
        image_url = request.form['image_url']

        if not name or not price:
            flash("Missing product name or price", "danger")
            return render_template("add.html")

        conn = sqlite3.connect("marketplace.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (product_name, price, category, image_url) VALUES (?, ?, ?, ?)",
            (name, price, category, image_url)
        )
        conn.commit()
        conn.close()
        flash("Product uploaded successfully!", "success")
        return redirect('/items')

    return render_template("add.html")

if __name__ == '__main__':
    app.run(debug=True, port=5050)
