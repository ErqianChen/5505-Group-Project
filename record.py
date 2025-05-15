from flask import Blueprint, jsonify, request, session
from datetime import date, timedelta
from sqlalchemy import func
from models import db, User, WorkoutRecord, SportsCategory


record_bp = Blueprint('record', __name__)

def get_current_user_id():
    return session.get('user_id')

def parse_range(rng: str):
    today = date.today()
    if rng == 'month':
        return today - timedelta(days=30)
    return today - timedelta(days=7)

@record_bp.route('/api/record/metrics')
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

    all_users = User.query.all()
    hours_list = [
        sum(rec.duration_min for rec in u.records if rec.date >= start) / 60
        for u in all_users
    ]
    your_hours = next((h for uid, h in zip([u.id for u in all_users], hours_list) if uid == user_id), 0)
    n = len(hours_list)
    if n > 1:
        sorted_hours = sorted(hours_list)
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

@record_bp.route('/api/record/trend')
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

@record_bp.route('/api/record/aeroAnaerobic')
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

    aerobic = sum(r.duration_min for r in recs if r.category and r.category.met_value >= 6.0)
    anaerobic = sum(r.duration_min for r in recs if r.category and r.category.met_value < 6.0)

    return jsonify({
        'aerobic': round(aerobic / 60, 2),
        'anaerobic': round(anaerobic / 60, 2)
    })

@record_bp.route('/api/record/categoryComparison')
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

@record_bp.route('/api/record/leaderboard')
def record_leaderboard():
    rng = request.args.get('range', 'week')
    start = parse_range(rng)

    stats = []
    for u in User.query.all():
        total_cal = sum((r.calories_burn or 0) for r in u.records if r.date >= start)
        total_hr = sum((r.duration_min or 0) for r in u.records if r.date >= start) / 60
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

@record_bp.route('/api/log_cardio', methods=['POST'])
def log_cardio():
    user_id = get_current_user_id()
    print("user_id:", user_id)
    if not user_id:
        print("No user_id in session")
        return jsonify({'error': 'Unauthorized'}), 401

    activity = request.form.get('activity')
    duration = request.form.get('duration')
    calories = request.form.get('calories')
    print("Received:", activity, duration, calories)

    # Validate required fields
    if not activity or not duration or not calories:
        return jsonify({'error': 'Missing required fields'}), 400

    # Find the sports category by name
    category = SportsCategory.query.filter_by(name=activity).first()
    if not category:
        return jsonify({'error': 'Invalid activity type'}), 400

    try:
        record = WorkoutRecord(
            user_id=user_id,
            category_id=category.id,
            date=date.today(),
            duration_min=int(float(duration)),
            difficulty=1,  # Always set a default value for difficulty
            calories_burn=float(calories)
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
  
    
@record_bp.route('/api/log_strength', methods=['POST'])
def log_strength():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    activity = request.form.get('activity')
    duration = request.form.get('duration')
    calories = request.form.get('calories')
    difficulty = request.form.get('difficulty', 1)

    # Find the sports category by name
    category = SportsCategory.query.filter_by(name=activity).first()
    if not category:
        return jsonify({'error': 'Invalid activity type'}), 400

    try:
        record = WorkoutRecord(
            user_id=user_id,
            category_id=category.id,
            date=date.today(),
            duration_min=int(float(duration)),
            difficulty=int(difficulty),
            calories_burn=float(calories)
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500