import os

# Default values from Railway Redis service
DEFAULT_REDIS_HOST = 'redis.railway.internal'
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_USER = 'default'
DEFAULT_REDIS_PASSWORD = 'aXYyjnAjWnEPOgmGIWefwmqRGOhlImDZ'  # Default Railway password
DEFAULT_REDIS_URL = 'redis://default:aXYyjnAjWnEPOgmGIWefwmqRGOhlImDZ@redis.railway.internal:6379'
DEFAULT_REDIS_PUBLIC_URL = None  # Will be set by environment variable

# Redis persistence settings
REDIS_AOF_ENABLED = os.environ.get('REDIS_AOF_ENABLED', 'no').lower() == 'yes'
REDIS_RDB_POLICY = os.environ.get('REDIS_RDB_POLICY', '3600#1 300#100 60#10000')

REDIS_CONFIG = {
    'host': os.environ.get('REDIS_HOST', DEFAULT_REDIS_HOST),
    'port': int(os.environ.get('REDIS_PORT', DEFAULT_REDIS_PORT)),
    'password': os.environ.get('REDIS_PASSWORD', DEFAULT_REDIS_PASSWORD),
    'username': os.environ.get('REDIS_USERNAME', DEFAULT_REDIS_USER),
    'db': int(os.environ.get('REDIS_DB', 0)),
    'ssl': os.environ.get('REDIS_USE_SSL', 'true').lower() == 'true',
    'ssl_cert_reqs': None  # Don't verify SSL certificate
}

# Connection URLs
REDIS_URL = os.environ.get('REDIS_URL', DEFAULT_REDIS_URL)  # Internal URL
REDIS_PUBLIC_URL = os.environ.get('REDIS_PUBLIC_URL', DEFAULT_REDIS_PUBLIC_URL)  # External URL
