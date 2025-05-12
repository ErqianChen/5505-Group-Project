from flask import Flask, jsonify, request, session, render_template
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Import models and db from models.py
from models import db, User, WorkoutPlan, WorkoutRecord, SportsCategory, FavoriteCollection, BrowsingHistory

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
app.config['SECRET_KEY'] = 'your_secret_key_here'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'success': False, 'error': 'Username or Email already exists'}), 400

    hashed_pw = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()

    return jsonify({'success': True})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/plans/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    user_id = session.get('user_id')
    plan = WorkoutPlan.query.get(plan_id)
    if not plan or plan.user_id != user_id:
        return jsonify({'success': False, 'error': 'Plan not found or unauthorized'}), 404
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'No account with that email found.'}), 404
    return jsonify({'success': True, 'username': user.username})

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

