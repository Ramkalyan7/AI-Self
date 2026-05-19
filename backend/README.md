# Backend

FastAPI backend for Selfy AI.

The backend uses:

- PostgreSQL through async SQLAlchemy
- Alembic for schema migrations
- LangChain with Gemini as the first LLM provider
- JWTs issued by this backend for auth

## Structure

```text
backend/
|-- app/
|   |-- agent/          # Agent tools and orchestration primitives
|   |-- core/           # Settings and shared app primitives
|   |-- db/             # Async database engine and sessions
|   |-- integrations/   # Third-party API clients
|   |-- models/         # SQLAlchemy table models
|   |-- repositories/   # Database-backed data access
|   |-- routers/        # Feature-based HTTP routers
|   |-- schemas/        # Request/response schemas
|   `-- services/       # Business logic
|-- alembic/
|   `-- versions/       # Alembic migrations
|-- .env.example
|-- alembic.ini
|-- main.py             # Local run entrypoint
`-- pyproject.toml
```

## Setup

Install dependencies:

```bash
uv sync
```

Create `backend/.env` from `.env.example` and set the database URL:

```text
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/selfy
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Run the API:

```bash
uv run python main.py
```

## Database Changes

After changing SQLAlchemy models, generate and review a migration:

```bash
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
```

## Endpoints

```text
GET /health
POST /auth/signup
POST /auth/login
GET /onboarding
PUT /onboarding
POST /llm/generate
```
