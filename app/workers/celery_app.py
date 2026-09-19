"""Celery application configuration."""

import os
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "document_intelligence",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_routes={
        "app.workers.tasks.process_document_task": {"queue": "document_processing"},
        "app.workers.tasks.match_related_document_answers_task": {"queue": "document_processing"},
    },
)
