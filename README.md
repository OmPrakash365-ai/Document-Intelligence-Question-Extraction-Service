# Document Intelligence & Question Extraction Service

A scalable, production-oriented REST service built with **FastAPI**, **SQLAlchemy 2.x**, **PostgreSQL**, **Redis**, **Celery**, and **PyMuPDF / OpenCV / Tesseract OCR** that converts PDFs and examination paper images into structured, machine-readable question banks with automated answer-key matching, deterministic confidence scoring, and human review routing.

---

## 1. Project Overview

Educational examination papers, diagnostic assessments, and question banks often exist in imperfect formats: scanned PDFs with tilt or blur, photos taken on mobile devices (JPG/PNG), digitally generated PDFs with mixed fonts, and multi-page questions where problem statements and options cross page boundaries.

This service provides an end-to-end, non-blocking asynchronous pipeline:
1. **Immediate Ingestion**: Accepts multi-format documents via multipart upload and immediately returns a tracking ID (`202 Accepted`).
2. **Intelligent Page Processing**: Detects whether selectable text is present. Digitally rendered pages bypass rasterization, while scans are preprocessed with OpenCV (grayscale, deskew, denoise, Otsu thresholding) and run through Tesseract OCR.
3. **Robust Question Detection**: Discovers question boundaries across numbering schemes (`1.`, `1)`, `Q1.`, `Question 1:`, `(1)`), extracts options (`A.`, `(a)`, `1.`), and classifies question types (`MCQ`, `MULTIPLE_SELECT`, `TRUE_FALSE`, `FILL_IN_THE_BLANK`, `SHORT_ANSWER`, `DESCRIPTIVE`).
4. **Multi-Page Question Merging**: Detects when questions are split across page breaks and unifies them into single coherent entities with multi-page source tracking (`[1, 2]`).
5. **Answer Key Association**: Supports both inline answer keys and separate answer-key documents linked via relationships, associating answers without hallucinating or guessing.
6. **Deterministic Confidence & Human Review**: Every question receives an explainable confidence score. Uncertain extractions automatically generate categorized `ReviewItem` entries.

---

## 2. Architecture

```mermaid
flowchart TD
    subgraph Client Layer
        Client["Client / API Consumer / Postman"]
    end

    subgraph API Layer ["FastAPI Application (Port 8000)"]
        Router["API Router (/api/v1)"]
        AuthMiddleware["JWT Auth & Security"]
        DocService["DocumentService"]
        QService["QuestionService"]
        RelService["RelationService"]
    end

    subgraph Persistence Layer
        PG[("PostgreSQL 16\n(Normalized Tables)")]
        Redis[("Redis 7\n(Broker & Cache)")]
        Storage["StorageService\n(Local Disk / S3 / GCS)"]
    end

    subgraph Asynchronous Worker Layer ["Celery Workers"]
        Worker["Celery Processing Worker"]
        PageProc["PageProcessor / PDFProcessor"]
        OCR["Tesseract OCR / Mock Fallback"]
        Preproc["OpenCV Preprocessor\n(Deskew, Denoise, Otsu)"]
        QDetect["QuestionDetector & OptionDetector"]
        QMerge["QuestionMerger\n(Multi-Page Unification)"]
        AnsKey["AnswerKeyDetector\n(Inline & Cross-Doc)"]
        ConfScore["ConfidenceService\n(Deterministic Scoring)"]
    end

    Client --> Router
    Router --> AuthMiddleware
    AuthMiddleware --> DocService
    AuthMiddleware --> QService
    AuthMiddleware --> RelService

    DocService --> Storage
    DocService --> PG
    DocService --> Redis

    Redis --> Worker
    Worker --> PageProc
    PageProc --> Preproc
    Preproc --> OCR
    Worker --> QDetect
    QDetect --> QMerge
    Worker --> AnsKey
    Worker --> ConfScore
    ConfScore --> PG
```

Detailed architectural flows, sequence diagrams, and failure recovery are documented in [docs/architecture.md](docs/architecture.md).

---

