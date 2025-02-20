"""
Flask application with GitHub OAuth integration
"""
from flask import Flask, jsonify, redirect, url_for, flash, render_template_string, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from sqlalchemy import text
import logging
import sys
import os
from models import db, User

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Simple HTML template for testing
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Rolodexter</title>
</head>
<body>
    <h1>Welcome to Rolodexter</h1>
    {% if current_user.is_authenticated %}
        <p>Hello, {{ current_user.username }}!</p>
        <a href="{{ url_for('logout') }}">Logout</a>
    {% else %}
        <p>Please <a href="{{ url_for('login') }}">login</a> to continue.</p>
    {% endif %}
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Rolodexter</title>
</head>
<body>
    <h1>Login</h1>
    <a href="{{ url_for('github_login') }}">Login with GitHub</a>
    <br>
    <a href="{{ url_for('home') }}">Back to Home</a>
</body>
</html>
"""

def create_app():
    """Create and configure the Flask application"""
    logger.info('Creating Flask application')
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    
    # Configure database URL
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    # Replace postgres:// with postgresql:// for SQLAlchemy
    if database_url.startswith('postgres://'):
        logger.info('Converting postgres:// to postgresql:// in DATABASE_URL')
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    logger.info('Using database URL: %s', database_url.split('@')[0] + '@' + database_url.split('@')[1] if '@' in database_url else 'sqlite database')
    
    if not app.config['SECRET_KEY']:
        logger.error('SECRET_KEY not set in environment variables')
        raise ValueError('SECRET_KEY must be set')
    
    logger.info('Initializing database')
    db.init_app(app)
    
    logger.info('Initializing login manager')
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    logger.info('Setting up OAuth')
    oauth = OAuth(app)
    
    if not os.environ.get('GITHUB_CLIENT_ID') or not os.environ.get('GITHUB_CLIENT_SECRET'):
        logger.error('GitHub OAuth credentials not set')
        raise ValueError('GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set')
    
    github = oauth.register(
        name='github',
        client_id=os.environ.get('GITHUB_CLIENT_ID'),
        client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID"""
        logger.debug('Loading user: %s', user_id)
        return User.query.get(int(user_id))

    @app.route('/')
    def home():
        """Home page endpoint"""
        logger.info('Home page request received')
        try:
            return render_template_string(INDEX_TEMPLATE)
        except Exception as e:
            logger.error('Error rendering home page: %s', str(e), exc_info=True)
            return 'Internal Server Error', 500

    @app.route('/login')
    def login():
        """Login page endpoint"""
        logger.info('Login page request received')
        try:
            return render_template_string(LOGIN_TEMPLATE)
        except Exception as e:
            logger.error('Error rendering login page: %s', str(e), exc_info=True)
            return 'Internal Server Error', 500

    @app.route('/logout')
    @login_required
    def logout():
        """Logout endpoint"""
        logger.info('Logout request received')
        logout_user()
        return redirect(url_for('home'))

    @app.route('/login/github')
    def github_login():
        """Initiate GitHub OAuth flow"""
        logger.info('GitHub login request received')
        try:
            redirect_uri = url_for('github_authorized', _external=True)
            return github.authorize_redirect(redirect_uri)
        except Exception as e:
            logger.error('Error initiating GitHub OAuth: %s', str(e), exc_info=True)
            return 'Error connecting to GitHub', 500

    @app.route('/login/github/authorized')
    def github_authorized():
        """Handle GitHub OAuth callback"""
        logger.info('GitHub authorization callback received')
        try:
            token = github.authorize_access_token()
            if not token:
                logger.warning('GitHub authorization failed: No token received')
                flash('Access denied: No token received')
                return redirect(url_for('login'))

            resp = github.get('user', token=token)
            if not resp or resp.status_code != 200:
                logger.warning('Failed to get user info from GitHub')
                flash('Failed to get user info from GitHub')
                return redirect(url_for('login'))

            profile = resp.json()
            user = User.query.filter_by(github_id=profile['id']).first()
            if not user:
                logger.info('Creating new user from GitHub: %s', profile['login'])
                user = User(
                    username=profile['login'],
                    github_id=profile['id'],
                    github_login=profile['login'],
                    github_access_token=token['access_token']
                )
                if profile.get('email'):
                    user.email = profile['email']
                db.session.add(user)
                db.session.commit()

            login_user(user)
            flash('Successfully signed in with GitHub.')
            return redirect(url_for('home'))
        except Exception as e:
            logger.error('Error in GitHub authorization callback: %s', str(e), exc_info=True)
            return 'Error processing GitHub login', 500

    @app.route('/health')
    def health():
        """Health check endpoint"""
        logger.info('Health check request received')
        try:
            # Test database connection using SQLAlchemy 2.0 syntax
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            
            response = jsonify({
                'success': True,
                'message': 'Service is healthy',
                'version': '1.0.0'
            })
            logger.info('Sending health check response: %s', response.get_data(as_text=True))
            return response, 200
        except Exception as e:
            logger.error('Error in health check: %s', str(e), exc_info=True)
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    # Create database tables
    with app.app_context():
        logger.info('Creating database tables')
        try:
            db.create_all()
            logger.info('Database tables created successfully')
        except Exception as e:
            logger.error('Error creating database tables: %s', str(e), exc_info=True)
            raise

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    logger.info('Starting Flask application')
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
