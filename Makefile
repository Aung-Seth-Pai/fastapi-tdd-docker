# ============================================
# FastAPI + Docker + Aerich Makefile
# ============================================

# Name of the backend container (from docker-compose.yml)
WEB=web

# Name of the Postgres container
DB=db

# Name of the test service (from docker-compose.yml)
TEST=test

# Heroku app name — replace with your app name from `heroku create`
HEROKU_APP=limitless-ridge-16447
HEROKU_REGISTRY_IMAGE=registry.heroku.com/$(HEROKU_APP)/web

# ============================================
# First-Time / Full Reset Workflows
# ============================================

# First-time setup from a clean state (no containers, no volumes).
# Builds images, starts web + db in background, then applies migrations.
setup:
	docker compose up --build -d $(WEB) $(DB)
	docker compose exec $(WEB) aerich upgrade

# Wipe everything (containers, images, volumes) then run setup fresh.
fresh:
	docker compose down --rmi all --volumes --remove-orphans
	$(MAKE) setup

# Delete generated migration files and recreate from scratch.
# Use this to replay the full aerich init-db flow from zero.
# Steps: wipe everything → delete migrations → start → regenerate → apply.
reset-migrations:
	docker compose down --rmi all --volumes --remove-orphans
	rm -rf backend/migrations
	docker compose up --build -d $(WEB) $(DB)
	docker compose exec $(WEB) aerich init-db

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

# Generate DB schemas manually via Tortoise (run after DB is live).
generate-schemas:
	docker compose exec $(WEB) python -m app.db

# ============================================
# Test Commands
# ============================================

# Run full test suite with coverage report (default).
test:
	docker compose exec $(DB) psql -U postgres -c "CREATE DATABASE web_test" 2>/dev/null || true
	docker compose run --rm $(TEST) python -m pytest --cov=app --cov-branch --cov-report=term-missing

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

# Run only the tests that failed in the last run.
test-lf:
	docker compose run --rm $(TEST) python -m pytest --lf -v --cov=app --cov-report=term-missing

# Enter PDB debugger on first failure (no coverage — meant for interactive debugging).
test-pdb:
	docker compose run --rm $(TEST) python -m pytest -x --pdb

# Stop after N failures. Usage: make test-maxfail N=2
test-maxfail:
	docker compose run --rm $(TEST) python -m pytest --maxfail=$(N) -v --cov=app --cov-report=term-missing

# Show local variables in tracebacks (useful for debugging assertion failures).
test-l:
	docker compose run --rm $(TEST) python -m pytest -l -v --cov=app --cov-report=term-missing

# List the N slowest tests. Usage: make test-durations N=2
test-durations:
	docker compose run --rm $(TEST) python -m pytest --durations=$(N) --cov=app --cov-report=term-missing

# Suppress pytest warnings (useful when third-party warnings clutter output).
test-no-warn:
	docker compose run --rm $(TEST) python -m pytest -p no:warnings --cov=app --cov-report=term-missing

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

# Lint code using Flake8.
lint:
	docker compose exec $(WEB) flake8 .

# Format code using Black.
format:
	docker compose exec $(WEB) black .

isort:
	docker compose exec $(WEB) isort .

isort-check:
	docker compose exec $(WEB) isort . --check-only

# ============================================
# Heroku
# ============================================

# Log in to Heroku's container registry (one-time per machine session).
heroku-login:
	heroku container:login

# Build the production image tagged for Heroku's registry.
heroku-build:
	docker build \
	  --platform linux/amd64 \
	  --provenance=false \
	  -f backend/Dockerfile.prod \
	  -t $(HEROKU_REGISTRY_IMAGE) \
	  ./backend

# Push the built image to Heroku's registry.
heroku-push:
	docker push $(HEROKU_REGISTRY_IMAGE)

# Tell Heroku to activate the pushed image as the live release.
heroku-release:
	heroku container:release web --app $(HEROKU_APP)

# Full deploy in one shot: build → push → release.
heroku-deploy: heroku-build heroku-push heroku-release

# Run pending Aerich migrations on the production database.
heroku-migrate:
	heroku run aerich upgrade --app $(HEROKU_APP)

# Tail live logs from the production dyno.
heroku-logs:
	heroku logs --tail --app $(HEROKU_APP)

# Open an interactive shell inside the running production container.
heroku-shell:
	heroku run bash --app $(HEROKU_APP)

# Open a psql shell against the production Postgres database.
heroku-psql:
	heroku pg:psql --app $(HEROKU_APP)

# Show all environment variables set on the Heroku app.
heroku-config:
	heroku config --app $(HEROKU_APP)

# Show running dynos and their status.
heroku-ps:
	heroku ps --app $(HEROKU_APP)

# Open the live app in a browser.
heroku-open:
	heroku open --app $(HEROKU_APP)

# ============================================
# Declare non-file targets so Make doesn't
# confuse them with actual files on disk.
# ============================================
.PHONY: setup fresh reset-migrations \
        init init-db migrate upgrade downgrade history current \
        up up-dev down clean restart logs logs-test \
        test test-v test-file test-k test-x \
        test-lf test-pdb test-maxfail test-l test-durations test-no-warn \
        test-cov-html \
        psql psql-dev psql-test reset-dev-db reset-test-db \
        format lint \
        heroku-login heroku-build heroku-push heroku-release heroku-deploy \
        heroku-migrate heroku-logs heroku-shell heroku-psql \
        heroku-config heroku-ps heroku-open