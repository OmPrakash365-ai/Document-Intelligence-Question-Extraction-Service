"""Convenience runner script for instant local evaluation without requiring external services."""

import os
import sys

# Default to SQLite and synchronous Celery execution if no external services are configured
os.environ.setdefault("DATABASE_URL", "sqlite:///./storage/local.db")
os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "true")
os.environ.setdefault("STORAGE_BASE_PATH", "./storage")

import uvicorn
import app.models
from app.core.database import Base, engine
from scripts.seed_data import seed_user


def main():
    print("=" * 70)
    print(" Document Intelligence & Question Extraction Service — Local Runner")
    print("=" * 70)
    print("1. Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    print("2. Seeding default evaluator account...")
    seed_user()

    print("\n" + "=" * 70)
    print(" Service is starting!")
    print(" Interactive Swagger UI: http://localhost:8000/docs")
    print(" ReDoc Documentation:    http://localhost:8000/redoc")
    print(" Default Login:          evaluator@example.com / Password123!")
    print("=" * 70 + "\n")

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
