#!/bin/bash
# Railway startup script with proper PORT handling

# Get PORT from environment or default to 8000
PORT=${PORT:-8000}

echo "Starting TitleTesterPro server on port $PORT"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Available files:"
ls -la

# Start the application with more verbose logging
echo "Starting uvicorn..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info