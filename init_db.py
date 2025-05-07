"""
This initializes the SQLite database for the Exercise Tracking Application.
It defines the database schema, creates tables, and inserts mock data.
"""

import random
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta

# Initialize Flask app and configure SQLite database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------
# Model Definitions
# ----------------------

class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    profile          = db.relationship('Profile',       back_populates='user',       uselist=False, cascade='all, delete-orphan')
    records          = db.relationship('WorkoutRecord', back_populates='user',       cascade='all, delete-orphan')
    skills           = db.relationship('UserSkill',     back_populates='user',       cascade='all, delete-orphan')
    posts            = db.relationship('Post',          back_populates='user',       cascade='all, delete-orphan')
    shares_sent      = db.relationship('Share',         foreign_keys='Share.from_user_id', back_populates='from_user', cascade='all, delete-orphan')
    shares_received  = db.relationship('Share',         foreign_keys='Share.to_user_id',   back_populates='to_user',   cascade='all, delete-orphan')
    comments         = db.relationship('Comment',       back_populates='user',       cascade='all, delete-orphan')
    likes            = db.relationship('Like',          back_populates='user',       cascade='all, delete-orphan')
    bookmarks        = db.relationship('Bookmark',      back_populates='user',       cascade='all, delete-orphan')

class Profile(db.Model):
    __tablename__ = 'profiles'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    height_cm   = db.Column(db.Integer)
    weight_kg   = db.Column(db.Float)
    gender      = db.Column(db.String(10))
    fav_sports  = db.Column(db.String(256))  # JSON string of favorite sports

    # Relationship back to User
    user = db.relationship('User', back_populates='profile')

class SportsCategory(db.Model):
    __tablename__ = 'sports_categories'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(80), unique=True, nullable=False)
    met_value  = db.Column(db.Float)  # Metabolic Equivalent of Task (MET) value for the activity

    # Relationships
    records    = db.relationship('WorkoutRecord', back_populates='category', cascade='all, delete-orphan')
    skills     = db.relationship('UserSkill',      back_populates='category', cascade='all, delete-orphan')
    tutorials  = db.relationship('Tutorial',       back_populates='category', cascade='all, delete-orphan')

class WorkoutRecord(db.Model):
    __tablename__ = 'workout_records'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),     nullable=False)
    category_id   = db.Column(db.Integer, db.ForeignKey('sports_categories.id', ondelete='CASCADE'), nullable=False)
    date          = db.Column(db.Date, nullable=False)
    duration_min  = db.Column(db.Integer, nullable=False)   # Duration in minutes
    difficulty    = db.Column(db.Integer, nullable=False)   # Subjective difficulty 1–5
    calories_burn = db.Column(db.Float)                    # Precomputed calories

    # Relationships
    user     = db.relationship('User',           back_populates='records')
    category = db.relationship('SportsCategory', back_populates='records')

class UserSkill(db.Model):
    """
    User's skill level (1–5) for each sports category.
    """
    __tablename__ = 'user_skills'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('sports_categories.id', ondelete='CASCADE'), nullable=False)
    skill_level = db.Column(db.Integer, nullable=False)  # 1–5 scale
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user     = db.relationship('User',           back_populates='skills')
    category = db.relationship('SportsCategory', back_populates='skills')

