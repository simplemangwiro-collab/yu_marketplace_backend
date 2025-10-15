from flask import Blueprint, request, jsonify, render_template, redirect, session
from models import User, Item, db

auth_routes = Blueprint("auth", __name__)

@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    # Handle form or JSON data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session["username"] = user.username  # ✅ Store username in session
        if request.is_json:
            return jsonify({"message": "Login successful"}), 200
        else:
            return redirect("/items")  # ✅ Redirect to product page
    else:
        if request.is_json:
            return jsonify({"error": "Invalid email or password"}), 401
        else:
            return render_template("login.html", error="Invalid credentials")

@auth_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # Handle form or JSON data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Check for existing user
    if User.query.filter((User.email == email) | (User.username == username)).first():
        if request.is_json:
            return jsonify({"error": "User already exists"}), 409
        else:
            return render_template("register.html", error="User already exists")

    # Create new user
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    if request.is_json:
        return jsonify({"message": "User registered successfully"}), 201
    else:
        return redirect("/login")

@auth_routes.route("/logout")
def logout():
    session.clear()  # ✅ Clear session on logout
    return redirect("/login")
