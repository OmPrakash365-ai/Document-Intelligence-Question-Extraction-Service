#!/bin/sh
set -e

echo "Starting Document Intelligence Service..."

# Ensure database tables exist
python -c "from app.core.database import engine, Base; import app.models; Base.metadata.create_all(bind=engine)"

# Seed initial evaluator user
python scripts/seed_data.py || true

# Start application
PORT="${PORT:-8000}"
echo "Server starting on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
