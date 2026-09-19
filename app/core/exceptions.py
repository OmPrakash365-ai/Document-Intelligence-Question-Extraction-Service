"""Application custom exceptions and global exception handlers."""

import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("document_intelligence")


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ResourceNotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(message, code=code, status_code=status.HTTP_404_NOT_FOUND)


class DocumentNotFoundError(ResourceNotFoundError):
    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document with ID '{document_id}' was not found.",
            code="DOCUMENT_NOT_FOUND",
        )


class QuestionNotFoundError(ResourceNotFoundError):
    def __init__(self, question_id: str):
        super().__init__(
            message=f"Question with ID '{question_id}' was not found.",
            code="QUESTION_NOT_FOUND",
        )


class AnswerNotFoundError(ResourceNotFoundError):
    def __init__(self, question_id: str):
        super().__init__(
            message=f"Answer for question ID '{question_id}' was not found.",
            code="ANSWER_NOT_FOUND",
        )


class UnauthorizedAccessError(AppException):
    def __init__(self, message: str = "Not authorized to perform this action."):
        super().__init__(
            message,
            code="UNAUTHORIZED_ACCESS",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class AuthenticationError(AppException):
    def __init__(self, message: str = "Could not validate credentials."):
        super().__init__(
            message,
            code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class UnsupportedFileTypeError(AppException):
    def __init__(self, message: str = "Only PDF, JPG, JPEG, and PNG files are supported."):
        super().__init__(
            message,
            code="UNSUPPORTED_FILE_TYPE",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class FileSizeExceededError(AppException):
    def __init__(self, max_size_mb: int):
        super().__init__(
            message=f"File size exceeds the maximum allowed limit of {max_size_mb}MB.",
            code="FILE_SIZE_EXCEEDED",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )


class MalformedFileError(AppException):
    def __init__(self, message: str = "File is malformed or corrupted."):
        super().__init__(
            message,
            code="MALFORMED_FILE",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict detected."):
        super().__init__(
            message,
            code="RESOURCE_CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
        )


class InvalidRelationError(AppException):
    def __init__(self, message: str = "Invalid document relationship."):
        super().__init__(
            message,
            code="INVALID_RELATION",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ExtractionError(AppException):
    def __init__(self, message: str = "Failed to extract content from document."):
        super().__init__(
            message,
            code="EXTRACTION_FAILED",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


from fastapi.encoders import jsonable_encoder

def make_error_response(
    code: str,
    message: str,
    status_code: int,
    request_id: Optional[str] = None,
    details: Optional[Any] = None,
) -> JSONResponse:
    content: Dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id or "unknown",
        }
    }
    if details is not None:
        content["error"]["details"] = jsonable_encoder(details)
    return JSONResponse(status_code=status_code, content=content)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        request_id = getattr(request.state, "request_id", None)
        logger.warning(
            f"AppException: code={exc.code}, message={exc.message}, request_id={request_id}"
        )
        return make_error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            request_id=request_id,
            details=exc.details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = getattr(request.state, "request_id", None)
        code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            code = "NOT_FOUND"
        elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
            code = "UNAUTHORIZED"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            code = "FORBIDDEN"
        elif exc.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
            code = "PAYLOAD_TOO_LARGE"
        elif exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            code = "TOO_MANY_REQUESTS"

        return make_error_response(
            code=code,
            message=str(exc.detail),
            status_code=exc.status_code,
            request_id=request_id,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", None)
        errors = exc.errors()
        return make_error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            request_id=request_id,
            details=errors,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        logger.error(f"Unhandled Exception: {str(exc)}, request_id={request_id}", exc_info=True)
        return make_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred. Please contact support.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
        )
