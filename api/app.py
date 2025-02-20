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

def is_db_command():
    if len(sys.argv) > 1 and sys.argv[0].endswith("flask") and sys.argv[1] == "db":
        return True
    return False

# create app
if is_db_command():
    from app_factory import create_migrations_app
    app = create_migrations_app()
else:
    try:
        # Gevent configuration as specified in deployment task
        if (flask_debug := os.environ.get("FLASK_DEBUG", "0")) and flask_debug.lower() in {"false", "0", "no"}:
            logger.info("Initializing gevent patches...")
            from gevent import monkey  # type: ignore
            # gevent
            monkey.patch_all()

            from grpc.experimental import gevent as grpc_gevent  # type: ignore
            # grpc gevent
            grpc_gevent.init_gevent()

            import psycogreen.gevent  # type: ignore
            psycogreen.gevent.patch_psycopg()
            logger.info("Gevent patches applied successfully")

        logger.info("Creating Flask application...")
        from app_factory import create_app
        from health import health_check

        app = create_app()
        celery = app.extensions["celery"]
        logger.info("Flask application created successfully")

        # Health check endpoint required by Railway deployment
        # See /rolodexters/rolodextervs/tasks/in_progress/railway_deployment.md
        app.route('/health')(health_check)
        logger.info("Health check endpoint registered")

    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask application on port {port}")
    app.run(host="0.0.0.0", port=port)
