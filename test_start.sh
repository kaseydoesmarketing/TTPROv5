#!/bin/bash
# Minimal Railway test startup

PORT=${PORT:-8000}
echo "Starting minimal test on port $PORT"
exec python -m uvicorn test_main:app --host 0.0.0.0 --port $PORT --log-level info