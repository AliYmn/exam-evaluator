# 🚀 Exam Evaluator Makefile
# Modern and easy-to-understand build automation

#-----------------------------------------------
# 🐳 Docker Commands
#-----------------------------------------------

# 🏗️ Build all containers
build:
	docker compose build

# 🚀 Start all services in detached mode
up:
	docker compose up -d

# 🛑 Stop and remove all containers
down:
	docker compose down

# ⏹️ Stop all services without removing them
stop:
	docker compose stop

# 🔄 Restart all services
restart:
	docker compose restart

#-----------------------------------------------
# 📊 Logging & Debugging
#-----------------------------------------------

# 📝 View logs for all services
logs:
	docker compose logs -f

# 📝 View logs for a specific service
log:
	@echo '🔍 Enter service name (e.g., content-service, auth-service): '; \
	read SERVICE; \
	docker compose logs -f $$SERVICE

# 🖥️ Open a bash shell in a container
bash:
	@echo '🔍 Enter service name (e.g., content-service, auth-service): '; \
	read SERVICE; \
	docker compose exec $$SERVICE bash

# 🐞 Run a service in debug mode with ports exposed
run-debug:
	@echo '🔍 Enter service name (e.g., content-service, auth-service): '; \
	read SERVICE; \
	docker compose stop $$SERVICE; \
	docker compose rm -f $$SERVICE; \
	docker compose run --rm --service-ports $$SERVICE

#-----------------------------------------------
# 🗄️ Database Migration Commands
#-----------------------------------------------

# 📝 Create a new migration
makemigrations:
	@echo '✏️ Migration Name: '; \
	read NAME; \
	docker compose run --rm content-service alembic -c /app/libs/alembic.ini revision --autogenerate -m "$$NAME"

# ⬆️ Apply all migrations
migrate:
	docker compose run --rm content-service alembic -c /app/libs/alembic.ini upgrade heads

# 📋 Show migration history
showmigrations:
	docker compose run --rm content-service alembic -c /app/libs/alembic.ini history

# 🏁 Initialize migrations
initmigrations:
	docker compose run --rm content-service alembic -c /app/libs/alembic.ini init migrations

# ⬇️ Downgrade to a previous migration
downgrade:
	@echo '⏮️ Enter revision (or press enter for -1): '; \
	read REVISION; \
	if [ -z "$$REVISION" ]; then \
		docker compose run --rm content-service alembic -c /app/libs/alembic.ini downgrade -1; \
	else \
		docker compose run --rm content-service alembic -c /app/libs/alembic.ini downgrade $$REVISION; \
	fi

#-----------------------------------------------
# 🛠️ Development Tools
#-----------------------------------------------

# 🔍 Set up pre-commit hooks
pre-check:
	pre-commit uninstall && \
	pre-commit install && \
	pre-commit autoupdate && \
	pre-commit install --hook-type commit-msg -f

# 🐚 Open a Python shell in a service
service-shell:
	@echo '🔍 Enter service name (e.g., content-service, auth-service): '; \
	read SERVICE; \
	docker compose run --rm $$SERVICE python /app/libs/shell_plus.py

# 📊 Show running containers
ps:
	docker compose ps

# 🧹 Clean up unused Docker resources
clean:
	docker compose down -v
	docker system prune -f

#-----------------------------------------------
# ☁️ Fly.io Deployment Commands
#-----------------------------------------------

# 🚀 Deploy all services to Fly.io
deploy-all:
	@echo "🚀 Deploying all services to Fly.io..."
	flyctl deploy -c fly-auth.toml
	flyctl deploy -c fly-content.toml
	flyctl deploy -c fly-worker.toml
	flyctl deploy -c fly-frontend.toml
	@echo "✅ All services deployed successfully!"

# 🔐 Deploy Auth Service
deploy-auth:
	flyctl deploy -c fly-auth.toml

# 📝 Deploy Content Service
deploy-content:
	flyctl deploy -c fly-content.toml

# 👷 Deploy Content Worker
deploy-worker:
	flyctl deploy -c fly-worker.toml

# 🌐 Deploy Frontend
deploy-frontend:
	flyctl deploy -c fly-frontend.toml

# 📊 Check all services status
status-all:
	@echo "📊 Checking all services status..."
	flyctl status -a exam-evaluator-auth
	flyctl status -a exam-evaluator-content
	flyctl status -a exam-evaluator-worker
	flyctl status -a exam-evaluator-frontend

# 📊 Check Auth Service status
status-auth:
	flyctl status -a exam-evaluator-auth

# 📊 Check Content Service status
status-content:
	flyctl status -a exam-evaluator-content

# 📊 Check Worker status
status-worker:
	flyctl status -a exam-evaluator-worker

# 📊 Check Frontend status
status-frontend:
	flyctl status -a exam-evaluator-frontend

# 📝 View all services logs
logs-all:
	@echo "📝 Viewing all services logs..."
	flyctl logs -a exam-evaluator-auth
	flyctl logs -a exam-evaluator-content
	flyctl logs -a exam-evaluator-worker
	flyctl logs -a exam-evaluator-frontend

# 📝 View Auth Service logs
logs-auth:
	flyctl logs -a exam-evaluator-auth

# 📝 View Content Service logs
logs-content:
	flyctl logs -a exam-evaluator-content

# 📝 View Worker logs
logs-worker:
	flyctl logs -a exam-evaluator-worker

# 📝 View Frontend logs
logs-frontend:
	flyctl logs -a exam-evaluator-frontend

# 🔄 Restart all services
restart-all:
	@echo "🔄 Restarting all services..."
	flyctl apps restart exam-evaluator-auth
	flyctl apps restart exam-evaluator-content
	flyctl apps restart exam-evaluator-worker
	flyctl apps restart exam-evaluator-frontend
	@echo "✅ All services restarted!"

# 🔄 Restart Auth Service
restart-auth:
	flyctl apps restart exam-evaluator-auth

# 🔄 Restart Content Service
restart-content:
	flyctl apps restart exam-evaluator-content

# 🔄 Restart Worker
restart-worker:
	flyctl apps restart exam-evaluator-worker

# 🔄 Restart Frontend
restart-frontend:
	flyctl apps restart exam-evaluator-frontend

# 🗄️ Run database migrations
migrate-fly:
	@echo "🗄️ Running database migrations..."
	flyctl ssh console -a exam-evaluator-content -C "cd /app && alembic -c /app/libs/alembic.ini upgrade heads"

# 🔧 Set secrets for all services
set-secrets:
	@echo "🔧 Setting secrets for all services..."
	@echo "Please run the following commands manually:"
	@echo "flyctl secrets set -a exam-evaluator-auth JWT_SECRET_KEY=your_jwt_secret"
	@echo "flyctl secrets set -a exam-evaluator-auth JWT_ALGORITHM=HS256"
	@echo "flyctl secrets set -a exam-evaluator-auth GEMINI_API_KEY=your_gemini_key"
	@echo "flyctl secrets set -a exam-evaluator-content JWT_SECRET_KEY=your_jwt_secret"
	@echo "flyctl secrets set -a exam-evaluator-content JWT_ALGORITHM=HS256"
	@echo "flyctl secrets set -a exam-evaluator-content GEMINI_API_KEY=your_gemini_key"
	@echo "flyctl secrets set -a exam-evaluator-worker GEMINI_API_KEY=your_gemini_key"
	@echo "flyctl secrets set -a exam-evaluator-worker CONTENT_QUEUE_NAME=content_queue"
	@echo "flyctl secrets set -a exam-evaluator-worker CONTENT_WORKER_NAME=content_worker"
