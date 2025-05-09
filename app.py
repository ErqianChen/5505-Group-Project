from flask import Flask, jsonify, request, session, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import date, datetime, timedelta
from init_db import db, WorkoutPlan, FavoriteCollection, BrowsingHistory
import os

# --- Flask and Database Initialization ---
# Create the Flask application, serve static files from the project root, and use root as template folder
app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
app.config['SECRET_KEY'] = 'your_secret_key_here'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Model Definitions (simplified) ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Omitted email/password fields for brevity
    records = db.relationship('WorkoutRecord', back_populates='user', cascade='all, delete-orphan')

class SportsCategory(db.Model):
    __tablename__ = 'sports_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    met_value = db.Column(db.Float)
    records = db.relationship('WorkoutRecord', back_populates='category', cascade='all, delete-orphan')

class WorkoutRecord(db.Model):
    __tablename__ = 'workout_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('sports_categories.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration_min = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)  # Scale 1–5
    calories_burn = db.Column(db.Float)
    user = db.relationship('User', back_populates='records')
    category = db.relationship('SportsCategory', back_populates='records')

# --- Helper: Get Current User ID ---
def get_current_user_id():
    # In a real app, fetch from session after login; here default to user 1
    return session.get('user_id', 1)

# --- Helper: Calculate Start Date for Ranges ---
def parse_range(rng: str):
    today = date.today()
    if rng == 'month':
        return today - timedelta(days=30)
    # Default to week range
    return today - timedelta(days=7)

# --- API: User Metrics ---
@app.route('/api/record/metrics')
def record_metrics():
    user_id = get_current_user_id()
    rng = request.args.get('range', 'week')
    start = parse_range(rng)

    # Fetch all records for this user within the range
    recs = WorkoutRecord.query.filter(
        WorkoutRecord.user_id == user_id,
        WorkoutRecord.date >= start
    ).all()

    # 1. Calculate current consecutive days streak
    dates = {r.date for r in recs}
    streak = 0
    d = date.today()
    while d in dates:
        streak += 1
        d -= timedelta(days=1)

    # 2. Sum total calories and hours
    total_cal = sum(r.calories_burn for r in recs)
    total_hrs = sum(r.duration_min for r in recs) / 60

    # 3. Compute percentile of this user's hours against all users
    all_users = User.query.all()
    hours_list = [(u.id, sum(r.duration_min for r in u.records if r.date >= start) / 60) for u in all_users]
    your_hours = next(h for uid, h in hours_list if uid == user_id)
    below_count = sum(1 for _, h in hours_list if h < your_hours)
    percentile = int(below_count / len(hours_list) * 100)

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
    rng     = request.args.get('range', 'week')
    start   = parse_range(rng)
    today   = date.today()

    # build list of dates from start → today
    days   = [start + timedelta(days=i) for i in range((today - start).days + 1)]
    labels = [d.strftime('%m-%d') for d in days]

    # 1) Your daily hours
    your_vals = []
    for d in days:
        hrs = (WorkoutRecord.query
               .filter_by(user_id=user_id, date=d)
               .with_entities(db.func.sum(WorkoutRecord.duration_min))
               .scalar() or 0)
        your_vals.append(round(hrs / 60, 2))

    # 2) Group average daily hours
    all_users = User.query.all()
    avg_vals  = []
    for d in days:
        total = 0
        for u in all_users:
            day_sum = (WorkoutRecord.query
                       .filter_by(user_id=u.id, date=d)
                       .with_entities(db.func.sum(WorkoutRecord.duration_min))
                       .scalar() or 0)
            total += day_sum
        # avoid divide-by-zero
        avg = (total / 60 / len(all_users)) if all_users else 0
        avg_vals.append(round(avg, 2))

    return jsonify({
        'labels':  labels,
        'you':     your_vals,
        'average': avg_vals
    })

# --- API: Aerobic vs Anaerobic Pie Chart ---
@app.route('/api/record/aeroAnaerobic')
def record_aero_anaerobic():
    user_id = get_current_user_id()
    rng = request.args.get('range', 'week')
    start = parse_range(rng)

    aero = ana = 0.0
    recs = WorkoutRecord.query.join(SportsCategory).filter(
        WorkoutRecord.user_id == user_id,
        WorkoutRecord.date >= start
    ).all()
    for r in recs:
        if r.category.met_value >= 6.0:
            aero += r.duration_min
        else:
            ana += r.duration_min

    # Convert minutes to hours
    return jsonify({
        'aerobic': round(aero/60, 2),
        'anaerobic': round(ana/60, 2)
    })

