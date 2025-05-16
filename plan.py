# plan.py
from flask import Blueprint, render_template, session, redirect
from models import WorkoutPlan, User
from datetime import datetime
from sqlalchemy import func

plan_bp = Blueprint('plan_bp', __name__)

@plan_bp.route('/my_plan')
def my_plan():
    if not session.get('user_id'):
        return redirect('/login_system/login.html')

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    today = datetime.now().date()
    plans = WorkoutPlan.query.filter(
        func.date(WorkoutPlan.start_time) == today,
        WorkoutPlan.user_id == user_id
    ).all()

    total_minutes = sum([(plan.end_time - plan.start_time).seconds // 60 for plan in plans])
    total_time_str = f"{total_minutes // 60}h {total_minutes % 60}min"

    return render_template('my_plan.html',
                           username=user.username,
                           coins=66,#Todo
                           total_time=total_time_str,
                           calories=2000,#Todo
                           plans=[{
                               'id': p.id,
                               'activity': p.activity,
                               'start_time': p.start_time.strftime('%Y-%m-%dT%H:%M'),
                               'end_time': p.end_time.strftime('%Y-%m-%dT%H:%M')
                           } for p in plans],
                           current_date=today.strftime('%Y-%m-%d'))
