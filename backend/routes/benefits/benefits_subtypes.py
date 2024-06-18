from typing import Any

from common.services.benefits.benefits_subtypes import BenefitSubtypes, check_status_db_subtypes
from common.errors import raise_http_error, ErrorCode
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get(
    path="/status/benefits/subtypes",
    tags=["STATUS ORMA_BENEFIT_SUBTYPES"],
    summary="Status of REST API Benefit Subtypes"
)
async def status_orma_benefit_subtypes():
    """ Return status of the REST API Benefits Types"""
    return JSONResponse(
        content={
            "status": "Available" if check_status_db_subtypes() else "Outage"
        }
    )


@router.get(
    path="/benefits/subtypes",
    tags=["ORMA_BENEFIT_SUBTYPES"],
    summary="Get all benefits subtypes"
)
async def get_orma_benefit_subtypes(
        benefit_subtype_name: str = None,
        benefit_subtype_code: str = None,
        benefit_type_code: str = None,
        deleted: bool = False,
        page: int = 1,
        size: int = 20
) -> Any:
    try:
        benefit_subtypes = BenefitSubtypes(
            benefit_subtype_name=benefit_subtype_name,
            benefit_subtype_code=benefit_subtype_code,
            benefit_type_code=benefit_type_code,
            deleted=deleted,
            page=page,
            size=size
        )

        return JSONResponse(
            content=benefit_subtypes.return_benefit_subtypes()
        )
    except Exception as e:
        raise_http_error(ErrorCode.INTERNAL_SERVER_ERROR, message=str(e))
