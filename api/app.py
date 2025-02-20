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
    level=logging.DEBUG,
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
        response = make_response(jsonify({'message': 'Welcome to the API'}))
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
        port = int(os.environ.get('PORT', 3000))
        logger.info(f'Starting Flask app on port {port}')
        app.run(host='0.0.0.0', port=port, debug=True)

except Exception as e:
    logger.error(f'Error during app initialization: {str(e)}', exc_info=True)