class Tutorial(db.Model):
    """
    Tutorial links per category and level.
    """
    __tablename__ = 'tutorials'
    id          = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('sports_categories.id', ondelete='CASCADE'), nullable=False)
    level       = db.Column(db.Integer, nullable=False)   # Recommended for skill level
    title       = db.Column(db.String(256), nullable=False)
    url         = db.Column(db.String(512), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    category = db.relationship('SportsCategory', back_populates='tutorials')

class Share(db.Model):
    __tablename__ = 'shares'
    id            = db.Column(db.Integer, primary_key=True)
    record_id     = db.Column(db.Integer, db.ForeignKey('workout_records.id', ondelete='CASCADE'), nullable=False)
    from_user_id  = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    to_user_id    = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    shared_at     = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    from_user = db.relationship('User', foreign_keys=[from_user_id], back_populates='shares_sent')
    to_user   = db.relationship('User', foreign_keys=[to_user_id],   back_populates='shares_received')
    record    = db.relationship('WorkoutRecord')

class Post(db.Model):
    __tablename__ = 'posts'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    record_id  = db.Column(db.Integer, db.ForeignKey('workout_records.id', ondelete='SET NULL'))
    content    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user     = db.relationship('User',           back_populates='posts')
    record   = db.relationship('WorkoutRecord')
    comments = db.relationship('Comment',        back_populates='post', cascade='all, delete-orphan')
    likes    = db.relationship('Like',           back_populates='post', cascade='all, delete-orphan')
    bookmarks= db.relationship('Bookmark',       back_populates='post', cascade='all, delete-orphan')

class Comment(db.Model):
    __tablename__ = 'comments'
    id         = db.Column(db.Integer, primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    post = db.relationship('Post', back_populates='comments')
    user = db.relationship('User', back_populates='comments')

class Like(db.Model):
    __tablename__ = 'likes'
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='likes')

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    post_id    = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='bookmarks')
    post = db.relationship('Post', back_populates='bookmarks')


