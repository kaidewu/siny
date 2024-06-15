from enum import Enum
from fastapi import HTTPException


class ErrorCode(str, Enum):
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL SERVER ERROR"
    INCORRECT_PASSWORD = "INCORRECT PASSWORD"
    TOO_MANY_REQUESTS = "TOO MANY REQUESTS"
    TOKEN_VALIDATION_FAILED = "TOKEN VALIDATION FAILED"
    APIKEY_VALIDATION_FAILED = "APIKEY VALIDATION FAILED"
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


error_messages = {
    ErrorCode.UNKNOWN_ERROR: {"status_code": 500, "message": "Unknown error occurred."},
    ErrorCode.INTERNAL_SERVER_ERROR: {"status_code": 500, "message": "Internal server error."},
    ErrorCode.INCORRECT_PASSWORD: {"status_code": 401, "message": "Incorrect password."},
    ErrorCode.TOO_MANY_REQUESTS: {"status_code": 429, "message": "Too many requests."},
    ErrorCode.TOKEN_VALIDATION_FAILED: {"status_code": 401, "message": "Token validation failed."},
    ErrorCode.APIKEY_VALIDATION_FAILED: {"status_code": 401, "message": "API key validation failed."},
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
    ErrorCode.UNPROCESSABLE_ENTITY: {"status_code": 422, "message": "Unprocessable Entity."},
}

assert len(error_messages) == len(ErrorCode)


def raise_http_error(error_code: ErrorCode, message: str = ""):
    raise HTTPException(
        status_code=error_messages[error_code]["status_code"],
        detail={"error_code": error_code, "message": message},
    )