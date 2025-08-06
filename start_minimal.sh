#!/bin/bash
# Minimal startup script for testing Railway deployment

# Get PORT from environment or default to 8000
PORT=${PORT:-8000}

echo "Starting minimal TitleTesterPro server on port $PORT"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Start the minimal application
echo "Starting minimal uvicorn..."
exec python -m uvicorn minimal_main:app --host 0.0.0.0 --port $PORT --log-level info