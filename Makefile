# 🚀 Fit API Gateway Makefile
# Modern and easy-to-understand build automation

#-----------------------------------------------
# 🐳 Docker Commands - Local Environment
#-----------------------------------------------

# 🏗️ Build all containers for local development
build:
	docker compose -f docker-compose.local.yml build

# 🚀 Start all services in detached mode for local development
up:
	docker compose -f docker-compose.local.yml up -d

# 🛑 Stop and remove all containers for local development
down:
	docker compose -f docker-compose.local.yml down

# ⏹️ Stop all services without removing them for local development
stop:
	docker compose -f docker-compose.local.yml stop

# 🔄 Restart all services for local development
restart:
	docker compose -f docker-compose.local.yml restart

#-----------------------------------------------
# 🐳 Docker Commands - Production Environment
#-----------------------------------------------

# 🏗️ Build all containers for production
build-prod:
	docker compose -f docker-compose.production.yml build

# 🚀 Start all services in detached mode for production
up-prod:
	docker compose -f docker-compose.production.yml up -d

# 🛑 Stop and remove all containers for production
down-prod:
	docker compose -f docker-compose.production.yml down

# ⏹️ Stop all services without removing them for production
stop-prod:
	docker compose -f docker-compose.production.yml stop

# 🔄 Restart all services for production
restart-prod:
	docker compose -f docker-compose.production.yml restart

#-----------------------------------------------
# 📊 Logging & Debugging
#-----------------------------------------------

# 📝 View logs for a specific service
log:
	docker compose logs -f auth-service

# 🖥️ Open a bash shell in a container
bash:
	docker compose exec auth-service bash

# 🐞 Run a service in debug mode with ports exposed
run-debug:
	docker compose stop auth-service; \
	docker compose rm -f auth-service; \
	docker compose run --rm --service-ports auth-service

#-----------------------------------------------
# 🗄️ Database Migration Commands
#-----------------------------------------------

# 📝 Create a new migration
makemigrations:
	@echo '✏️ Migration Name: '; \
	read NAME; \
	docker compose run --rm auth-service alembic -c /app/libs/alembic.ini revision --autogenerate -m "$$NAME"

# ⬆️ Apply all migrations
migrate:
	docker compose run --rm auth-service alembic -c /app/libs/alembic.ini upgrade heads

# 📋 Show migration history
showmigrations:
	docker compose run --rm auth-service alembic -c /app/libs/alembic.ini history

# 🏁 Initialize migrations
initmigrations:
	docker compose run --rm auth-service alembic -c /app/libs/alembic.ini init migrations

# ⬇️ Downgrade to a previous migration
downgrade:
	@echo '⏮️ Enter revision (or press enter for -1): '; \
	read REVISION; \
	if [ -z "$$REVISION" ]; then \
		docker compose run --rm auth-service alembic -c /app/libs/alembic.ini downgrade -1; \
	else \
		docker compose run --rm auth-service alembic -c /app/libs/alembic.ini downgrade $$REVISION; \
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
	docker compose run --rm auth-service python /app/libs/shell_plus.py
