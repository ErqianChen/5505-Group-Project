import os
from app import app, db
from models import User
from datetime import datetime

os.environ["DATABASE_URI"] = "postgresql://username:password@localhost:5432/your_db"

with app.app_context():
    db.create_all()  # Create tables if they don't exist

    # Insert one user
    user = User(
        username='admin',
        email='admin@example.com',
        password_hash='pbkdf2:sha256:...',  # Replace with real hash
        created_at=datetime.utcnow()
    )
    db.session.add(user)
    db.session.commit()
    print("Database created and user inserted.")
