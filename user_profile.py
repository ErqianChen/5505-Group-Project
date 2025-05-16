import os
from flask import (
    Blueprint, render_template, request, session,
    current_app, redirect, url_for, flash
)
from werkzeug.utils import secure_filename
from models import db, User

profile_bp = Blueprint('profile_bp', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 1) Account main page
@profile_bp.route('/account')
def account():
    uid = session.get('user_id')
    if not uid: return redirect(url_for('auth_bp.login'))
    user = User.query.get_or_404(uid)
    return render_template('account.html', user=user)

# 2) check information page
@profile_bp.route('/account/info')
def my_info():
    uid = session.get('user_id')
    if not uid: return redirect(url_for('auth_bp.login'))
    user = User.query.get_or_404(uid)
    return render_template('my_info.html', user=user)

# 3) edit information page
@profile_bp.route('/account/edit', methods=['GET','POST'])
def edit_info():
    uid = session.get('user_id')
    if not uid: return redirect(url_for('auth_bp.login'))
    user = User.query.get_or_404(uid)

    if request.method == 'POST':
        # deal with nickname and address
        user.nickname = request.form.get('nickname') or user.nickname
        user.address  = request.form.get('address')  or user.address
        # deal with avatar
        file = request.files.get('avatar')
        if file and file.filename:
            ALLOWED = {'png','jpg','jpeg'}
            ext = file.filename.rsplit('.',1)[-1].lower()
            if ext not in ALLOWED:
                flash('only JPG/PNG', 'error')
            else:
                if file.content_length > 5*1024*1024:
                    flash('no bigger than 5MB', 'error')
                else:
                    fn = secure_filename(file.filename)
                    updir = current_app.config['UPLOAD_FOLDER']
                    os.makedirs(updir, exist_ok=True)
                    path = os.path.join(updir, fn)
                    file.save(path)
                    user.avatar = fn
        db.session.commit()
        flash('flashed!', 'success')
        return redirect(url_for('profile_bp.my_info'))

    # GET
    return render_template('edit_info.html', user=user)

@profile_bp.route('/api/account/info')
def api_account_info():
    uid = session.get('user_id')
    if not uid:
        return {'error': 'Unauthorized'}, 401
    user = User.query.get_or_404(uid)
    return {
        'username': user.username,
        'email': user.email,
        'nickname': user.nickname or 'Not set',
        'address': user.address or 'Not set',
        'avatar': url_for('profile_bp.get_avatar', user_id=user.id),
        'coins': user.coins or 0
    }


@profile_bp.route('/api/account/edit', methods=['POST'])
def api_account_edit():
    uid = session.get('user_id')
    if not uid:
        return {'error': 'Unauthorized'}, 401
    user = User.query.get_or_404(uid)

    # update nickname and address
    nickname = request.form.get('nickname')
    address = request.form.get('address')
    user.nickname = nickname or user.nickname
    user.address = address or user.address


    # update avatar and make it be binary
    file = request.files.get('avatar')
    if file and allowed_file(file.filename):
        avatar_data = file.read()
        user.avatar = avatar_data
        user.avatar_mimetype = file.mimetype
    try:
        db.session.commit()
        return {'success': True}
    except Exception as e:
        print(f"Database commit failed: {e}")
        return {'error': 'Failed to update user information'}, 500
    
@profile_bp.route('/account/avatar/<int:user_id>')
def get_avatar(user_id):
    user = User.query.get_or_404(user_id)
    if not user.avatar:
        return redirect(url_for('static', filename='uploads/default.jpg')) # default avatar
    return current_app.response_class(user.avatar, mimetype=user.avatar_mimetype)