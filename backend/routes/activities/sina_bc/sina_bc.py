import sys
from datetime import datetime, timedelta

from common.services.activities.sina_bc.sina_bc import SINA_BC
from common.errors import raise_http_error
from common.database.sqlserver.pool import SQLServerDatabasePool, get_db_pool
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get(
    path="/activities/sina-bc",
    tags=["Activities no passed SINA-BC"],
    summary="Get all activities that has not passed from SINA to BC"
)
async def get_activities_sina_bc(
        appointment_start_date: str = (datetime.now() - timedelta(weeks=2)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        appointment_end_date: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
) -> JSONResponse:
    try:
        db_pool: SQLServerDatabasePool = get_db_pool()

        sina_bc: SINA_BC = SINA_BC(
            appointment_start_date=appointment_start_date,
            appointment_end_date=appointment_end_date,
            sqlserver=db_pool
        )

        return JSONResponse(
            content=sina_bc.return_patients_activities()
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())
