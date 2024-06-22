from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from .error_code import ErrorCode
import traceback
from settings.settings import settings

router = APIRouter()


def build_error_response_dict(uuid, message: str = None, debug: str = None):
    error_dict = {
        "code": str(uuid) if uuid else None,
        "message": message if message else None,
    }
    if debug:
        error_dict["debug"] = debug
    return error_dict


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_response_dict(
                uuid=str(exc.detail.get("uuid")),
                message=exc.detail.get("message", None),
            ),
        )
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_response_dict(uuid=str(exc.detail.get("uuid", None)), message=str(exc.detail.get("message", None))),
        )
