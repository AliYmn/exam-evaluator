# 🚀 Fly.io Deployment Guide

## Architecture

Our app will be deployed as:

1. **Backend** (FastAPI) - Single Fly App with multiple processes
   - Auth Service (port 8004)
   - Content Service (port 8001)
   - Celery Worker
   - Celery Beat

2. **Frontend** (Next.js) - Separate Fly App

3. **Databases** (Managed Services)
   - PostgreSQL: Fly Postgres
   - Redis: Fly Redis (Upstash Redis)
   - RabbitMQ: CloudAMQP

## Deployment Steps

### 1. Create PostgreSQL Database
```bash
flyctl postgres create --name exam-evaluator-db --region iad
```

### 2. Create Redis
```bash
flyctl redis create --name exam-evaluator-redis --region iad
```

### 3. Deploy Backend
```bash
cd backend
flyctl launch --name exam-evaluator-backend --region iad
flyctl secrets set \
  POSTGRES_DB=postgres \
  POSTGRES_USER=postgres \
  POSTGRES_PASSWORD=your-password \
  REDIS_HOST=your-redis-host \
  REDIS_PORT=6379 \
  RABBITMQ_HOST=your-rabbitmq-host \
  RABBITMQ_USER=your-user \
  RABBITMQ_PASS=your-pass \
  JWT_SECRET_KEY=your-jwt-secret \
  GEMINI_API_KEY=your-gemini-key

flyctl deploy
```

### 4. Deploy Frontend
```bash
cd frontend
flyctl launch --name exam-evaluator-frontend --region iad
flyctl secrets set NEXT_PUBLIC_API_URL=https://exam-evaluator-backend.fly.dev/api/v1
flyctl deploy
```

### 5. Run Migrations
```bash
flyctl ssh console -a exam-evaluator-backend
cd /app
alembic upgrade head
```

## Post-Deployment

1. Create demo user
2. Test all endpoints
3. Monitor logs: `flyctl logs -a exam-evaluator-backend`
