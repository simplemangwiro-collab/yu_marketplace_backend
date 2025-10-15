from models import db, User, Item
from flask import Flask

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    # Create tables
    db.create_all()

    # Seed user
    if not User.query.filter_by(email="geoff@example.com").first():
        user = User(username="geoff", email="geoff@example.com")
        user.set_password("securepassword123")
        db.session.add(user)
        print("✅ Test user created.")
    else:
        print("ℹ️ User already exists.")

    # Seed items
    if not Item.query.first():
        item1 = Item(name="Notebook", price=5.99)
        item2 = Item(name="Pen", price=1.49)
        item3 = Item(name="Backpack", price=29.99)
        item4 = Item(name="Moment",price=5000)
        item5 = Item(name="Nyasha",price=6000)
        item6 = Item(name="Thelma",price=7000)
        items7 =Item(name="Natasha",price=8000)
        db.session.add_all([item1, item2, item3])
        print("✅ Sample items inserted.")
    else:
        print("ℹ️ Items already exist.")

    db.session.commit()
