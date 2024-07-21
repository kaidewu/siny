import logging
import zipfile
import traceback
from uuid import uuid4, UUID
from typing import Any
from enum import Enum
from pathlib import Path
from fastapi import HTTPException
from settings.settings import settings
from datetime import datetime, timedelta

logger = logging.Logger(__name__)


class ErrorCode(str, Enum):
    UNKNOWN_ERROR = "UNKNOWN ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL SERVER ERROR"
    INCORRECT_PASSWORD = "INCORRECT PASSWORD"
    TOO_MANY_REQUESTS = "TOO MANY REQUESTS"
    OBJECT_NOT_FOUND = "OBJECT NOT FOUND"
    REQUEST_VALIDATION_ERROR = "REQUEST VALIDATION ERROR"
    DATA_MODEL_VALIDATION_ERROR = "DATA MODEL VALIDATION ERROR"
    RESOURCE_LIMIT_REACHED = "RESOURCE LIMIT REACHED"
    DUPLICATE_OBJECT = "DUPLICATE OBJECT"
    ACTION_API_REQUEST_ERROR = "ACTION API REQUEST ERROR"
    OBJECT_LOCKED = "OBJECT_LOCKED"
    INVALID_REQUEST = "INVALID REQUEST"
    FORBIDDEN = "FORBIDDEN"
    UNPROCESSABLE_ENTITY = "UNPROCESSABLE ENTITY"
    CLIENT_CLOSED_REQUEST = "CLIENT CLOSE REQUEST"
    EXPECTATION_FAILED = "EXPECTATION FAILED"
    SERVICE_UNAVAILABLE = "SERVICE UNAVAILABLE"
    CONFLICT = "CONFLICT"


error_messages = {
    ErrorCode.UNKNOWN_ERROR: {"status_code": 500, "message": "Unknown error occurred."},
    ErrorCode.INTERNAL_SERVER_ERROR: {"status_code": 500, "message": "Internal server error."},
    ErrorCode.INCORRECT_PASSWORD: {"status_code": 401, "message": "Incorrect password."},
    ErrorCode.TOO_MANY_REQUESTS: {"status_code": 429, "message": "Too many requests."},
    ErrorCode.OBJECT_NOT_FOUND: {"status_code": 404, "message": "Object does not exist."},
    ErrorCode.REQUEST_VALIDATION_ERROR: {"status_code": 400, "message": "Request validation error."},
    ErrorCode.DATA_MODEL_VALIDATION_ERROR: {"status_code": 400, "message": "Data model validation error."},
    ErrorCode.RESOURCE_LIMIT_REACHED: {
        "status_code": 429,
        "message": "You have reached the limit of allowed resources.",
    },
    ErrorCode.DUPLICATE_OBJECT: {"status_code": 409, "message": "Duplicate object."},
    ErrorCode.ACTION_API_REQUEST_ERROR: {"status_code": 400, "message": "Action API request error."},
    ErrorCode.OBJECT_LOCKED: {"status_code": 423, "message": "Object locked."},
    ErrorCode.INVALID_REQUEST: {"status_code": 400, "message": "Invalid request."},
    ErrorCode.FORBIDDEN: {"status_code": 403, "message": "Forbidden."},
    ErrorCode.CLIENT_CLOSED_REQUEST: {"status_code": 499, "message": "Client Closed Request."},
    ErrorCode.UNPROCESSABLE_ENTITY: {"status_code": 422, "message": "Unprocessable Entity."},
    ErrorCode.EXPECTATION_FAILED: {"status_code": 417, "message": "Expectation Failed."},
    ErrorCode.SERVICE_UNAVAILABLE: {"status_code": 503, "message": "Service Unavailable."},
    ErrorCode.CONFLICT: {"status_code": 409, "message": "Conflict."},
}

assert len(error_messages) == len(ErrorCode)


