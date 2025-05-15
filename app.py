from flask import Flask, render_template, session, redirect
from flask_wtf.csrf import CSRFProtect
from models import db
import os

# Import blueprints
from auth import auth_bp
from record import record_bp, log_cardio  # Import log_cardio for CSRF exemption
from social import social_bp

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
# Secret key for session and CSRF. Use environment or generate random
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
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

# Exempt the log_cardio route from CSRF protection
csrf.exempt(log_cardio)

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
