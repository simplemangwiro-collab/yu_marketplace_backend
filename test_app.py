from flask import Flask
from models import db
from routes.auth import auth_routes
from routes.products import product_routes

app = Flask(__name__)
app.secret_key = "supersecret123"  # ✅ Enables session support

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(auth_routes)
app.register_blueprint(product_routes)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
