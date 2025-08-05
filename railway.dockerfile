# Railway-specific Dockerfile for Python backend
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PostgreSQL and Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Poetry
RUN pip install --upgrade pip setuptools wheel && pip install poetry

# Copy poetry files first for better caching
COPY pyproject.toml poetry.lock* ./

# Configure poetry environment
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install dependencies with multiple fallback strategies
RUN echo "Installing dependencies..." && \
    (poetry install --only=main --no-ansi -vvv || \
     echo "Poetry install failed, trying without --only=main" && \
     poetry install --no-dev --no-ansi -vvv || \
     echo "Poetry still failing, exporting to requirements.txt" && \
     poetry export -f requirements.txt --output requirements.txt --without-hashes --only=main && \
     pip install -r requirements.txt || \
     echo "Export failed, installing from pyproject.toml directly" && \
     pip install fastapi[standard] uvicorn psycopg[binary] redis celery firebase-admin google-auth google-auth-oauthlib sqlalchemy alembic asyncpg python-jose[cryptography] passlib[bcrypt] python-multipart psycopg2-binary pydantic-settings)

# Copy application code
COPY app/ ./app/
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY start.sh .

# Make start script executable
RUN chmod +x start.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Use Railway's PORT environment variable
ENV PORT=${PORT:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start command using Railway's PORT
CMD ["sh", "-c", "exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]