# -----------------------------------
# Database Initialization and Mock Data
# -----------------------------------
def init_db():
    """Initialize the database and insert mock data step by step."""
    db.drop_all()
    db.create_all()

    # 1. Insert Users
    usernames = [
        ('taylorswift',    'taylor@example.com'),
        ('edsheeran',      'ed@example.com'),
        ('beyonce',        'beyonce@example.com'),
        ('adele',          'adele@example.com'),
        ('drake',          'drake@example.com'),
        ('rihanna',        'rihanna@example.com'),
        ('justinbieber',   'justin@example.com'),
        ('arianagrande',   'ariana@example.com')
    ]
    users = []
    fitness_bases = [1.5,1.3,1.1,0.9,0.8,0.6,0.4,0.2]
    for (uname, mail), base in zip(usernames, fitness_bases):
        user = User(username=uname, email=mail,
                    password_hash=generate_password_hash('password123'))
        db.session.add(user)
        db.session.commit()
        user.fitness_base = base
        users.append(user)

    # 2. Insert Profiles
    profiles_data = [
        (178, 60, 'female', ['Running','Yoga']),
        (173, 68, 'male',   ['Cycling','Swimming']),
        (169, 62, 'female', ['Weightlifting','Running']),
        (175, 70, 'female', ['Pilates','Running']),
        (182, 85, 'male',   ['Basketball','Running']),
        (170, 60, 'female', ['Dance','Yoga']),
        (177, 65, 'male',   ['Football','Cycling']),
        (165, 55, 'female', ['Swimming','Pilates'])
    ]
    for user, pdata in zip(users, profiles_data):
        profile = Profile(
            user_id=user.id,
            height_cm=pdata[0],
            weight_kg=pdata[1],
            gender=pdata[2],
            fav_sports=str(pdata[3])
        )
        db.session.add(profile)
    db.session.commit()

    # 3. Insert Sports Categories
    categories = [
        ('Running', 9.8), ('Swimming', 8.0), ('Cycling', 7.5),
        ('Weightlifting', 6.0), ('Yoga', 2.5), ('Basketball', 8.0),
        ('Pilates', 3.0), ('Football', 7.0), ('Dance', 6.5)
    ]
    cat_objs = {}
    for name, met in categories:
        cat = SportsCategory(name=name, met_value=met)
        db.session.add(cat)
        db.session.commit()
        cat_objs[name] = cat

    # 4. Insert User Skills (initial level = 3 for all)
    for user in users:
        for cname, _ in categories:
            skill = UserSkill(
                user_id=user.id,
                category_id=cat_objs[cname].id,
                skill_level=3
            )
            db.session.add(skill)
    db.session.commit()

    # 5. Insert Tutorials for various levels
    tutorials_data = [
        # (category_name, level, title, url)
        ('Running',       1, 'Beginner Running Drills',         'https://youtu.be/run-beg1'),
        ('Running',       3, 'Intermediate Interval Training',  'https://youtu.be/run-int3'),
        ('Running',       5, 'Advanced Marathon Prep',         'https://youtu.be/run-adv5'),
        ('Yoga',          1, 'Yoga for Total Beginners',        'https://youtu.be/yoga-beg1'),
        ('Yoga',          3, 'Power Yoga Sequence',            'https://youtu.be/yoga-int3'),
        ('Yoga',          5, 'Advanced Yoga Flows',            'https://youtu.be/yoga-adv5'),
        # ... add more tutorials as needed ...
    ]
    for cname, lvl, title, link in tutorials_data:
        tut = Tutorial(
            category_id=cat_objs[cname].id,
            level=lvl,
            title=title,
            url=link
        )
        db.session.add(tut)
    db.session.commit()

    # 6. Insert Workout Records (simulate daily routines over last 90 days)
    start_date = date.today() - timedelta(days=89)
    total_days = 90
    for i, user in enumerate(users):
        # Determine training intensity by user index: even-indexed users train 6 days/week, odd-indexed users train 4 days/week
        rest_day_offset = i % 7  # Which weekday the user rests each week (0=Monday ... 6=Sunday)
        for day_offset in range(total_days):
            current_day = start_date + timedelta(days=day_offset)
            weekday = day_offset % 7
            # Heavy trainers: rest one day per week; light trainers: rest three days per week
            if i % 2 == 0:
                # Heavy trainer: skip the rest day
                if weekday == rest_day_offset:
                    continue
            else:
                # Light trainer: rest on three specific weekdays
                rest_days = (rest_day_offset, (rest_day_offset+2)%7, (rest_day_offset+4)%7)
                if weekday in rest_days:
                    continue

            # Rotate through exercise categories to increase variety
            cname = categories[(day_offset * (i+1)) % len(categories)][0]
            cat = cat_objs[cname]

            # Calculate duration: 30–75 minutes cycling by formula
            duration = 30 + ((day_offset * 5 + i*3) % 46)
            # Calculate difficulty: cycle through 1–5
            difficulty = 1 + ((day_offset + i) % 5)

            # Compute calories: (duration in hours) × MET × user weight
            weight = profiles_data[i][1]
            calories = duration / 60 * cat.met_value * weight

            rec = WorkoutRecord(
                user_id=user.id,
                category_id=cat.id,
                date=current_day,
                duration_min=duration,
                difficulty=difficulty,
                calories_burn=round(calories, 2)
            )
            db.session.add(rec)

        # Commit the records for each user after insertion
        db.session.commit()


        
    # 7. Insert Shares (each user's first record to the next user)
    all_records = WorkoutRecord.query.order_by(WorkoutRecord.id).all()
    for idx, rec in enumerate(all_records[:-1]):
        share = Share(
            record_id=rec.id,
            from_user_id=rec.user_id,
            to_user_id=users[(idx + 1) % len(users)].id
        )
        db.session.add(share)
    db.session.commit()

    # 8. Insert Posts (2 per user), Comments, Likes, Bookmarks
    posts = []
    for i, user in enumerate(users):
        p1 = Post(
            user_id=user.id,
            record_id=all_records[i].id,
            content=f"{user.username} completed a {all_records[i].duration_min}-min {all_records[i].category.name} session!"
        )
        p2 = Post(
            user_id=user.id,
            content=f"Keep going! {user.username} is crushing it this week!"
        )
        db.session.add(p1); db.session.commit(); posts.append(p1)
        db.session.add(p2); db.session.commit(); posts.append(p2)

    for idx, post in enumerate(posts[:len(users)]):
        c1 = Comment(post_id=post.id, user_id=users[(idx+1) % len(users)].id,
                     content="Awesome work!")
        c2 = Comment(post_id=post.id, user_id=users[(idx+2) % len(users)].id,
                     content="Keep it up!")
        db.session.add(c1); db.session.add(c2)
    db.session.commit()

    first_post = posts[0]
    for user in users:
        like = Like(user_id=user.id, post_id=first_post.id)
        db.session.add(like)
    db.session.commit()

    for idx, user in enumerate(users):
        target = posts[(idx*2 + 1) % len(posts)]
        bookmark = Bookmark(user_id=user.id, post_id=target.id)
        db.session.add(bookmark)
    db.session.commit()

    print("Database initialized with full schema and mock data.")

if __name__ == '__main__':
    with app.app_context():
        init_db()