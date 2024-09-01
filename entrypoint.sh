#!/bin/bash
# Run database migrations
echo "Running migrations..."
python -m alembic upgrade head

# Start the server
exec uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8000} --reload
