from app import app
from models import db, User

with app.app_context():
    new_user = User(username='geoff', email='geoff@example.com')
    new_user.set_password('securepassword123')
    db.session.add(new_user)
    db.session.commit()
    print("Test user added.")
