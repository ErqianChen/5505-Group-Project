from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def init_db():
    db.drop_all()
    db.create_all()

    # Optional: Add test users
    users = [
        ('alice', 'alice@example.com', 'password123'),
        ('bob', 'bob@example.com', 'password456')
    ]

    for uname, email, pw in users:
        user = User(username=uname, email=email, password_hash=generate_password_hash(pw))
        db.session.add(user)
    db.session.commit()

    print("✅ Database initialized with demo users.")

if __name__ == '__main__':
    with app.app_context():
        init_db()
