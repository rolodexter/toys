"""
Flask application with authentication.
"""

from flask import Flask, jsonify, make_response, render_template, request
from flask_cors import CORS
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

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
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

    # Create tables
    with app.app_context():
        try:
            db.create_all()
            logger.info('Database tables created successfully')
        except Exception as e:
            logger.error(f'Error creating database tables: {str(e)}')
            # Don't fail on database error, let health check handle it
            pass

    logger.info('Flask app initialized with database')

    # Root endpoint
    @app.route('/')
    def root():
        logger.info('Handling request to /')
        return render_template('index.html')

    # Registration endpoint
    @app.route('/register')
    def register_page():
        logger.info('Handling request to /register')
        return render_template('register.html')

    # API endpoint for registration
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

    # API endpoint for login
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

    # API endpoint
    @app.route('/api')
    def api_root():
        logger.info('Handling request to /api')
        response = make_response(jsonify({
            'message': 'Welcome to the API',
            'status': 'running'
        }))
        response.headers['Content-Type'] = 'application/json'
        return response

    # Health check endpoint
    @app.route('/health')
    def health():
        logger.info('Handling health check request')
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            db.session.commit()
            status = 'ok'
        except Exception as e:
            logger.error(f'Database health check failed: {str(e)}')
            status = 'error'
        
        response = make_response(jsonify({
            'status': status,
            'database': status
        }))
        response.headers['Content-Type'] = 'application/json'
        return response

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f'Starting Flask app on port {port}')
    app.run(host='0.0.0.0', port=port)
