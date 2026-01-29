FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies (frozen from lock file)
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ ./app/

# Create temp directory for video downloads
RUN mkdir -p /tmp/ugc_videos

EXPOSE 3000

# Run with uv (uses the virtual env it created)
CMD ["uv", "run", "uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", "3000"]
