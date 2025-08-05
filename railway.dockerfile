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
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip && pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create virtual environment
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies with fallback
RUN poetry install --no-dev --no-ansi || \
    (echo "Poetry failed, exporting to requirements.txt" && \
     poetry export -f requirements.txt --output requirements.txt --without-hashes && \
     pip install -r requirements.txt)

# Copy application code
COPY app/ ./app/
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY start.sh .

# Make start script executable
RUN chmod +x start.sh

# Use Railway's PORT environment variable
ENV PORT=${PORT:-8000}

# Start command - use Railway's PORT
CMD ["sh", "-c", "./start.sh"]