from flask import Flask
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route('/health')
def health():
    logger.info('Health check endpoint called')
    return {'status': 'ok'}

@app.route('/')
def home():
    logger.info('Home endpoint called')
    return 'Hello from Flask!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
