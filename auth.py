from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_wtf.csrf import generate_csrf

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    # Provide CSRF token for AJAX requests
    token = generate_csrf()
    return jsonify({'csrf_token': token})

@auth_bp.route('/api/signup', methods=['POST'])
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

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'No account with that email found.'}), 404
    # TODO: integrate email sending
    return jsonify({'success': True})

@auth_bp.route('/api/reset-password', methods=['POST'])
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