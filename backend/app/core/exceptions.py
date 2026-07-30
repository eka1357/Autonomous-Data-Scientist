from datetime import datetime, timezone
from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger


class AutoDSException(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFoundException(AutoDSException):
    def __init__(self, message: str = "Requested resource not found"):
        super().__init__(code="NOT_FOUND", message=message, status_code=status.HTTP_404_NOT_FOUND)


class PermissionDeniedException(AutoDSException):
    def __init__(self, message: str = "Permission denied to perform this action"):
        super().__init__(code="PERMISSION_DENIED", message=message, status_code=status.HTTP_403_FORBIDDEN)


async def autods_exception_handler(request: Request, exc: AutoDSException) -> JSONResponse:
    logger.warning(f"Handled exception on {request.url.path}: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
