"""
Health check module for Railway deployment.

Required for Railway's health check system. For configuration details, see:
- /rolodexters/rolodextervs/tasks/in_progress/railway_deployment.md
- /rolodexters/rolodextervs/memories/railway_deployment_config.md
"""

from flask import current_app, jsonify
from sqlalchemy import text
from redis.exceptions import RedisError

def check_database():
    """
    Check if database is accessible.
    
    Uses connection pooling settings from deployment config.
    """
    try:
        # Get database connection from SQLAlchemy
        db = current_app.extensions['sqlalchemy'].db
        # Execute a simple query
        with db.engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        return True
    except Exception as e:
        current_app.logger.error(f"Database health check failed: {str(e)}")
        return False

def check_redis():
    """
    Check if Redis is accessible.
    
    Uses connection settings from deployment config.
    """
    try:
        # Get Redis client
        redis_client = current_app.extensions['redis'].redis_client
        # Execute a simple ping
        redis_client.ping()
        return True
    except (RedisError, AttributeError) as e:
        current_app.logger.error(f"Redis health check failed: {str(e)}")
        return False

def health_check():
    """
    Comprehensive health check endpoint.
    
    Required by Railway for deployment validation.
    See /rolodexters/rolodextervs/tasks/in_progress/railway_deployment.md
    """
    db_healthy = check_database()
    redis_healthy = check_redis()
    
    status = 'healthy' if db_healthy and redis_healthy else 'unhealthy'
    http_status = 200 if status == 'healthy' else 503
    
    response = {
        'status': status,
        'database': 'up' if db_healthy else 'down',
        'redis': 'up' if redis_healthy else 'down',
    }
    
    return jsonify(response), http_status
