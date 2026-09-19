"""Structured logging configuration for Document Intelligence Service."""

import logging
import sys
import re
from typing import Any, Dict
import json
from contextvars import ContextVar

# ContextVar for Request ID propagation
request_id_ctx: ContextVar[str] = ContextVar("request_id_ctx", default="")

# Sensitive patterns to scrub
SENSITIVE_PATTERNS = [
    (re.compile(r'"password"\s*:\s*"[^"]*"', re.IGNORECASE), '"password": "[REDACTED]"'),
    (re.compile(r'"access_token"\s*:\s*"[^"]*"', re.IGNORECASE), '"access_token": "[REDACTED]"'),
    (re.compile(r'"token"\s*:\s*"[^"]*"', re.IGNORECASE), '"token": "[REDACTED]"'),
    (re.compile(r'Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*', re.IGNORECASE), "Bearer [REDACTED]"),
]


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter with request ID and data sanitization."""

    def format(self, record: logging.LogRecord) -> str:
        req_id = request_id_ctx.get()
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if req_id:
            log_data["request_id"] = req_id

        if hasattr(record, "document_id"):
            log_data["document_id"] = record.document_id
        if hasattr(record, "stage"):
            log_data["stage"] = record.stage
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "error_category"):
            log_data["error_category"] = record.error_category

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        formatted = json.dumps(log_data)
        for pattern, replacement in SENSITIVE_PATTERNS:
            formatted = pattern.sub(replacement, formatted)

        return formatted


def setup_logging(debug: bool = False) -> logging.Logger:
    """Configures application logger."""
    level = logging.DEBUG if debug else logging.INFO
    logger = logging.getLogger("document_intelligence")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    # Suppress overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.INFO)

    return logger
