from typing import Any

from common.services.benefits.benefit_types import BenefitTypes
from common.errors import raise_http_error, ErrorCode
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from settings.settings import settings

router = APIRouter()


@router.get(
    path="/benefits/types/helloworld",
    tags=["STATUS ORMA_BENEFIT_TYPES"],
    summary="Status of REST API Benefit Types"
)
async def status_orma_benefit_types():
    """ Return status of the REST API Benefits Types"""
    return HTMLResponse(content=settings.HELLOWORLD_HTML.read_text())


@router.get(
    path="/benefits/types",
    tags=["ORMA_BENEFIT_TYPES"],
    summary="Get all benefits types"
)
async def get_orma_benefit_types(
        benefit_type_name: str = None,
        benefit_type_code: str = None,
        deleted: bool = False,
        page: int = 1,
        size: int = 20
) -> Any:
    try:
        benefit_types = BenefitTypes(
            benefit_type_name=benefit_type_name,
            benefit_type_code=benefit_type_code,
            deleted=deleted,
            page=page,
            size=size
        )

        return JSONResponse(
            content=benefit_types.return_benefit_types()
        )
    except Exception as e:
        raise_http_error(ErrorCode.INTERNAL_SERVER_ERROR, message=str(e))
