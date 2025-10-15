from flask import Blueprint, render_template, request, redirect, session
from models import Item, db

product_routes = Blueprint("products", __name__)

@product_routes.route("/items")
def view_items():
    items = Item.query.all()
    username = session.get("username")
    return render_template("items.html", items=items, username=username)

@product_routes.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "GET":
        return render_template("add_item.html")

    name = request.form.get("name")
    price = request.form.get("price")

    if name and price:
        new_item = Item(name=name, price=float(price))
        db.session.add(new_item)
        db.session.commit()
        return redirect("/items")
    else:
        return render_template("add_item.html", error="Please provide both name and price.")

@product_routes.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)

    if request.method == "GET":
        return render_template("edit_item.html", item=item)

    name = request.form.get("name")
    price = request.form.get("price")

    if name and price:
        item.name = name
        item.price = float(price)
        db.session.commit()
        return redirect("/items")
    else:
        return render_template("edit_item.html", item=item, error="Please provide both name and price.")

@product_routes.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect("/items")
