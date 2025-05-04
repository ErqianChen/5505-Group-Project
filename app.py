from flask import Flask, jsonify, request, session, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta

# --- Flask and Database Initialization ---
# Create the Flask application, serve static files from the project root, and use root as template folder
app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
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

# --- Render Main Page ---
@app.route('/')
def index():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)