# --- API: Category Comparison Radar Chart ---
@app.route('/api/record/categoryComparison')
def record_category_comparison():
    user_id = get_current_user_id()
    rng = request.args.get('range', 'week')
    start = parse_range(rng)

    # Collect unique categories in range
    cat_names = sorted({r.category.name for r in WorkoutRecord.query.filter(
        WorkoutRecord.user_id == user_id,
        WorkoutRecord.date >= start
    )})
    you_data, avg_data = [], []
    for name in cat_names:
        your_avg = db.session.query(db.func.avg(WorkoutRecord.difficulty)).join(SportsCategory).filter(
            WorkoutRecord.user_id == user_id,
            SportsCategory.name == name,
            WorkoutRecord.date >= start
        ).scalar() or 0
        avg_all = db.session.query(db.func.avg(WorkoutRecord.difficulty)).join(SportsCategory).filter(
            SportsCategory.name == name,
            WorkoutRecord.date >= start
        ).scalar() or 0
        you_data.append(round(your_avg, 2))
        avg_data.append(round(avg_all, 2))

    return jsonify({'categories': cat_names, 'you': you_data, 'average': avg_data})

# --- API: Calories Leaderboard ---
@app.route('/api/record/leaderboard')
def record_leaderboard():
    rng = request.args.get('range', 'week')
    start = parse_range(rng)

    # Compute total calories & hours for all users in range
    stats = []
    for u in User.query.all():
        recs = [r for r in u.records if r.date >= start]
        total_cal = sum(r.calories_burn for r in recs)
        total_hr = sum(r.duration_min for r in recs) / 60
        stats.append((u.username, total_cal, total_hr))

    # Sort by calories desc, take top 10
    stats.sort(key=lambda x: x[1], reverse=True)
    leaderboard = [{'rank': idx+1, 'username': uname, 'total_calories': round(cal,1), 'total_hours': round(hr,2)}
                   for idx, (uname, cal, hr) in enumerate(stats[:10])]

    return jsonify(leaderboard)

# --- Page Account: My Information ---
@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    user = User.query.get(user_id)
    return jsonify({
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.strftime('%Y-%m-%d')
    })

# --- Page Account: My Collection ---
@app.route('/api/user/collections', methods=['GET'])
def get_user_collections():
    user_id = session.get('user_id')
    items = FavoriteCollection.query.filter_by(user_id=user_id).all()
    return jsonify([{'title': i.title, 'type': i.content_type} for i in items])

# --- Page Account: Browsing History ---
@app.route('/api/user/history', methods=['GET'])
def get_user_history():
    user_id = session.get('user_id')
    logs = BrowsingHistory.query.filter_by(user_id=user_id).order_by(BrowsingHistory.timestamp.desc()).limit(20)
    return jsonify([{
        'action': log.action,
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M')
    } for log in logs])

# --- Page Account: My plan ---
@app.route('/api/user/plan/add', methods=['POST'])
def add_plan():
    user_id = session.get('user_id', 1)  # 默认 1
    data = request.get_json()
    try:
        plan = WorkoutPlan(
            user_id=user_id,
            activity=data['activity'],
            start_time=datetime.fromisoformat(data['start']),
            end_time=datetime.fromisoformat(data['end'])
        )
        db.session.add(plan)
        db.session.commit()
        return jsonify({'success': True, 'id': plan.id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/plans', methods=['GET'])
def get_plans():
    user_id = session.get('user_id', 1)
    date_str = request.args.get('date')
    if date_str:
        try:
            date_obj = datetime.fromisoformat(date_str)
            start = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            end = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
            plans = WorkoutPlan.query.filter(
                WorkoutPlan.user_id == user_id,
                WorkoutPlan.start_time >= start,
                WorkoutPlan.start_time <= end
            ).all()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        plans = WorkoutPlan.query.filter_by(user_id=user_id).all()

    return jsonify([{
        'id': plan.id,
        'activity': plan.activity,
        'start_time': plan.start_time.isoformat(),
        'end_time': plan.end_time.isoformat()
    } for plan in plans])

@app.route('/api/plans/<int:plan_id>', methods=['PUT'])
def update_plan(plan_id):
    user_id = session.get('user_id', 1)
    data = request.get_json()
    plan = WorkoutPlan.query.get(plan_id)

    if not plan or plan.user_id != user_id:
        return jsonify({'success': False, 'error': 'Plan not found or permission denied'}), 404

    try:
        plan.activity = data['activity']
        plan.start_time = datetime.fromisoformat(data['start'])
        plan.end_time = datetime.fromisoformat(data['end'])
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/my_plan')
def my_plan_page():
    return render_template('my_plan.html')

#get data from cardio page
@app.route('/log_cardio', methods=['POST'])
def log_cardio():
    activity = request.form.get('activity')
    duration = int(request.form.get('duration'))
    calories_raw = request.form.get('calories')
    try:
        calories = float(calories_raw) if calories_raw else 0.0
    except ValueError:
        calories = 0.0

    user_id = get_current_user_id()

    # 查找对应运动类型的 category_id
    category = SportsCategory.query.filter(func.lower(SportsCategory.name) == activity.lower()).first()
    if not category:
        return "Activity type not found in database.", 400

    # 暂时假设难度为 3（中等），也可以根据 activity 自定义一个逻辑
    record = WorkoutRecord(
        user_id=user_id,
        category_id=category.id,
        date=date.today(),
        duration_min=duration,
        difficulty=3,
        calories_burn=calories
    )

    db.session.add(record)
    db.session.commit()

    return "Workout logged successfully!"


# --- Render Main Page ---
@app.route('/')
def index():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)
