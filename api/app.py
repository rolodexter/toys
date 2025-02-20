"""
Flask application with authentication.
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Root endpoint
@app.route('/')
def root():
    logger.info('Handling request to /')
    return jsonify({'message': 'Welcome to the API'})

# Health check endpoint - must be first route
@app.route('/health')
def health():
    logger.info('Handling health check request')
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    logger.info(f'Starting Flask app on port {port}')
    app.run(host='0.0.0.0', port=port)
