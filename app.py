"""
Flask application with authentication.
"""

from flask import Flask, jsonify, make_response, render_template, request, redirect, url_for, session
from flask_cors import CORS
from flask_oauthlib.client import OAuth
from models import db, User
import os
import logging
import sys
from urllib.parse import quote_plus

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Initialize Flask app
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
logger.info(f'Template directory: {template_dir}')
logger.info(f'Template directory exists: {os.path.exists(template_dir)}')
logger.info(f'Template directory contents: {os.listdir(template_dir) if os.path.exists(template_dir) else "directory not found"}')

app = Flask(__name__, template_folder=template_dir)
CORS(app)

# Set secret key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')

# Configure PostgreSQL database
postgres_host = os.environ.get('PGHOST', 'localhost')
postgres_port = os.environ.get('PGPORT', '5432')
postgres_db = os.environ.get('PGDATABASE', 'railway')
postgres_user = os.environ.get('PGUSER', 'postgres')
postgres_password = quote_plus(os.environ.get('PGPASSWORD', ''))

database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize OAuth
oauth = OAuth(app)
github = oauth.remote_app(
    'github',
    consumer_key=os.environ.get('GITHUB_CLIENT_ID'),
    consumer_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

# Create tables
with app.app_context():
    try:
        db.create_all()
        logger.info('Database tables created successfully')
    except Exception as e:
        logger.error(f'Error creating database tables: {str(e)}')

@app.route('/')
def root():
    logger.info('Handling request to /')
    return render_template('index.html')

@app.route('/register')
def register_page():
    logger.info('Handling request to /register')
    return render_template('register.html')

@app.route('/login/github')
def github_login():
    logger.info('Initiating GitHub login')
    return github.authorize(callback=url_for('github_authorized', _external=True))

@app.route('/login/github/authorized')
def github_authorized():
    logger.info('Handling GitHub authorization callback')
    resp = github.authorized_response()
    if resp is None or resp.get('access_token') is None:
        logger.warning('GitHub authorization failed')
        return redirect(url_for('root', error='GitHub authorization failed'))

    session['github_token'] = (resp['access_token'], '')
    
    # Get user info from GitHub
    github_user = github.get('user').data
    github_emails = github.get('user/emails').data
    primary_email = next(email['email'] for email in github_emails if email['primary'])

    # Check if user exists
    user = User.query.filter_by(github_id=github_user['id']).first()
    if not user:
        # Create new user
        username = github_user['login']
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            username=username,
            email=primary_email,
            github_id=github_user['id'],
            github_username=github_user['login'],
            github_access_token=resp['access_token']
        )
        db.session.add(user)
        db.session.commit()
        logger.info(f'Created new user from GitHub: {username}')
    else:
        # Update existing user
        user.github_access_token = resp['access_token']
        db.session.commit()
        logger.info(f'Updated existing GitHub user: {user.username}')

    return redirect(url_for('root', message='Successfully signed in with GitHub'))

@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')

@app.route('/api/register', methods=['POST'])
def register():
    logger.info('Handling registration request')
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    try:
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        logger.info(f'User {data["username"]} registered successfully')
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        logger.error(f'Error during registration: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    logger.info('Handling login request')
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing username or password'}), 400
    
    try:
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            logger.info(f'User {data["username"]} logged in successfully')
            return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
        
        logger.warning(f'Failed login attempt for user {data["username"]}')
        return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        logger.error(f'Error during login: {str(e)}')
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api')
def api_root():
    logger.info('Handling request to /api')
    response = make_response(jsonify({
        'message': 'Welcome to the API',
        'status': 'running'
    }))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/health')
def health():
    """Simple health check endpoint"""
    logger.info('Handling health check request')
    return jsonify({
        'status': 'healthy',
        'message': 'Flask application is running'
    }), 200

@app.route('/healthcheck')
def healthcheck():
    """Simple health check endpoint"""
    logger.info('Handling health check request')
    return jsonify({
        'status': 'healthy',
        'message': 'Flask application is running'
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
