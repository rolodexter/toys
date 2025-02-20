"""
Main Flask application entry point.

For deployment configuration details, see:
- /rolodexters/rolodextervs/tasks/in_progress/railway_deployment.md
- /rolodexters/rolodextervs/memories/railway_deployment_config.md
"""

import os
import sys
import logging
from logging.config import dictConfig

# Configure logging as specified in /rolodexters/rolodextervs/memories/railway_deployment_config.md
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

logger = logging.getLogger(__name__)

# Log environment information
logger.info("Starting Flask application...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Environment variables:")
for key in ['PORT', 'FLASK_APP', 'FLASK_ENV', 'DATABASE_URL', 'REDIS_URL']:
    value = os.environ.get(key, 'Not set')
    if key in ['DATABASE_URL', 'REDIS_URL']:
        # Mask sensitive information
        value = value[:10] + '...' if value != 'Not set' else value
    logger.info(f"  {key}: {value}")

from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask application on port {port}")
    app.run(host="0.0.0.0", port=port)
