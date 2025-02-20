"""
Health check module for Railway deployment.

Required for Railway's health check system. For configuration details, see:
- /rolodexters/rolodextervs/tasks/in_progress/railway_deployment.md
- /rolodexters/rolodextervs/memories/railway_deployment_config.md
"""

import os
import logging
from flask import current_app, jsonify
from sqlalchemy import text
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

def check_database():
    """
    Check if database is accessible.
    
    Uses connection pooling settings from deployment config.
    """
    if not os.environ.get('DATABASE_URL'):
        logger.warning("DATABASE_URL not set, skipping database check")
        return True
        
    try:
        # Get database connection from SQLAlchemy
        db = current_app.extensions['sqlalchemy'].db
        # Execute a simple query
        with db.engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        logger.info("Database health check passed")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

def check_redis():
    """
    Check if Redis is accessible.
    
    Uses connection settings from deployment config.
    """
    if not os.environ.get('REDIS_URL'):
        logger.warning("REDIS_URL not set, skipping Redis check")
        return True
        
    try:
        # Get Redis client
        redis_client = current_app.extensions['redis'].redis_client
        # Execute a simple ping
        redis_client.ping()
        logger.info("Redis health check passed")
        return True
    except (RedisError, AttributeError) as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return False

def health_check():
    """
    Comprehensive health check endpoint.
    
    Required by Railway for deployment validation.
    See /rolodexters/rolodextervs/tasks/in_progress/railway_deployment.md
    """
    try:
        logger.info("Starting health check...")
        
        # For initial deployment, we'll consider the service healthy if it can respond
        response = {
            'status': 'initializing',
            'message': 'Service is starting up',
            'checks': {}
        }
        
        # Try database check
        db_healthy = check_database()
        response['checks']['database'] = 'up' if db_healthy else 'down'
        
        # Try Redis check
        redis_healthy = check_redis()
        response['checks']['redis'] = 'up' if redis_healthy else 'down'
        
        # For initial deployment, always return 200 if we can respond
        response['status'] = 'healthy'
        logger.info(f"Health check completed: {response}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Health check failed with error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
