# Railway Deployment Configuration Memory

## Project Structure
- Project Name: toys
- Environment: production
- GitHub Repository: rolodexter/toys

## Services
1. Main Application (toys)
   ```
   RAILWAY_PROJECT_ID=fe07eb00-ce47-4841-8f75-45a2d9018d4e
   RAILWAY_ENVIRONMENT_ID=60693e13-f5c6-4879-bf31-dc01224d8753
   RAILWAY_SERVICE_ID=4c91f505-14a4-4aaf-8922-103ca1e469b4
   ```

2. PostgreSQL (toys-postgres)
   ```
   DATABASE_URL=postgresql://postgres:cxwhLFWdYNokjpnBUdiNqfYKKdfvtxaI@postgres.railway.internal:5432/railway
   PGHOST=postgres.railway.internal
   PGPORT=5432
   PGDATABASE=railway
   PGUSER=postgres
   ```

3. Redis (toys-redis)
   ```
   REDIS_URL=redis://default:aXYyjnAjWnEPOgmGIWefwmqRGOhlImDZ@redis.railway.internal:6379
   REDISHOST=redis.railway.internal
   REDISPORT=6379
   REDISUSER=default
   ```

## Important Configuration Files
1. railway.toml - Main deployment configuration
2. Dockerfile - Build configuration
3. configs/database.py - Database settings
4. configs/redis.py - Redis settings
5. configs/app_config.py - Application settings

## Deployment Settings
- Serverless: Enabled
- Health Check: /health
- Timeout: 300s
- Replicas: 1
- Region: US West (California)

## Notes
- All services use Railway's internal network for communication
- SSL is enabled for Redis connections
- PostgreSQL uses connection pooling
- Environment variables are properly referenced between services

## User Preferences
- User: Joe Maristela
- Preferred Region: US West
- GitHub Integration: Enabled
- Auto-deploy: Enabled on main branch
