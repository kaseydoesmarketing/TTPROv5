#!/bin/bash
# Railway startup script with proper PORT handling

# Get PORT from environment or default to 8000
PORT=${PORT:-8000}

echo "Starting server on port $PORT"

# Run the application
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT