from app import app, db
from models import User
from datetime import datetime

with app.app_context():
    user = User(
        username='admin',
        email='admin@example.com',
        password_hash='pbkdf2:sha256:...',  # Replace with real hashed password
        created_at=datetime.utcnow()
    )
    db.session.add(user)
    db.session.commit()
    print("User inserted.")
