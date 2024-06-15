from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class BaseSuccessEmptyResponse(BaseModel):
    status: str = Field("ok")


class BaseSuccessDataResponse(BaseModel):
    status: str = Field("ok")
    data: Optional[Any] = None


class BaseErrorResponse(BaseModel):
    status: str = Field("error")
    error: Dict[str, Any]


class BaseSuccessListResponse(BaseModel):
    status: str = Field("ok")
    count: int = Field(default=0)
    data: Any