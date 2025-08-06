# Single Railway service for TitleTesterPro backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip && pip install poetry

# Copy poetry files and requirements.txt
COPY pyproject.toml poetry.lock* requirements.txt ./

# Configure Poetry for production
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies
RUN poetry install --no-dev --no-ansi || \
    (echo "Fallback to pip install" && \
     pip install -r requirements.txt)

# Copy application code
COPY app/ ./app/
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY start.sh .

# Make start script executable
RUN chmod +x start.sh

# Use Railway's PORT
ENV PORT=${PORT:-8000}

# Expose the port
EXPOSE ${PORT}

# Use start.sh which handles PORT correctly
CMD ["./start.sh"]