error_system = {
    "SystemExit": "INTERNAL_SERVER_ERROR",
    "ValidationError": "INTERNAL_SERVER_ERROR",
    "KeyboardInterrupt": "CLIENT_CLOSED_REQUEST",
    "GeneratorExit": "INTERNAL_SERVER_ERROR",
    "Exception": "INTERNAL_SERVER_ERROR",
    "StopIteration": "OBJECT_NOT_FOUND",
    "ArithmeticError": "REQUEST_VALIDATION_ERROR",
    "OverflowError": "REQUEST_VALIDATION_ERROR",
    "FloatingPointError": "REQUEST_VALIDATION_ERROR",
    "ZeroDivisionError": "REQUEST_VALIDATION_ERROR",
    "AssertionError": "417 Expectation Failed",
    "AttributeError": "REQUEST_VALIDATION_ERROR",
    "EOFError": "REQUEST_VALIDATION_ERROR",
    "ImportError": "INTERNAL_SERVER_ERROR",
    "ModuleNotFoundError": "OBJECT_NOT_FOUND",
    "LookupError": "OBJECT_NOT_FOUND",
    "IndexError": "REQUEST_VALIDATION_ERROR",
    "KeyError": "REQUEST_VALIDATION_ERROR",
    "MemoryError": "INTERNAL_SERVER_ERROR",
    "NameError": "REQUEST_VALIDATION_ERROR",
    "UnboundLocalError": "REQUEST_VALIDATION_ERROR",
    "OSError": "INTERNAL_SERVER_ERROR",
    "BlockingIOError": "SERVICE_UNAVAILABLE",
    "ChildProcessError": "INTERNAL_SERVER_ERROR",
    "ConnectionError": "SERVICE_UNAVAILABLE",
    "BrokenPipeError": "INTERNAL_SERVER_ERROR",
    "ConnectionAbortedError": "SERVICE_UNAVAILABLE",
    "ConnectionRefusedError": "SERVICE_UNAVAILABLE",
    "ConnectionResetError": "SERVICE_UNAVAILABLE",
    "FileExistsError": "CONFLICT",
    "FileNotFoundError": "OBJECT_NOT_FOUND",
    "InterruptedError": "SERVICE_UNAVAILABLE",
    "IsADirectoryError": "REQUEST_VALIDATION_ERROR",
    "NotADirectoryError": "REQUEST_VALIDATION_ERROR",
    "PermissionError": "FORBIDDEN",
    "ProcessLookupError": "OBJECT_NOT_FOUND",
    "TimeoutError": "RESOURCE_LIMIT_REACHED",
    "ReferenceError": "INTERNAL_SERVER_ERROR",
    "RuntimeError": "INTERNAL_SERVER_ERROR",
    "NotImplementedError": "501 Not Implemented",
    "RecursionError": "INTERNAL_SERVER_ERROR",
    "SyntaxError": "REQUEST_VALIDATION_ERROR",
    "IndentationError": "REQUEST_VALIDATION_ERROR",
    "TabError": "REQUEST_VALIDATION_ERROR",
    "SystemError": "INTERNAL_SERVER_ERROR",
    "TypeError": "REQUEST_VALIDATION_ERROR",
    "ValueError": "REQUEST_VALIDATION_ERROR",
    "UnicodeError": "REQUEST_VALIDATION_ERROR",
    "UnicodeDecodeError": "REQUEST_VALIDATION_ERROR",
    "UnicodeEncodeError": "REQUEST_VALIDATION_ERROR",
    "UnicodeTranslateError": "REQUEST_VALIDATION_ERROR",
    "Warning": "INTERNAL_SERVER_ERROR",
    "DeprecationWarning": "INTERNAL_SERVER_ERROR",
    "PendingDeprecationWarning": "INTERNAL_SERVER_ERROR",
    "RuntimeWarning": "INTERNAL_SERVER_ERROR",
    "SyntaxWarning": "INTERNAL_SERVER_ERROR",
    "UserWarning": "INTERNAL_SERVER_ERROR",
    "FutureWarning": "INTERNAL_SERVER_ERROR",
    "ImportWarning": "INTERNAL_SERVER_ERROR",
    "UnicodeWarning": "INTERNAL_SERVER_ERROR",
    "BytesWarning": "INTERNAL_SERVER_ERROR",
    "ResourceWarning": "INTERNAL_SERVER_ERROR"
}


def register_error_logs(file: Any, message: str, uuid: UUID):
    # Set datetime now
    current_date: datetime = datetime.now()

    # Set error log path
    error_log_path: Path = Path(settings.ERROR_LOG_PATH).resolve()

    # Check if exists the Logs folder
    error_log_path.mkdir(exist_ok=True)

    # Iterate over all log files in the directory
    for log_file in error_log_path.glob("server.log.*"):
        # Get the modification time of the log file
        modification_time = datetime.fromtimestamp(log_file.stat().st_mtime)

        # Check if the log file is older than 7 days
        if modification_time < current_date - timedelta(weeks=1):
            # Remove the log file
            log_file.unlink()

    # Save each log the day before
    if error_log_path.joinpath(f"server.log.{(current_date - timedelta(days=1)).strftime("%Y-%m-%d")}").exists():
        error_log_path.rename(error_log_path.joinpath(f"server.log.{(current_date - timedelta(days=1)).strftime("%Y-%m-%d")}"))
        error_log_path.joinpath("server.log").unlink()

    # Log the error into a file
    with open(error_log_path.joinpath("server.log"), "a", encoding="utf-8") as log:
        log.write(
            f"\n{'='*200}"
            f"\n{current_date.strftime("%Y-%m-%d %H:%M:%S.%f")} - {uuid} - {str(Path(file).relative_to(settings.ROOT_PATH)).replace("/", ".")}\n"
            f"{message}\n")


def raise_http_error(file: Any, sys_traceback: Any):
    exc_type, exc_value, exc_traceback = sys_traceback

    uuid_code: UUID = uuid4()

    # Resume: A short summary of the traceback
    resume: str = "".join(traceback.format_exception_only(exc_type, exc_value)).strip().replace(f"{exc_type.__name__}: ", "")

    # Whole body: The detailed traceback
    body: str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)).strip()

    logger.error(resume)
    print(exc_type.__name__)

    register_error_logs(file=file, message=body, uuid=uuid_code)

    raise HTTPException(
        status_code=error_messages[ErrorCode[error_system.get(exc_type.__name__)]]["status_code"],
        detail={"uuid": uuid_code, "message": resume},
    )
