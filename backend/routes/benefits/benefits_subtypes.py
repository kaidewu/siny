from typing import Any
import sys

from common.services.benefits.benefits_subtypes import BenefitSubtypes
from common.errors import raise_http_error, ErrorCode
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


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
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())
