# ============================================
# FastAPI + Docker + Aerich Makefile
# ============================================

# Name of the backend container (from docker-compose.yml)
WEB=web

# Name of the Postgres container
DB=db

# ============================================
# Aerich Migration Commands
# ============================================

# Initialize Aerich for the first time.
# Creates aerich.ini and migrations/ folder.
init:
  docker compose exec $(WEB) aerich init -t app.db.TORTOISE_ORM

# Create initial database schema and mark migration as applied.
# Run only ONCE after init.
init-db:
  docker compose exec $(WEB) aerich init-db

# Generate a new migration file based on model changes.
# Does NOT apply the migration.
migrate:
  docker compose exec $(WEB) aerich migrate

# Apply all pending migrations to the database.
upgrade:
  docker compose exec $(WEB) aerich upgrade

# Roll back the most recent migration.
downgrade:
  docker compose exec $(WEB) aerich downgrade

# Show migration history (applied + pending).
history:
  docker compose exec $(WEB) aerich history

# Show the current migration version applied to the DB.
current:
  docker compose exec $(WEB) aerich heads

# ============================================
# Docker Commands
# ============================================

# Start all services and rebuild images if needed.
up:
  docker compose up --build

# Stop all running containers.
down:
  docker compose down

# Restart the entire stack (useful after config changes).
restart:
  docker compose down
  docker compose up --build

# Follow logs of the backend container.
logs:
  docker compose logs -f $(WEB)

# ============================================
# Database Utilities
# ============================================

# Open Postgres shell (psql) inside the DB container.
psql:
  docker compose exec $(DB) psql -U postgres

# Connect directly to the development database.
psql-dev:
  docker compose exec $(DB) psql -U postgres -d web_dev

# Connect directly to the test database.
psql-test:
  docker compose exec $(DB) psql -U postgres -d web_test

# Drop and recreate the development DB (dangerous).
reset-dev-db:
  docker compose exec $(DB) psql -U postgres -c "DROP DATABASE IF EXISTS web_dev;"
  docker compose exec $(DB) psql -U postgres -c "CREATE DATABASE web_dev;"

# ============================================
# Code Quality (optional)
# ============================================

# Format code using Black.
format:
  docker compose exec $(WEB) black .

# Lint code using Flake8.
lint:
  docker compose exec $(WEB) flake8 .
