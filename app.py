from flask import Flask, jsonify, request, session, render_template
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import os

# Import models and db from models.py
from models import db, User, WorkoutPlan, WorkoutRecord, SportsCategory

app = Flask(__name__, static_folder='static', static_url_path='', template_folder='templates')
app.config['SECRET_KEY'] = 'your_secret_key_here'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# --- Authentication and Template Routes ---
@app.route('/')
def index():
    if not session.get('user_id'):
        return render_template('login.html')
    return render_template('main.html')


# log cardio route
@app.route('/workouts/log/cardio', methods=['GET'])
def cardio_page():
    return render_template('workouts/cardio.html')

# --- User Account APIs ---
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
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'No account with that email found.'}), 404
    # TODO: integrate email sending
    return jsonify({'success': True})

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

# --- Helpers ---
def get_current_user_id():
    return session.get('user_id')

def parse_range(rng: str):
    today = date.today()
    if rng == 'month':
        return today - timedelta(days=30)
    return today - timedelta(days=7)

# --- API: User Metrics ---
@app.route('/api/record/metrics')
def record_metrics():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    rng = request.args.get('range', 'week')
    start = parse_range(rng)

    recs = WorkoutRecord.query.filter(
        WorkoutRecord.user_id == user_id,
        WorkoutRecord.date >= start
    ).all()

    dates_set = {r.date for r in recs}
    streak = 0
    d = date.today()
    while d in dates_set:
        streak += 1
        d -= timedelta(days=1)

    total_cal = sum(r.calories_burn or 0 for r in recs)
    total_hrs = sum(r.duration_min or 0 for r in recs) / 60

    # Calculate percentile rank correctly
    all_users = User.query.all()
    hours_list = [
        sum(rec.duration_min for rec in u.records if rec.date >= start) / 60
        for u in all_users
    ]
    your_hours = next((h for uid, h in zip([u.id for u in all_users], hours_list) if uid == user_id), 0)
    n = len(hours_list)
    if n > 1:
        # rank position (0-based) among sorted hours
        sorted_hours = sorted(hours_list)
        # for duplicates, this gives first index
        idx = sorted_hours.index(your_hours)
        percentile = int(idx / (n - 1) * 100)
    else:
        percentile = 100

    return jsonify({
        'current_streak': streak,
        'total_calories': round(total_cal, 1),
        'total_hours': round(total_hrs, 1),
        'percentile': percentile
    })

# --- API: Trend Data (Daily Hours) ---({'error': 'Unauthorized'}), 401
    rng = request.args.get('range', 'week')
    start = parse_range(rng)

    recs = WorkoutRecord.query.filter(
        WorkoutRecord.user_id == user_id,
        WorkoutRecord.date >= start
    ).all()

    dates_set = {r.date for r in recs}
    streak = 0
    d = date.today()
    while d in dates_set:
        streak += 1
        d -= timedelta(days=1)

    total_cal = sum(r.calories_burn or 0 for r in recs)
    total_hrs = sum(r.duration_min or 0 for r in recs) / 60

    all_users = User.query.all()
    hours_list = [
        (u.id, sum(rec.duration_min for rec in u.records if rec.date >= start) / 60)
        for u in all_users
    ]
    your_hours = next((h for uid, h in hours_list if uid == user_id), 0)
    below_count = sum(1 for uid, h in hours_list if h < your_hours)
    percentile = int(below_count / len(hours_list) * 100) if hours_list else 0

    return jsonify({
        'current_streak': streak,
        'total_calories': round(total_cal, 1),
        'total_hours': round(total_hrs, 1),
        'percentile': percentile
    })

# --- API: Trend Data (Daily Hours) ---
@app.route('/api/record/trend')
def record_trend():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    rng = request.args.get('range', 'week')
    start = parse_range(rng)
    today = date.today()
    days = [start + timedelta(days=i) for i in range((today - start).days + 1)]
    labels = [d.strftime('%m-%d') for d in days]

    your_vals = []
    for d in days:
        hrs = (
            WorkoutRecord.query
            .filter_by(user_id=user_id, date=d)
            .with_entities(func.sum(WorkoutRecord.duration_min))
            .scalar() or 0
        )
        your_vals.append(round(hrs / 60, 2))

    all_users = User.query.all()
    avg_vals = []
    for d in days:
        total = 0
        for u in all_users:
            day_sum = (
                WorkoutRecord.query
                .filter_by(user_id=u.id, date=d)
                .with_entities(func.sum(WorkoutRecord.duration_min))
                .scalar() or 0
            )
            total += day_sum
        avg = (total / 60 / len(all_users)) if all_users else 0
        avg_vals.append(round(avg, 2))

    return jsonify({'labels': labels, 'you': your_vals, 'average': avg_vals})

# --- API: Aerobic vs Anaerobic Pie Chart ---
@app.route('/api/record/aeroAnaerobic')
def record_aero_anaerobic():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    rng = request.args.get('range', 'week')
    start = parse_range(rng)

    recs = (
        WorkoutRecord.query
        .join(SportsCategory)
        .filter(
            WorkoutRecord.user_id == user_id,
            WorkoutRecord.date >= start
        )
        .all()
    )

    aerobic = sum(r.duration_min for r in recs if r.category.met_value >= 6.0)
    anaerobic = sum(r.duration_min for r in recs if r.category.met_value < 6.0)

    return jsonify({
        'aerobic': round(aerobic / 60, 2),
        'anaerobic': round(anaerobic / 60, 2)
    })

# --- API: Category Comparison Radar Chart ---
@app.route('/api/record/categoryComparison')
def record_category_comparison():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    rng = request.args.get('range', 'week')
    start = parse_range(rng)

    categories = SportsCategory.query.all()
    labels = [cat.name for cat in categories]
    you_data = []
    avg_data = []
    for cat in categories:
        your_avg = (
            db.session.query(func.avg(WorkoutRecord.difficulty))
            .filter(
                WorkoutRecord.user_id == user_id,
                WorkoutRecord.category_id == cat.id,
                WorkoutRecord.date >= start
            )
            .scalar() or 0
        )
        avg_all = (
            db.session.query(func.avg(WorkoutRecord.difficulty))
            .filter(
                WorkoutRecord.category_id == cat.id,
                WorkoutRecord.date >= start
            )
            .scalar() or 0
        )
        you_data.append(round(your_avg, 2))
        avg_data.append(round(avg_all, 2))

    return jsonify({'categories': labels, 'you': you_data, 'average': avg_data})

# --- API: Calories Leaderboard ---
@app.route('/api/record/leaderboard')
def record_leaderboard():
    rng = request.args.get('range', 'week')
    start = parse_range(rng)

    stats = []
    for u in User.query.all():
        total_cal = sum(r.calories_burn for r in u.records if r.date >= start)
        total_hr = sum(r.duration_min for r in u.records if r.date >= start) / 60
        stats.append((u.username, total_cal, total_hr))

    stats.sort(key=lambda x: x[1], reverse=True)
    leaderboard = [
        {
            'rank': idx + 1,
            'username': uname,
            'total_calories': round(cal, 1),
            'total_hours': round(hr, 2)
        }
        for idx, (uname, cal, hr) in enumerate(stats[:10])
    ]
    return jsonify(leaderboard)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
