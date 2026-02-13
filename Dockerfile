FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies (frozen from lock file)
RUN uv sync --frozen --no-dev

# Copy Alembic config and migrations
COPY alembic.ini ./
COPY migrations/ ./migrations/

# Copy application code
COPY app/ ./app/

EXPOSE 3000

# Run with uv (uses the virtual env it created)
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:api --host 0.0.0.0 --port 3000"]
