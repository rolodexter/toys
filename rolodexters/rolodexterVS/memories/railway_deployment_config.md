# Railway Deployment Configuration Memory

## Project Structure
- Project Name: toys
- Environment: production
- GitHub Repository: rolodexter/toys

## Services
1. Main Application (toys)
   - Serverless deployment
   - Health check: /health
   - Timeout: 300s
   - Replicas: 1

2. PostgreSQL (toys-postgres)
   - Internal access via shared variables
   - Connection pooling settings:
     ```python
     SQLALCHEMY_ENGINE_OPTIONS = {
         'pool_size': 10,
         'max_overflow': 20,
         'pool_recycle': 300,
         'pool_pre_ping': True,
         'connect_args': {
             'connect_timeout': 10,
             'application_name': 'toys-app'
         }
     }
     ```

3. Redis (toys-redis)
   - Internal access via shared variables
   - SSL enabled
   - Connection settings:
     ```python
     REDIS_CONFIG = {
         'socket_timeout': 5,
         'socket_connect_timeout': 5,
         'retry_on_timeout': True,
         'health_check_interval': 30,
         'max_connections': 10,
         'decode_responses': True
     }
     ```

## Shared Variables
1. Database Variables:
   ```
   DATABASE_URL
   DATABASE_PUBLIC_URL
   PGHOST
   PGPORT
   PGDATABASE
   PGUSER
   PGPASSWORD
   POSTGRES_DB
   POSTGRES_USER
   POSTGRES_PASSWORD
   ```

2. Redis Variables:
   ```
   REDIS_URL
   REDIS_PUBLIC_URL
   REDISHOST
   REDISPORT
   REDISUSER
   REDISPASSWORD
   REDIS_AOF_ENABLED
   REDIS_RDB_POLICY
   ```

3. Railway System Variables:
   ```
   RAILWAY_PROJECT_ID
   RAILWAY_ENVIRONMENT_ID
   RAILWAY_SERVICE_ID
   RAILWAY_SERVICE_NAME
   RAILWAY_PROJECT_NAME
   RAILWAY_ENVIRONMENT_NAME
   RAILWAY_PRIVATE_DOMAIN
   RAILWAY_RUN_AS_ROOT
   RAILWAY_RUN_UID
   ```

## Startup Configuration
1. Process Management:
   ```bash
   # Start Next.js
   cd /app && node server.js

   # Start Flask
   cd /app/api && gunicorn app:app --bind 0.0.0.0:$PORT --worker-class gevent
   ```

2. Health Check Logic:
   - Check database connection
   - Check Redis connection
   - Return detailed status
   - Log connection issues

## Logging Configuration
1. Flask Logging:
   ```python
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
   ```

2. Start Script Logging:
   - Process status monitoring
   - File existence checks
   - Environment variable logging
   - Error handling with set -e

## Important Notes
- All services use Railway's internal network
- SSL is required for Redis connections
- PostgreSQL uses connection pooling
- Health checks must pass for deployment
- Logging is configured for debugging
- Variables are shared across services

## User Preferences
- User: Joe Maristela
- Region: US West
- GitHub Integration: Enabled
- Auto-deploy: Enabled on main branch
- Logging: Detailed for debugging
