"""
Flask application for Rolodexter
"""
from flask import Flask, jsonify, render_template_string, request
from sqlalchemy import text
import logging
import sys
import os
from models import db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Main interface template
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Rolodexter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        .header {
            background: #24292e;
            color: white;
            padding: 1rem;
            text-align: center;
        }
        .container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 1rem;
        }
        .chat-container {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .input-container {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        textarea {
            flex-grow: 1;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            min-height: 60px;
            font-family: inherit;
        }
        button {
            padding: 0.5rem 1rem;
            background: #2ea44f;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #2c974b;
        }
        .message {
            margin: 1rem 0;
            padding: 1rem;
            border-radius: 4px;
        }
        .user-message {
            background: #f0f0f0;
        }
        .assistant-message {
            background: #e3f2fd;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Rolodexter</h1>
    </div>
    <div class="container">
        <div class="chat-container">
            <div id="chat-messages">
                <!-- Messages will appear here -->
            </div>
            <div class="input-container">
                <textarea id="user-input" placeholder="Type your message here..."></textarea>
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, 'user');
            input.value = '';

            // TODO: Send to backend and get response
            // For now, just echo back
            setTimeout(() => {
                addMessage('I received your message: ' + message, 'assistant');
            }, 500);
        }

        function addMessage(text, sender) {
            const messages = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = `message ${sender}-message`;
            div.textContent = text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>
"""

def create_app():
    """Create and configure the Flask application"""
    logger.info('Creating Flask application')
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    
    # Configure database URL
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    logger.info('Using database URL: %s', database_url.split('@')[0] + '@' + database_url.split('@')[1] if '@' in database_url else 'sqlite database')
    
    logger.info('Initializing database')
    db.init_app(app)

    @app.route('/')
    def home():
        """Home page endpoint - shows the main interface"""
        logger.info('Home page request received')
        return render_template_string(MAIN_TEMPLATE)

    @app.route('/health')
    def health():
        """Health check endpoint"""
        logger.info('Health check request received')
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
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
