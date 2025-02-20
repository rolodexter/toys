"""
Flask application for Rolodexter
"""
from flask import Flask, jsonify, render_template_string, request
from sqlalchemy import text
import logging
import sys
import os
from models import db

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Rolodexter</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .chat-container {
            height: calc(100vh - 140px);
        }
        .message {
            max-width: 85%;
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 0.5rem;
            line-height: 1.5;
        }
        .user-message {
            background-color: #f3f4f6;
            margin-left: auto;
        }
        .assistant-message {
            background-color: #e5e7eb;
            margin-right: auto;
        }
        .typing-indicator::after {
            content: '...';
            animation: typing 1s infinite;
        }
        @keyframes typing {
            0% { content: ''; }
            25% { content: '.'; }
            50% { content: '..'; }
            75% { content: '...'; }
        }
    </style>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex">
                    <div class="flex-shrink-0 flex items-center">
                        <h1 class="text-xl font-bold">Rolodexter</h1>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
            <div class="bg-white shadow rounded-lg">
                <div id="chat-messages" class="chat-container overflow-y-auto p-4">
                    <!-- Messages will appear here -->
                </div>
                <div class="border-t p-4">
                    <div class="flex space-x-4">
                        <textarea 
                            id="user-input"
                            class="flex-1 border rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Send a message..."
                            rows="3"
                        ></textarea>
                        <button 
                            onclick="sendMessage()"
                            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            Send
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        const chatMessages = document.getElementById('chat-messages');
        const userInput = document.getElementById('user-input');

        function addMessage(content, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            
            // Create message content
            const textDiv = document.createElement('div');
            textDiv.className = 'whitespace-pre-wrap';
            textDiv.textContent = content;
            messageDiv.appendChild(textDiv);
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function addTypingIndicator() {
            const indicator = document.createElement('div');
            indicator.className = 'message assistant-message typing-indicator';
            indicator.textContent = 'Thinking';
            chatMessages.appendChild(indicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return indicator;
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            // Clear input
            userInput.value = '';

            // Add user message
            addMessage(message, 'user');

            // Add typing indicator
            const indicator = addTypingIndicator();

            try {
                // Send to backend
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message })
                });

                const data = await response.json();
                
                // Remove typing indicator
                indicator.remove();

                // Add assistant response
                addMessage(data.response, 'assistant');
            } catch (error) {
                console.error('Error:', error);
                indicator.remove();
                addMessage('Sorry, there was an error processing your request.', 'assistant');
            }
        }

        // Handle Enter key
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
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

    @app.route('/api/chat', methods=['POST'])
    def chat():
        """Chat API endpoint"""
        data = request.json
        message = data.get('message', '')
        
        # For now, just echo back
        response = f"I received your message: {message}"
        
        return jsonify({
            'response': response
        })

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
