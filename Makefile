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