## 3. Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.12+ | Modern syntax, strong typing, speed |
| **API Framework** | FastAPI | High-performance async REST API with OpenAPI |
| **Validation** | Pydantic v2 | Strict schema validation and serialization |
| **Database ORM** | SQLAlchemy 2.x | Type-safe declarative database operations |
| **Database Migrations** | Alembic | Version-controlled schema migrations |
| **Database** | PostgreSQL 16 | Primary relational data store |
| **Message Broker** | Redis 7 | Celery task queues and result backend |
| **Task Queue** | Celery 5.x | Asynchronous background processing |
| **PDF Processing** | PyMuPDF (fitz) | Fast PDF parsing, text extraction, page rendering |
| **Image Preprocessing** | OpenCV & Pillow | Deskew, denoise, Otsu thresholding, rotation |
| **OCR Engine** | Tesseract OCR | Local open-source OCR (with mock fallback for tests) |
| **Authentication** | Passlib, Bcrypt, Python-Jose | Salted bcrypt hashing and JWT token handling |
| **Testing** | Pytest, Pytest-Asyncio, HTTPX | Unit and integration test suite |

---

## 4. Features

- **Asynchronous Non-Blocking Upload**: Immediate `202 Accepted` response with document ID.
- **Multi-Stage Real-Time Status**: Tracks progress from 0% to 100% across stages: `UPLOADING`, `VALIDATING`, `EXTRACTING_TEXT`, `OCR`, `DETECTING_QUESTIONS`, `MATCHING_ANSWERS`, `VALIDATING`, `COMPLETED`.
- **Hybrid OCR & Digital Extraction**: Automatically detects digital vector text to bypass expensive OCR; falls back to 300 DPI image rendering and OpenCV enhancement when needed.
- **Multi-Format Numbering & Options**: Detects `1.`, `1)`, `Q1.`, `Question 1:`, `(1)`, `A.`, `(a)`, `1.`.
- **Multi-Page Question Unification**: Concatenates split questions and unifies options across page breaks.
- **Cross-Document Answer Key Association**: Links separate answer-key PDFs (`POST /documents/{id}/relations`) and matches questions.
- **Zero-Hallucination Policy**: If answers are missing or ambiguous, they are marked `UNMATCHED` or `UNCERTAIN` and flagged for human review.
- **Granular Review System**: Issues categorized by type (`LOW_OCR_CONFIDENCE`, `PARTIAL_QUESTION`, `OPTIONS_UNCERTAIN`, `ANSWER_UNMATCHED`, etc.) with severity levels (`HIGH`, `MEDIUM`, `LOW`).
- **Secure File Handling**: Magic bytes inspection, random storage filenames, and path traversal protection.

---

## 5. Folder Structure

```
PBNC/
├── app/
│   ├── main.py                      # FastAPI app entrypoint, middleware, and routes
│   ├── core/
│   │   ├── config.py                # Pydantic v2 settings
│   │   ├── security.py              # Bcrypt, JWT tokens, path traversal protection
│   │   ├── database.py              # SQLAlchemy engine, sessionmaker, GUID type
│   │   ├── logging.py               # Structured JSON logger with request ID
│   │   └── exceptions.py            # Global exception handlers and domain exceptions
│   ├── api/
│   │   ├── dependencies.py          # Database and JWT authentication dependencies
│   │   └── routes/
│   │       ├── auth.py              # Register, login, me
│   │       ├── documents.py         # Upload, list, status, delete, pages, relations
│   │       ├── questions.py         # List questions by document, single question
│   │       ├── answers.py           # Get question answers
│   │       ├── reviews.py           # Get document review items
│   │       └── health.py            # Health and readiness probes
│   ├── models/                      # SQLAlchemy 2.x declarative models
│   ├── schemas/                     # Pydantic v2 request/response schemas
│   ├── services/                    # Business logic and orchestration
│   ├── processors/                  # OCR, PDF, image, question, and answer engines
│   ├── workers/                     # Celery application and asynchronous tasks
│   ├── repositories/                # Database query abstractions with eager loading
│   └── utils/                       # File validation, hashing, text cleaning
├── tests/
│   ├── conftest.py                  # Pytest fixtures and in-memory test database
│   ├── unit/                        # Unit tests for core business logic
│   └── integration/                 # Integration tests for API endpoints and pipeline
├── scripts/
│   ├── create_sample_documents.py   # Generates 10 realistic test documents
│   └── seed_data.py                 # Seeds demo user
├── sample_documents/                # Generated sample PDFs and images
├── sample_outputs/                  # Expected JSON output examples
├── docs/
│   └── architecture.md              # Detailed architecture documentation
├── postman/
│   └── document-intelligence.postman_collection.json # 14-step Postman collection
├── alembic/                         # Alembic database migrations
├── alembic.ini                      # Alembic configuration
├── Dockerfile                       # Production Docker image with Tesseract
├── docker-compose.yml               # Multi-container setup (postgres, redis, api, worker, flower)
├── .env.example                     # Environment variable template
├── requirements.txt                 # Python dependencies
└── README.md                        # Documentation
```

