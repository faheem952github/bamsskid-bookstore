#!/bin/bash

# Wait for PostgreSQL
/app/wait-for-postgres.sh

echo "🛠️ -- Running Alembic migrations..."
alembic upgrade head

echo "🚀 -- Starting FastAPI app..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
