"""
Flask application with GitHub OAuth integration
"""
from flask import Flask, jsonify, redirect, url_for, flash, render_template, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_oauthlib.client import OAuth
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

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Setup OAuth
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

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID"""
        return User.query.get(int(user_id))

    @app.route('/')
    def home():
        """Home page endpoint"""
        logger.info('Home page request received')
        return render_template('index.html')

    @app.route('/login')
    def login():
        """Login page endpoint"""
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        """Logout endpoint"""
        logout_user()
        return redirect(url_for('home'))

    @app.route('/login/github')
    def github_login():
        """Initiate GitHub OAuth flow"""
        return github.authorize(callback=url_for('github_authorized', _external=True))

    @app.route('/login/github/authorized')
    def github_authorized():
        """Handle GitHub OAuth callback"""
        resp = github.authorized_response()
        if resp is None or resp.get('access_token') is None:
            flash('Access denied: reason={} error={}'.format(
                request.args['error_reason'],
                request.args['error_description']
            ))
            return redirect(url_for('login'))

        session['github_token'] = (resp['access_token'], '')
        me = github.get('user')
        
        # Get or create user
        user = User.query.filter_by(github_id=me.data['id']).first()
        if not user:
            user = User(
                username=me.data['login'],
                github_id=me.data['id'],
                github_login=me.data['login'],
                github_access_token=resp['access_token']
            )
            if 'email' in me.data and me.data['email']:
                user.email = me.data['email']
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash('Successfully signed in with GitHub.')
        return redirect(url_for('home'))

    @github.tokengetter
    def get_github_oauth_token():
        """Get GitHub OAuth token from session"""
        return session.get('github_token')

    @app.route('/health')
    def health():
        """Health check endpoint"""
        logger.info('Health check request received')
        try:
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
        db.create_all()

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    logger.info('Starting Flask application')
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
