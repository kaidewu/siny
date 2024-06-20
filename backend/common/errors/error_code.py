import logging
import zipfile
import traceback
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


def register_error_logs(file: Any, message: str):
    # Check if exists the Logs folder
    if not Path(settings.ERROR_LOG_PATH).exists():
        Path(settings.ERROR_LOG_PATH).mkdir()

    if Path(settings.ERROR_LOG_PATH).joinpath(f"{datetime.now().strftime("%Y-%m-%d")}-sinasuite-dl.log").exists():
        with zipfile.ZipFile(
                Path(settings.ERROR_LOG_PATH).joinpath(f"{datetime.now().strftime("%Y-%m-%d")}-sinasuite-dl.zip"),
                "w",
                zipfile.ZIP_DEFLATED
        ) as zipf:
            zipf.write(
                Path(settings.ERROR_LOG_PATH).joinpath(f"{datetime.now().strftime("%Y-%m-%d")}-sinasuite-dl.log"),
                arcname=
                Path(settings.ERROR_LOG_PATH).joinpath(f"{datetime.now().strftime("%Y-%m-%d")}-sinasuite-dl.log").split("/")[-1]
            )

    # Log the error into a file
    with open(
            Path(settings.ERROR_LOG_PATH).joinpath(
                f"{(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")}-sinasuite-dl.log"),
            "a",
            encoding="utf-8"
    ) as log:
        log.write(
            f"\n#############################################################################################"
            f"\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} - {str(Path(file).relative_to(settings.ROOT_PATH)).replace("/", ".")}\n"
            f"{message}\n")


def raise_http_error(file: Any, sys_traceback: Any):
    exc_type, exc_value, exc_traceback = sys_traceback

    # Resume: A short summary of the traceback
    resume: str = "".join(traceback.format_exception_only(exc_type, exc_value)).strip().replace(f"{exc_type.__name__}: ", "")

    # Whole body: The detailed traceback
    body: str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)).strip()

    logger.error(resume)

    register_error_logs(file=file, message=body)

    raise HTTPException(
        status_code=error_messages[ErrorCode[error_system.get(exc_type.__name__)]]["status_code"],
        detail={"error_code": ErrorCode[error_system.get(exc_type.__name__)], "message": resume},
    )
