"""Health and readiness check routes."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis

from app.core.config import get_settings
from app.core.database import get_db

settings = get_settings()
router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Service health check",
    description="Returns basic health status of the application.",
)
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get(
    "/ready",
    summary="Service readiness check",
    description="Checks connectivity to PostgreSQL database and Redis.",
)
def readiness_check(db: Session = Depends(get_db)):
    checks = {"database": False, "redis": False}
    status_code = status.HTTP_200_OK

    # Check Database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        checks["database_error"] = str(e)
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL, socket_timeout=2)
        r.ping()
        checks["redis"] = True
    except Exception as e:
        checks["redis_error"] = str(e)
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    all_ready = checks["database"] and checks["redis"]
    content = {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
    }
    return JSONResponse(status_code=status_code, content=content)
