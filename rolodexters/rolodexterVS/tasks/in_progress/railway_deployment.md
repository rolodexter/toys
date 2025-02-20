# Railway Deployment Task

## Overview
Configuring and deploying the application on Railway.app with PostgreSQL and Redis services.

## User
Joe Maristela

## Status
In Progress

## Services Setup
1. Main Application Service (toys)
   - Connected to GitHub repo: rolodexter/toys
   - Branch: main
   - Using Dockerfile for build
   - Serverless deployment enabled
   - Health check path: /health

2. PostgreSQL Service (toys-postgres)
   - Internal URL: postgresql://postgres:cxwhLFWdYNokjpnBUdiNqfYKKdfvtxaI@postgres.railway.internal:5432/railway
   - Host: postgres.railway.internal
   - Port: 5432
   - Database: railway
   - User: postgres

3. Redis Service (toys-redis)
   - Internal URL: redis://default:aXYyjnAjWnEPOgmGIWefwmqRGOhlImDZ@redis.railway.internal:6379
   - Host: redis.railway.internal
   - Port: 6379
   - Username: default

## Configuration Files
1. railway.toml
   - Build and deployment settings
   - Environment variables
   - Service connections

2. Dockerfile
   - Multi-stage build (Node.js and Python)
   - PostgreSQL development dependencies
   - Redis support

3. Flask Configurations
   - Database config (configs/database.py)
   - Redis config (configs/redis.py)
   - App config (configs/app_config.py)

## Next Steps
1. Monitor deployment logs
2. Test database connections
3. Test Redis connections
4. Set up health checks
5. Configure auto-scaling rules

## Notes
- Using Railway's internal network for service communication
- SSL enabled for Redis connections
- Connection pooling configured for PostgreSQL
- Environment variables properly referenced between services