---

## 6. Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Key configuration options:

```ini
# Application
APP_NAME=Document Intelligence & Question Extraction Service
API_V1_STR=/api/v1
SECRET_KEY=replace-with-a-secure-key
DEBUG=false

# Database & Redis
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/document_intelligence
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Security & Storage
JWT_SECRET_KEY=replace-with-a-secure-jwt-key
MAX_UPLOAD_SIZE_MB=25
STORAGE_BASE_PATH=./storage

# OCR & Thresholds
OCR_PROVIDER=tesseract
OCR_LANGUAGE=eng
OCR_DPI=300
HIGH_CONFIDENCE_THRESHOLD=0.85
MEDIUM_CONFIDENCE_THRESHOLD=0.65
```

---

## 7. Docker Setup

To run the entire stack with PostgreSQL, Redis, FastAPI API, Celery Worker, and Flower:

```bash
docker compose up --build
```

The services will be available at:
* **FastAPI Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Flower Celery Dashboard**: [http://localhost:5555](http://localhost:5555)

---

## 8. Local Setup

### Prerequisites
* Python 3.12+
* PostgreSQL & Redis (or use Docker for DB/Redis only)
* Tesseract OCR (`brew install tesseract` on macOS or `apt-get install tesseract-ocr` on Ubuntu)

### Step-by-Step

1. **Create and activate virtual environment**:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Seed initial demo user**:
   ```bash
   python scripts/seed_data.py
   ```

5. **Generate sample documents**:
   ```bash
   python scripts/create_sample_documents.py
   ```

6. **Start FastAPI server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Start Celery worker** (in a separate terminal):
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info -Q document_processing
   ```

---

## 9. Running Tests

The test suite runs with an in-memory SQLite database and mock OCR fixtures, requiring no external databases or Tesseract binaries:

```bash
source .venv/bin/activate
PYTHONPATH=. pytest -v tests/
```

To run with coverage:
```bash
PYTHONPATH=. pytest -v --cov=app tests/
```

---

## 10. API Documentation

Interactive Swagger documentation is available at `/docs` and ReDoc at `/redoc`.

### Summary of Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new user account |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT token |
| `GET` | `/api/v1/auth/me` | Retrieve profile of current user |
| `POST` | `/api/v1/documents` | Upload PDF/image; returns document ID immediately |
| `GET` | `/api/v1/documents` | List uploaded documents with pagination |
| `GET` | `/api/v1/documents/{id}` | Get document metadata and processing summary |
| `GET` | `/api/v1/documents/{id}/status`| Real-time processing progress and stage |
| `DELETE` | `/api/v1/documents/{id}` | Delete document, questions, answers, and files |
| `GET` | `/api/v1/documents/{id}/pages/{page}` | Get extracted text, OCR flag, and image for a page |
| `POST` | `/api/v1/documents/{id}/relations` | Link related documents (e.g. Question Paper + Answer Key) |
| `GET` | `/api/v1/documents/{id}/relations` | List relations for a document |
| `DELETE` | `/api/v1/documents/{id}/relations/{rel_id}` | Remove a document relation |
| `GET` | `/api/v1/documents/{id}/questions` | Get paginated structured questions |
| `GET` | `/api/v1/questions/{id}` | Get individual question details |
| `GET` | `/api/v1/questions/{id}/answer` | Get answer information for a question |
| `GET` | `/api/v1/documents/{id}/reviews` | Get review items and warnings |
| `GET` | `/health` | Application health check |
| `GET` | `/ready` | Database & Redis readiness probe |

---

## 11. Example API Requests & Responses

### 1. Upload Document
**Request**:
```http
POST /api/v1/documents HTTP/1.1
Host: localhost:8000
Authorization: Bearer <TOKEN>
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="clean_digital.pdf"
Content-Type: application/pdf

<PDF_BINARY_DATA>
------WebKitFormBoundary--
```

**Response (`202 Accepted`)**:
```json
{
  "document_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "QUEUED",
  "message": "Document uploaded and queued for processing"
}
```

### 2. Check Status
**Request**:
```http
GET /api/v1/documents/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d/status HTTP/1.1
Authorization: Bearer <TOKEN>
```

**Response**:
```json
{
  "document_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "PROCESSING",
  "progress": 55,
  "current_stage": "DETECTING_QUESTIONS",
  "pages_processed": 1,
  "total_pages": 1
}
```

### 3. Retrieve Questions (Section 17 Response Format)
**Request**:
```http
GET /api/v1/documents/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d/questions HTTP/1.1
Authorization: Bearer <TOKEN>
```

**Response**:
```json
{
  "items": [
    {
      "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "document_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "question_number": "1",
      "question": "Which data structure operates on a First-In-First-Out (FIFO) basis?",
      "question_type": "MCQ",
      "options": [
        {"key": "A", "text": "Stack", "confidence": 1.0},
        {"key": "B", "text": "Queue", "confidence": 1.0},
        {"key": "C", "text": "Binary Tree", "confidence": 1.0},
        {"key": "D", "text": "Graph", "confidence": 1.0}
      ],
      "answer": {
        "value": "B",
        "confidence": 0.95,
        "matching_status": "MATCHED",
        "source_document_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "source_page": 1
      },
      "source": {
        "document_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "pages": [1]
      },
      "confidence": 0.94,
      "extraction_status": "SUCCESS"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 50,
  "pages": 1
}
```

---

## 12. OCR Pipeline

The OCR pipeline follows a strict, defensive strategy:
1. **Digital Text Check**: Tests character count, word density, and alphanumeric ratios. If selectable text is intact and legible, native text is extracted directly, bypassing rasterization.
2. **High-Resolution Rendering**: If native text is absent or corrupt, PyMuPDF renders pages at 300 DPI.
3. **Image Preprocessing**:
   - `to_grayscale()`: Converts multi-channel images to 8-bit single-channel.
   - `deskew()`: Uses OpenCV `minAreaRect` on foreground text pixels to detect and rotate away paper tilts.
   - `denoise()`: Applies bilateral filtering to eliminate scan speckles without blurring character strokes.
   - `threshold()`: Applies Otsu binarization to maximize contrast for the OCR engine.
4. **Tesseract OCR Execution**: Extracts full text and computes word-level confidence values.

---

## 13. Question Extraction Strategy

The question detection engine does not rely exclusively on regular expressions. It combines multiple signals:
* **Numbering Patterns**: `1.`, `1)`, `Q1.`, `Q.1`, `Question 1:`, `(1)`, `[1]`.
* **Option Patterns**: `A.`, `(a)`, `1.`, `[A]`, across multi-line or inline layouts.
* **Layout & Structure**: Line breaks, indentation, and paragraph blocks.
* **Semantic Keywords**: Questions starting with `What`, `Which`, `Explain`, `Define`, `Calculate`, or containing `?`.
* **Type Classification**:
  - `MCQ`: Has options and single answer expectation.
  - `MULTIPLE_SELECT`: Has options and contains keywords like "select all that apply".
  - `TRUE_FALSE`: Contains "True or False" or options [True, False].
  - `FILL_IN_THE_BLANK`: Contains underscores `_____` or "fill in the blank".
  - `SHORT_ANSWER`: Open-ended question with concise expectation.
  - `DESCRIPTIVE`: Open-ended question with extensive explanation cues ("Explain in detail").
  - `UNKNOWN`: Unclear structure routed to human review.

---

## 14. Answer Key Matching & Relations

Answer keys can be located:
1. **Inline**: At the end of the question paper.
2. **Cross-Document**: In a separate document (e.g. `AnswerKey.pdf`).

When documents are linked via `POST /documents/{id}/relations` with `relation_type="ANSWER_KEY"`, a background task parses the answer key document and maps answers to questions using normalized identifiers (e.g. `Q1` $\to$ `1`).

* **Zero-Hallucination Policy**:
  - If an answer is clearly matched $\to$ `MATCHED`.
  - If an answer is ambiguous $\to$ `UNCERTAIN` (with a review item).
  - If no answer is found $\to$ `UNMATCHED` (without fabricating answers).

---

## 15. Confidence Scoring

Every question receives a deterministic score:

$$\text{Score} = 0.25 \times C_{\text{OCR}} + 0.25 \times C_{\text{Boundary}} + 0.20 \times C_{\text{Option}} + 0.15 \times C_{\text{Completeness}} + 0.15 \times C_{\text{Answer}}$$

* Score $\ge 0.85$: High confidence (`SUCCESS`).
* $0.65 \le \text{Score} < 0.85$: Medium confidence (`SUCCESS`).
* Score $< 0.65$: Low confidence (`REVIEW_REQUIRED`). Creates a `ReviewItem`.

---

## 16. Security

* **Authentication**: Salted bcrypt password hashing and JWT access tokens.
* **Authorization**: All database queries filter by `owner_id`. Cross-user access returns `403 Forbidden` or `404 Not Found`.
* **File Validation**: MIME type verification, extension whitelisting, file size limits (25MB default), and magic bytes checking.
* **Safe Filenames**: Uploaded files are stored using cryptographically random UUIDs (`uuid4().hex`).
* **Path Traversal Protection**: Storage paths are validated using `safe_join` to prevent directory traversal attacks.
* **Data Sanitization**: Sensitive fields (`password`, `token`, `Bearer`) are automatically redacted from logs.
* **SQL Injection Prevention**: All queries use SQLAlchemy 2.x parameterized expressions.

---

## 17. Sample Documents & Outputs

Sample documents generated in `sample_documents/`:
1. `clean_digital.pdf`: Clean digital exam with MCQs, True/False, and Fill-in-the-blank.
2. `scanned_exam.pdf`: Simulated scanned paper with slight skew.
3. `low_quality_scan.pdf`: Low-contrast, noisy scan.
4. `question_paper.jpg`: JPEG question paper.
5. `question_paper.png`: PNG question paper.
6. `multipage_question.pdf`: Question 15 starts on Page 1 and concludes on Page 2.
7. `exam_with_inline_answers.pdf`: Exam with Answer Key at the end.
8. `separate_answer_key.pdf`: Standalone answer key document.
9. `invalid_document.pdf`: Corrupt file disguised as PDF.
10. `unclear_question.pdf`: Unclear numbering and missing options.

Expected JSON responses are located in `sample_outputs/`.

---

## 18. Postman Collection

A complete, automated Postman collection is located at:
`postman/document-intelligence.postman_collection.json`

It includes the complete 14-step workflow:
1. Register
2. Login (sets `{{token}}` variable)
3. Upload PDF (sets `{{document_id}}` variable)
4. Upload Image
5. Get Document Details
6. Check Status
7. Get Extracted Questions (sets `{{question_id}}` variable)
8. Get Individual Question
9. Get Answer
10. Get Review Items
11. Upload Separate Answer Key (sets `{{answer_key_document_id}}`)
12. Create Relation
13. Retrieve Relations
14. Invalid Upload Demonstration

---

## 19. Design Decisions & Trade-offs

1. **Local OCR vs Cloud AI**:
   - *Decision*: Built with PyMuPDF, OpenCV, and Tesseract OCR with an abstract `DocumentUnderstandingProvider` interface.
   - *Rationale*: Allows anyone evaluating the assignment to run it locally or via Docker without requiring paid API keys or internet access.
2. **Synchronous vs Asynchronous Processing**:
   - *Decision*: Upload returns `202 Accepted` immediately with status `QUEUED`. Processing is delegated to Celery workers.
   - *Rationale*: Ensures the API remains responsive regardless of document size.
3. **Deterministic Confidence vs Black-Box Scoring**:
   - *Decision*: Deterministic, explainable weighted formula based on OCR quality, boundary certainty, option structure, text completeness, and answer key presence.
   - *Rationale*: Allows downstream systems and human evaluators to understand why a question requires review.

---

## 20. Limitations & Future Improvements

- **Handwritten Documents**: Current Tesseract model is optimized for printed text. Future iterations could integrate TrOCR or handwriting-specialized vision models.
- **Complex Mathematical Notation**: Formulas are currently extracted as unicode text. Future iterations could integrate LaTeX formula detection (e.g. Nougat or Mathpix).
- **Multi-Column Layouts**: Documents with multiple vertical columns can be improved by adding layout analysis (e.g. LayoutParser or YOLOv8-DocLayNet).
