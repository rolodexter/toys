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
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        .button {
            display: inline-block;
            padding: 10px 20px;
            background-color: #2ea44f;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 10px;
        }
        .button:hover {
            background-color: #2c974b;
        }
    </style>
</head>
<body>
    <h1>Welcome to Rolodexter</h1>
    {% if current_user.is_authenticated %}
        <p>Hello, {{ current_user.username }}!</p>
        <a href="{{ url_for('logout') }}" class="button">Logout</a>
    {% else %}
        <p>Please log in to continue.</p>
        <a href="{{ url_for('login') }}" class="button">Login</a>
    {% endif %}
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Rolodexter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        .form-group {
            margin: 15px 0;
        }
        input[type="text"], input[type="password"] {
            padding: 8px;
            width: 200px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .login-button {
            display: inline-block;
            padding: 10px 20px;
            background-color: #2ea44f;
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 6px;
            margin: 10px;
            cursor: pointer;
        }
        .login-button:hover {
            background-color: #2c974b;
        }
        .back-button {
            display: inline-block;
            padding: 10px 20px;
            background-color: #6e7681;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 10px;
        }
        .back-button:hover {
            background-color: #7d8590;
        }
        .error {
            color: #dc3545;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>Login to Rolodexter</h1>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <div class="error">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="POST" action="{{ url_for('login') }}">
        <div class="form-group">
            <input type="text" name="username" placeholder="Username" required>
        </div>
        <div class="form-group">
            <input type="password" name="password" placeholder="Password" required>
        </div>
        <div class="form-group">
            <button type="submit" class="login-button">Login</button>
        </div>
    </form>
    <a href="{{ url_for('home') }}" class="back-button">Back to Home</a>
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

    # Get the deployment URL from Railway
    deployment_url = os.environ.get('RAILWAY_STATIC_URL', 'http://localhost:8080')
    logger.info('Using deployment URL: %s', deployment_url)
    
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

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page endpoint"""
        logger.info('Login page request received')
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            logger.info('Login attempt for username: %s', username)
            logger.info('Password length: %d', len(password))
            
            user = User.query.filter_by(username=username).first()
            
            if user:
                logger.info('User found in database: %s', user)
                logger.info('User password hash: %s', user.password_hash)
                if user.check_password(password):
                    logger.info('Password check successful')
                    login_user(user)
                    flash('Logged in successfully.')
                    return redirect(url_for('home'))
                else:
                    logger.warning('Invalid password for user: %s', username)
            else:
                logger.warning('User not found: %s', username)
            
            flash('Invalid username or password')
            return render_template_string(LOGIN_TEMPLATE)
        
        return render_template_string(LOGIN_TEMPLATE)

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
            # Always use HTTPS for the callback URL in production
            redirect_uri = url_for('github_authorized', _external=True, _scheme='https')
            # Log the full URL for debugging
            logger.info('Full application URL: %s', request.url)
            logger.info('Generated redirect URI: %s', redirect_uri)
            logger.info('GitHub client ID: %s', os.environ.get('GITHUB_CLIENT_ID', 'Not set'))
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

    @app.route('/setup')
    def setup():
        """One-time setup route to create test user"""
        try:
            username = "rolodexter"
            password = "asdfasdf"
            
            # Check if user already exists
            user = User.query.filter_by(username=username).first()
            if user:
                logger.info('Setup: User %s already exists, updating password', username)
                logger.info('Old password hash: %s', user.password_hash)
                user.set_password(password)
                logger.info('New password hash: %s', user.password_hash)
                db.session.commit()
                return jsonify({'message': f'Updated password for user {username}'})
            
            # Create new user
            logger.info('Setup: Creating new user %s', username)
            user = User(username=username)
            user.set_password(password)
            logger.info('Initial password hash: %s', user.password_hash)
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'message': f'Created user {username}'})
        except Exception as e:
            logger.error('Error in setup: %s', str(e), exc_info=True)
            return jsonify({'error': str(e)}), 500

    @app.route('/reset')
    def reset():
        """Reset the database"""
        try:
            logger.info('Dropping all tables')
            db.drop_all()
            logger.info('Creating all tables')
            db.create_all()
            return jsonify({'message': 'Database reset successful'})
        except Exception as e:
            logger.error('Error resetting database: %s', str(e), exc_info=True)
            return jsonify({'error': str(e)}), 500

    @app.route('/health')
    def health():
        """Health check endpoint"""
        logger.info('Health check request received')
        try:
            # Test database connection using SQLAlchemy 2.0 syntax
            db.session.execute(text('SELECT 1'))
            
            # Check if test user exists
            user = User.query.filter_by(username='rolodexter').first()
            user_status = {
                'exists': user is not None,
                'has_password': user.password_hash is not None if user else False
            }
            
            response = jsonify({
                'success': True,
                'message': 'Service is healthy',
                'version': '1.0.0',
                'user_status': user_status
            })
            logger.info('Sending health check response: %s', response.get_data(as_text=True))
            return response, 200
        except Exception as e:
            logger.error('Error in health check: %s', str(e), exc_info=True)
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/check-user')
    def check_user():
        """Check if test user exists"""
        try:
            username = "rolodexter"
            user = User.query.filter_by(username=username).first()
            if user:
                return jsonify({
                    'exists': True,
                    'username': user.username,
                    'created_at': user.created_at.isoformat(),
                    'has_password': user.password_hash is not None
                })
            return jsonify({
                'exists': False,
                'message': 'User not found'
            })
        except Exception as e:
            logger.error('Error checking user: %s', str(e), exc_info=True)
            return jsonify({'error': str(e)}), 500

    @app.cli.command("create-user")
    def create_user():
        """Create a test user"""
        username = "rolodexter"
        password = "asdfasdf"
        
        # Check if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User {username} already exists")
            return
        
        # Create new user
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Created user {username}")

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
