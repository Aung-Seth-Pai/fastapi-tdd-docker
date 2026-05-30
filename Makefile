# ============================================
# FastAPI + Docker + Aerich Makefile
# ============================================

# Name of the backend container (from docker-compose.yml)
WEB=web

# Name of the Postgres container
DB=db

# Name of the test service (from docker-compose.yml)
TEST=test

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

# Start all services except the test runner (normal dev mode).
up-dev:
	docker compose up --build $(WEB) $(DB)

# Stop all running containers.
down:
	docker compose down

# Remove containers, images, volumes and orphans (full reset).
clean:
	docker compose down --rmi all --volumes --remove-orphans

# Restart the entire stack (useful after config changes).
restart:
	docker compose down
	docker compose up --build

# Follow logs of the backend container.
logs:
	docker compose logs -f $(WEB)

# Show logs of the last test run.
logs-test:
	docker compose logs $(TEST)

# ============================================
# Test Commands
# ============================================

# Run full test suite with coverage report (default).
test:
	docker compose run --rm $(TEST) python -m pytest --cov=app --cov-report=term-missing

# Run tests with verbose output and coverage.
test-v:
	docker compose run --rm $(TEST) python -m pytest -v --cov=app --cov-report=term-missing

# Run a specific test file with coverage. Usage: make test-file FILE=tests/test_summaries.py
test-file:
	docker compose run --rm $(TEST) python -m pytest $(FILE) -v --cov=app --cov-report=term-missing

# Run tests matching a keyword. Usage: make test-k K=summaries
test-k:
	docker compose run --rm $(TEST) python -m pytest -k "$(K)" -v --cov=app --cov-report=term-missing

# Run tests and fail fast on first error.
test-x:
	docker compose run --rm $(TEST) python -m pytest -x -v --cov=app --cov-report=term-missing

# Generate HTML coverage report (opens as htmlcov/index.html).
test-cov-html:
	docker compose run --rm $(TEST) python -m pytest --cov=app --cov-report=html

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

# Drop and recreate the test DB (safe to run anytime).
reset-test-db:
	docker compose exec $(DB) psql -U postgres -c "DROP DATABASE IF EXISTS web_test;"
	docker compose exec $(DB) psql -U postgres -c "CREATE DATABASE web_test;"

# ============================================
# Code Quality
# ============================================

# Format code using Black.
format:
	docker compose exec $(WEB) black .

# Lint code using Flake8.
lint:
	docker compose exec $(WEB) flake8 .

# ============================================
# Declare non-file targets so Make doesn't
# confuse them with actual files on disk.
# ============================================
.PHONY: init init-db migrate upgrade downgrade history current \
        up up-dev down clean restart logs logs-test \
        test test-v test-file test-k test-x test-cov-html \
        psql psql-dev psql-test reset-dev-db reset-test-db \
        format lint