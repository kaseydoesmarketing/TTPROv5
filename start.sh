#!/bin/bash
# Render startup script with proper PORT handling

# Render provides PORT environment variable - use it or default to 8000
PORT=${PORT:-8000}

echo "Starting TitleTesterPro server on port $PORT"
echo "Environment PORT: $PORT"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Start the application - Render expects service on the provided PORT
echo "Starting uvicorn on host 0.0.0.0 port $PORT..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info --access-log