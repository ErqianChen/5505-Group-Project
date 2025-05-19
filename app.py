from flask import Flask, render_template, session, redirect
from flask_wtf.csrf import CSRFProtect
from models import db
import os
from user_profile import profile_bp
from plan import plan_bp

# Import blueprints
from auth import auth_bp
from record import record_bp, log_cardio, log_strength
from social import social_bp

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
# Upload Configuration
BASEDIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASEDIR, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024    # 5 MB limited
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# Secret key for session and CSRF. Use environment or generate random
key_file = os.path.join(app.instance_path, 'secret_key.txt')
os.makedirs(app.instance_path, exist_ok=True)
if os.path.exists(key_file):
    with open(key_file, 'r') as f:
        secret_key = f.read().strip()
else:
    secret_key = os.urandom(24).hex()
    with open(key_file, 'w') as f:
        f.write(secret_key)

app.config['SECRET_KEY'] = secret_key
# SQLite database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(record_bp)
app.register_blueprint(social_bp)
# register the user_profile blueprint
app.register_blueprint(profile_bp)
# register the plan blueprint
app.register_blueprint(plan_bp)

@csrf.exempt  # Allow login page to render without CSRF token
@app.route('/')
def root():
    return redirect('/login_system/login.html', code=302)

def index():
    # If no user is logged in, show login page
    if not session.get('user_id'):
        return render_template('login_system/login.html')
    # Render main page, passing username for display
    return render_template('main.html', username=session.get('username'))

if __name__ == '__main__':
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
    # Run Flask app in debug mode on default port
    app.run(debug=True)

@app.route('/')
@app.route('/workout')
def workout():
    return render_template('workout.html')

@app.route('/record')
def record():
    return render_template('record.html')

@app.route('/social')
def social():
    return render_template('social.html')

@app.route('/account')
def account():
    return render_template('account.html')
