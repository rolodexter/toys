"""
Flask application with health check endpoint
"""
from flask import Flask, jsonify
import logging
import sys
import os

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
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        logger.info('Health check request received')
        try:
            response = jsonify({'status': 'healthy'})
            logger.info('Sending health check response: %s', response.get_data(as_text=True))
            return response, 200
        except Exception as e:
            logger.error('Error in health check: %s', str(e), exc_info=True)
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/')
    def home():
        """Home page endpoint"""
        logger.info('Home page request received')
        return 'Hello World!'

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    logger.info('Starting Flask application')
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
