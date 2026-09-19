"""FastAPI application main entrypoint."""

import uuid
import time
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging, request_id_ctx
from app.core.exceptions import register_exception_handlers
from app.api.routes import (
    auth_router,
    documents_router,
    questions_router,
    answers_router,
    reviews_router,
    health_router,
)
from app.api.routes.samples import router as samples_router

settings = get_settings()
logger = setup_logging(debug=settings.DEBUG)

tags_metadata = [
    {
        "name": "Authentication",
        "description": "User registration, authentication, and JWT token management.",
    },
    {
        "name": "Documents",
        "description": "Upload PDFs and images, check async status, query pages, and manage relations.",
    },
    {
        "name": "Sample Documents",
        "description": "1-Click sample test documents for instant testing.",
    },
    {
        "name": "Questions",
        "description": "Retrieve extracted examination questions, options, confidence, and source pages.",
    },
    {
        "name": "Answers",
        "description": "Retrieve matched answer keys and confidence scores.",
    },
    {
        "name": "Reviews",
        "description": "Access review items for uncertain questions, OCR warnings, and merge notes.",
    },
    {
        "name": "Health",
        "description": "Service health and PostgreSQL/Redis readiness probes.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} initialized and ready.")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# Document Intelligence & Question Extraction Service

A scalable, asynchronous REST API for extracting examination questions from PDFs and images.
Converts real-world imperfect documents into structured, machine-readable question banks.

### Key Capabilities:
* **Multi-Format Processing**: Digitally generated PDFs, scanned PDFs, JPG, JPEG, and PNG images.
* **Asynchronous Processing**: Immediate document ID response, background processing via Celery and Redis.
* **Smart OCR Pipeline**: Selectable PDF text detection with automatic fallback to high-resolution Tesseract OCR and OpenCV preprocessing (grayscale, deskew, denoise, Otsu thresholding).
* **Robust Question Detection**: Supports diverse numbering schemes (`1.`, `1)`, `Q1.`, `Question 1:`, `(1)`), option formats (`A.`, `(a)`, `1.`), and automatic question type classification (`MCQ`, `MULTIPLE_SELECT`, `TRUE_FALSE`, `FILL_IN_THE_BLANK`, `SHORT_ANSWER`, `DESCRIPTIVE`).
* **Multi-Page Question Merging**: Seamlessly unifies questions spanning page breaks (e.g. Question 15 starts on Page 1 and concludes on Page 2).
* **Answer Key Matching**: Associates inline or separate answer-key documents without hallucinating answers.
* **Deterministic Confidence & Human Review**: Multi-factor confidence scoring with granular review items for uncertain extractions.
    """,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id
        token = request_id_ctx.set(req_id)
        start_time = time.time()

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Process-Time-MS"] = str(duration_ms)
            return response
        finally:
            request_id_ctx.reset(token)


# Add Middlewares
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Global Exception Handlers
register_exception_handlers(app)

# Mount Static Files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Serve UI at Root and /ui
@app.get("/", include_in_schema=False)
@app.get("/ui", include_in_schema=False)
def serve_ui():
    index_file = static_dir / "index.html"
    return FileResponse(str(index_file))


# Include Routers
app.include_router(health_router)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(samples_router, prefix=settings.API_V1_STR)
app.include_router(questions_router, prefix=settings.API_V1_STR)
app.include_router(answers_router, prefix=settings.API_V1_STR)
app.include_router(reviews_router, prefix=settings.API_V1_STR)
