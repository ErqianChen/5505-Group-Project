# This script initializes the database with mock data for a fitness application.
# Forgot to mention on the PR comment: The default password for all users is 'password'!

from flask import Flask
from models import (
    db,
    User,
    SportsCategory,
    WorkoutPlan,
    WorkoutRecord,
    FavoriteCollection,
    BrowsingHistory,
    Comment,
    Like,
    Bookmark,
    Post
)
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import os
import random

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def init_db():
    # Drop and recreate all tables
    db.drop_all()
    db.create_all()

    # Seed users with popular Western pop singers
    singers = [
        ('taylor_swift', 'taylor@example.com', 'password'),
        ('ed_sheeran', 'ed@example.com', 'password'),
        ('beyonce', 'beyonce@example.com', 'password'),
        ('bruno_mars', 'bruno@example.com', 'password'),
        ('adele', 'adele@example.com', 'password'),
        ('rihanna', 'rihanna@example.com', 'password'),
        ('justin_bieber', 'justin@example.com', 'password'),
        ('lady_gaga', 'gaga@example.com', 'password'),
        ('katy_perry', 'katy@example.com', 'password'),
        ('shawn_mendes', 'shawn@example.com', 'password')
    ]
    users = []
    for uname, email, pw in singers:
        u = User(
            username=uname,
            email=email,
            password_hash=generate_password_hash(pw),
            created_at=datetime.utcnow()
        )
        users.append(u)
        db.session.add(u)

    # Seed sports categories
    categories = [
        ('Running', 9.8),
        ('Cycling', 7.5),
        ('Swimming', 8.0),
        ('Yoga', 3.0),
        ('Weightlifting', 6.0),
        ('HIIT', 10.0)
    ]
    cats = []
    for name, met in categories:
        c = SportsCategory(name=name, met_value=met)
        cats.append(c)
        db.session.add(c)

    db.session.commit()

    # Seed workout plans for each user
    for u in users:
        for i, c in enumerate(cats[:3]):  # each user 3 plans
            start = datetime.utcnow() + timedelta(days=i)
            end = start + timedelta(hours=1)
            plan = WorkoutPlan(
                user_id=u.id,
                activity=c.name,
                start_time=start,
                end_time=end
            )
            db.session.add(plan)

    # Seed diverse workout records for each user
    # Each user will have multiple records for each category over the past 60 days
    for u in users:
        for c in cats:
            # generate between 5 and 10 records per category per user
            count = random.randint(5, 10)
            for _ in range(count):
                days_ago = random.randint(0, 60)
                rec_date = date.today() - timedelta(days=days_ago)
                duration = random.randint(20, 120)  # duration between 20 and 120 minutes
                difficulty = random.randint(1, 5)   # difficulty level 1-5
                # approximate calories burned using MET, assuming 70kg individual
                calories = int(c.met_value * 70 * (duration / 60))
                record = WorkoutRecord(
                    user_id=u.id,
                    category_id=c.id,
                    date=rec_date,
                    duration_min=duration,
                    difficulty=difficulty,
                    calories_burn=calories
                )
                db.session.add(record)

    # Seed favorite collections
    for u in users:
        for idx in range(2):
            fav = FavoriteCollection(
                user_id=u.id,
                title=f"Favorites {idx+1} for {u.username}",
                content_type="workout_plan",
                created_at=datetime.utcnow()
            )
            db.session.add(fav)

    # Seed browsing history
    for u in users:
        for idx in range(3):
            bh = BrowsingHistory(
                user_id=u.id,
                action=f"Viewed category {cats[idx].name}",
                timestamp=datetime.utcnow() - timedelta(minutes=idx * 10)
            )
            db.session.add(bh)

    # --- Seed Social Posts, Likes, Comments, Bookmarks ---
    post_contents = [
        "Just finished a killer workout session! 🏋️‍♀️💦",
        "Tried morning yoga 🧘‍♀️— feel calm and centered.",
        "Pushed my limits on bench press today! 💪🔥",
        "Morning run with friends, best way to start the day! 🏃‍♂️☀️",
        "Discovered a new HIIT routine, totally recommend!",
        "Yoga stretches really helped my back.",
        "Cycling by the river, beautiful views! 🚴‍♀️🌊",
        "First time swimming 1km non-stop! 🏊‍♂️",
        "Weightlifting PR smashed! 🏋️‍♂️",
        "Rest day, but still did some stretching."
    ]
    posts = []
    for i, content in enumerate(post_contents):
        author = random.choice(users)
        post = Post(user_id=author.id, content=content, created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10)))
        db.session.add(post)
        posts.append(post)
    db.session.commit()

    # Randomly generate likes, comments, and bookmarks
    for post in posts:
        # Random likes
        like_users = random.sample(users, random.randint(1, min(5, len(users))))
        for u in like_users:
            db.session.add(Like(user_id=u.id, post_id=post.id, created_at=datetime.utcnow()))
        # Random bookmarks
        bookmark_users = random.sample(users, random.randint(1, min(5, len(users))))
        for u in bookmark_users:
            db.session.add(Bookmark(user_id=u.id, post_id=post.id, created_at=datetime.utcnow()))
        # Random comments
        for _ in range(random.randint(1, 5)):
            commenter = random.choice(users)
            text = random.choice([
                "Great job!", "Amazing progress!", "Keep it up!", "Love this!", "So inspiring!", "Nice work!", "🔥🔥🔥"
            ])
            db.session.add(Comment(user_id=commenter.id, post_id=post.id, content=text, created_at=datetime.utcnow() - timedelta(hours=random.randint(0, 48))))
    db.session.commit()

    db.session.commit()
    print("Database initialized with mock data.")

if __name__ == '__main__':
    with app.app_context():
        init_db()
