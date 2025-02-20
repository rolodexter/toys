"""
Redis configuration for Railway deployment.

For detailed configuration and deployment information, see:
- /rolodexters/rolodextervs/tasks/in_progress/railway_deployment.md
- /rolodexters/rolodextervs/memories/railway_deployment_config.md
"""

import os

# Default values for Railway Redis service
# See /rolodexters/rolodextervs/memories/railway_deployment_config.md for details
DEFAULT_REDIS_HOST = 'redis.railway.internal'
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_DB = 0
DEFAULT_REDIS_SSL = True

# Get Redis configuration from environment variables
# Support both naming conventions as documented in deployment task
REDIS_HOST = os.environ.get('REDIS_HOST') or os.environ.get('REDISHOST', DEFAULT_REDIS_HOST)
REDIS_PORT = int(os.environ.get('REDIS_PORT') or os.environ.get('REDISPORT', DEFAULT_REDIS_PORT))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD') or os.environ.get('REDISPASSWORD')
REDIS_USER = os.environ.get('REDIS_USER') or os.environ.get('REDISUSER', 'default')
REDIS_DB = int(os.environ.get('REDIS_DB', DEFAULT_REDIS_DB))
REDIS_USE_SSL = os.environ.get('REDIS_USE_SSL', str(DEFAULT_REDIS_SSL)).lower() in ('true', '1', 'yes')

# Get Redis URL from environment or construct it
REDIS_URL = os.environ.get('REDIS_URL')
if not REDIS_URL:
    # Construct Redis URL if not provided
    auth_part = f'{REDIS_USER}:{REDIS_PASSWORD}@' if REDIS_PASSWORD else ''
    scheme = 'rediss' if REDIS_USE_SSL else 'redis'
    REDIS_URL = f'{scheme}://{auth_part}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Redis client configuration
# Connection settings as specified in /rolodexters/rolodextervs/memories/railway_deployment_config.md
REDIS_CONFIG = {
    'url': REDIS_URL,
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'username': REDIS_USER,
    'password': REDIS_PASSWORD,
    'db': REDIS_DB,
    'ssl': REDIS_USE_SSL,
    'socket_timeout': 5,  # seconds
    'socket_connect_timeout': 5,  # seconds
    'retry_on_timeout': True,
    'health_check_interval': 30,  # seconds
    'max_connections': 10,
    'decode_responses': True  # Automatically decode response to str instead of bytes
}
