"""
Flask application with authentication.
"""

import os
import logging
import sys
from flask import Flask, jsonify, make_response
from flask_cors import CORS

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

try:
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app)
    logger.info('Flask app initialized')

    # Root endpoint
    @app.route('/')
    def root():
        logger.info('Handling request to /')
        response = make_response(jsonify({
            'message': 'Welcome to the API',
            'status': 'running'
        }))
        response.headers['Content-Type'] = 'application/json'
        return response

    # Health check endpoint - must be first route
    @app.route('/health')
    def health():
        logger.info('Handling health check request')
        response = make_response(jsonify({'status': 'ok'}))
        response.headers['Content-Type'] = 'application/json'
        return response

    if __name__ == '__main__':
        # Railway uses port 8080 internally
        port = int(os.environ.get('PORT', 8080))
        logger.info(f'Starting Flask app on port {port}')
        app.run(host='0.0.0.0', port=port)

except Exception as e:
    logger.error(f'Error during app initialization: {str(e)}', exc_info=True)
