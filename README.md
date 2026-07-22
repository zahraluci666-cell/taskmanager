# Task Management System: From CLI to Production API

A task management system built in two evolutionary stages that share a single
business-logic core:

1. **CLI tool** — a local command-line task manager (`app/cli`)
2. **Production REST API** — a FastAPI service with authentication, database
   persistence, automated tests, and Docker deployment (`app/api`)

Both interfaces call the exact same `TaskService` in `app/core/service.py`,
demonstrating how a simple script can evolve into a production system without
rewriting the core logic.

## Architecture

```
taskmanager/
├── app/
│   ├── core/            # Shared business logic (used by CLI and API)
│   │   ├── models.py     # SQLAlchemy models: User, Task
│   │   ├── database.py   # DB engine/session
│   │   ├── service.py    # TaskService — create/list/update/delete tasks
│   │   └── security.py   # Password hashing + JWT
│   ├── cli/
│   │   └── main.py       # Click-based CLI
│   └── api/
│       ├── main.py       # FastAPI app entrypoint
│       ├── schemas.py    # Pydantic request/response models
│       ├── deps.py       # Auth dependency
│       └── routes/
│           ├── auth.py   # /auth/register, /auth/login
│           └── tasks.py  # /tasks CRUD
├── tests/
│   ├── test_service.py   # Unit tests for core logic
│   └── test_api.py       # Integration tests for the API
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the CLI

```bash
python -m app.cli.main add "Write final report" --priority high --due 2026-08-01
python -m app.cli.main list
python -m app.cli.main list --status todo
python -m app.cli.main done 1
python -m app.cli.main delete 1
```

## Running the API

```bash
uvicorn app.api.main:app --reload
```

Open interactive docs at: `http://127.0.0.1:8000/docs`

Open the **graphical web UI** at: `http://127.0.0.1:8000/ui`
It's a single-page dashboard (login/register, a kanban-style To Do / In
Progress / Done board, and a command bar that accepts the same syntax as
the CLI, e.g. `add "Deploy to prod" --priority high --due 2026-08-01`).

### Typical flow

```bash
# Register
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'

# Login (get JWT token)
curl -X POST http://127.0.0.1:8000/auth/login \
  -F "username=alice" -F "password=secret123"

# Create a task (use the token from above)
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Deploy to production", "priority": "high"}'
```

## Running with Docker

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Running tests

```bash
pytest -v
```

## Design notes (for the project report)

- **Separation of concerns**: `core` holds all business logic and is fully
  independent of any interface (CLI or HTTP), following the same principle
  used in production systems to keep logic testable and reusable.
- **Authentication**: the API uses JWT bearer tokens; passwords are hashed
  with bcrypt via `passlib`. Tasks are scoped per-user.
- **Persistence**: SQLAlchemy ORM over SQLite by default; the `DATABASE_URL`
  environment variable can point to PostgreSQL for real production use
  without any code changes.
- **Testing**: unit tests target the service layer directly (fast, no HTTP
  overhead); integration tests exercise the full API through FastAPI's
  `TestClient`, using an isolated in-memory database.
- **Deployment**: a `Dockerfile` and `docker-compose.yml` package the API for
  containerized deployment, illustrating the "production" part of the title.

## Possible future work

- Rate limiting and pagination on `/tasks`
- Role-based access (e.g. shared/team tasks)
- Migrate to PostgreSQL + Alembic migrations for schema versioning
- CI/CD pipeline (GitHub Actions) running `pytest` on every push
