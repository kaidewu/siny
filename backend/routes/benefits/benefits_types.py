from typing import Any
import sys

from common.services.benefits.benefits_types import BenefitTypes
from common.errors import raise_http_error, ErrorCode
from common.database.sqlserver.pool import SQLServerDatabasePool, get_db_pool
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

router = APIRouter()


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
        size: int = 20,
        db_pool: SQLServerDatabasePool = Depends(get_db_pool)
) -> Any:
    try:
        benefit_types = BenefitTypes(
            benefit_type_name=benefit_type_name,
            benefit_type_code=benefit_type_code,
            deleted=deleted,
            page=page,
            size=size,
            sqlserver=db_pool
        )

        return JSONResponse(
            content=benefit_types.return_benefit_types()
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())
