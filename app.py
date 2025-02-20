from flask import Flask, jsonify
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health')
def health():
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
    logger.info('Home page request received')
    return 'Hello World!'

if __name__ == '__main__':
    logger.info('Starting Flask application')
    app.run(host='0.0.0.0', port=8080)
