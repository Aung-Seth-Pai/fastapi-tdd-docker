# FastAPI + TDD + Docker

A hands-on project built while learning FastAPI, TDD, and Docker mainly through the [testdriven.io](https://testdriven.io) course — adapted along the way to fit personal preferences and a more modern async-first stack. This is not a production service but kept as a reference for other projects.

---

## Tech Stack

| Layer | Tool |
|---|---|
| API framework | FastAPI |
| ORM | Tortoise ORM (async) |
| Migrations | Aerich |
| Database | PostgreSQL 17 |
| Containerization | Docker + Docker Compose |
| Package manager | uv |
| Testing | pytest + pytest-asyncio + httpx |
| Config | pydantic-settings |

---

## Project Structure

```
fastapi-app/
├── docker-compose.yml
├── Makefile
└── backend/
    ├── Dockerfile
    ├── pyproject.toml
    ├── migrations/          # Aerich migration files
    └── app/
        ├── main.py          # FastAPI app + router registration
        ├── config.py        # Settings (pydantic-settings + lru_cache)
        ├── db.py            # Tortoise ORM config + Aerich TORTOISE_ORM dict
        ├── api/
        │   ├── summaries.py # REST endpoints
        │   ├── crud.py      # DB operations
        │   └── hello_router.py
        ├── models/
        │   ├── text_summary.py  # Tortoise model
        │   └── pydantic.py      # Request/response schemas
        └── tests/
            ├── conftest.py      # pytest fixtures
            ├── test_summaries.py
            └── test_hello.py
```

---

## Docker Compose Services

| Service | Role |
|---|---|
| `web` | FastAPI app (uvicorn), port 8004 → 8000 |
| `db` | PostgreSQL 17, named volume for persistence |
| `test` | Dedicated pytest runner (`TESTING=1`, connects to `web_test` DB) |

---

## First-Time Setup

From a clean state (no containers, no volumes):

```bash
make setup          # build + start web & db + apply migrations
make test           # creates web_test DB if needed, then runs test suite
```

If starting completely from scratch with no migration files:

```bash
make reset-migrations   # wipe everything, delete migrations/, regenerate + apply
make test
```

---

## Startup Workflow Reference

```bash
make fresh              # wipe all containers/images/volumes then run setup
make up-dev             # start web + db only (no test runner)
make upgrade            # apply pending Aerich migrations
make test               # run full test suite
make down               # stop containers
make clean              # remove containers, images, volumes
```

---

## API Endpoints

Base URL (dev): `http://localhost:8004`

| Method | Path | Description |
|---|---|---|
| GET | `/api/hello` | Health check |
| GET | `/api/hello/{name}` | Greeting |
| POST | `/api/summarize` | Create a text summary |
| GET | `/api/summarize/{id}` | Get a summary by ID |
| GET | `/api/summarize` | List all summaries |

**POST `/api/summarize`**
```json
// Request
{ "url": "https://www.example.com" }

// Response 201
{ "id": 1, "url": "https://www.example.com/" }
```

> Note: Pydantic v2's `AnyHttpUrl` normalizes URLs — trailing slash is added automatically.

---

## Test Commands

```bash
make test                   # full suite with coverage
make test-v                 # verbose
make test-x                 # stop on first failure
make test-lf                # re-run only last failed tests
make test-pdb               # drop into PDB debugger on failure
make test-k K=summary       # run tests matching keyword
make test-file FILE=tests/test_summaries.py
make test-maxfail N=2       # stop after N failures
make test-l                 # show local vars in tracebacks
make test-durations N=5     # show N slowest tests
make test-no-warn           # suppress warnings
make test-cov-html          # generate HTML coverage report
```

---

## Database Utilities

```bash
make psql               # open psql shell
make psql-dev           # connect to web_dev DB
make psql-test          # connect to web_test DB
make reset-test-db      # drop + recreate web_test (safe to run anytime)
make reset-dev-db       # drop + recreate web_dev (destructive)
```

---

## Key Concepts

- **Tortoise ORM**: chosen over SQLAlchemy because it is async-native by design, which pairs naturally with FastAPI's async request handling. SQLAlchemy's async support is available but layered on top of a sync core; Tortoise is built from the ground up for asyncio.

- **Aerich**: chosen as the migration tool because it is the official companion to Tortoise ORM, the same way Alembic is to SQLAlchemy. Using any other migration tool with Tortoise would require maintaining the schema separately. `generate_schemas=False` is set in production to force explicit migration control through Aerich rather than letting Tortoise auto-create tables.

- **Dedicated `test` Docker service**: chosen over running pytest inside the `web` container so that the test environment is cleanly isolated — it gets its own env vars (`TESTING=1`, `DATABASE_URL` pointing to `web_test`) without touching the running web process or its database.

- **`httpx.AsyncClient` with `ASGITransport` over Starlette's `TestClient`**: chosen to keep tests fully async (matching the async FastAPI app). The tradeoff is that `ASGITransport` skips ASGI lifespan events, so `register_tortoise()` startup hook never fires during tests. This means Tortoise must be initialized manually inside test fixtures with `Tortoise.init()` + `Tortoise.generate_schemas()`.

- **pytest-asyncio `scope="function"`**: chosen over `scope="module"` to guarantee test isolation. Tortoise connections are bound to the event loop they were created in; module scope shares one connection across tests, which risks state leaking between them. Function scope gives each test its own loop, its own connection, and a clean teardown.

- **pydantic-settings with `@lru_cache`**: chosen to manage environment-based config with type validation and a singleton pattern. `@lru_cache` ensures `Settings` is only instantiated once per process. In tests, FastAPI's `dependency_overrides` swaps in a `Settings(testing=1, database_url=...)` instance without modifying env vars.

- **Named Docker volumes for Postgres**: chosen over bind-mounting a local folder because Docker manages the volume lifecycle and it is portable across machines. The consequence is that `docker-entrypoint-initdb.d/` init scripts (like `01_create.sql`) only run once on a fresh volume — recreating the container alone does not re-run them.
