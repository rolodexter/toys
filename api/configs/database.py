import os

# Default Railway PostgreSQL values
DEFAULT_DB_URL = 'postgresql://postgres:cxwhLFWdYNokjpnBUdiNqfYKKdfvtxaI@postgres.railway.internal:5432/railway'
DEFAULT_DB_HOST = 'postgres.railway.internal'
DEFAULT_DB_PORT = 5432
DEFAULT_DB_NAME = 'railway'
DEFAULT_DB_USER = 'postgres'
DEFAULT_DB_PASSWORD = 'cxwhLFWdYNokjpnBUdiNqfYKKdfvtxaI'

# Get database URL from environment or use default
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

# SQLAlchemy configuration
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_recycle': 300,
    'pool_pre_ping': True,  # Enable connection pool pre-ping
    'connect_args': {
        'connect_timeout': 10,  # Connection timeout in seconds
        'application_name': 'toys-app'  # Identify your application in pg_stat_activity
    }
}
