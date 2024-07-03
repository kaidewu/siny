import sys
from typing import Any
from common.database.sqlserver.pool import SQLServerDatabasePool, set_db_pool, get_db_pool
from schemas.database.pool import DatabaseCredentials
from common.errors import raise_http_error, ErrorCode
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post(
    path="/change/connection/database/pool",
    tags=["Change Connection Pool"],
    summary="Change connection from database pool",
    status_code=200
)
async def change_connection_pool(
        credentials: DatabaseCredentials
) -> Any:
    try:
        sqlserver_db_pool = SQLServerDatabasePool(
            driver=credentials.driver,
            servername=credentials.servername,
            database=credentials.database,
            username=credentials.username,
            password=credentials.password,
            environment=credentials.environment
        )

        if not sqlserver_db_pool:
            raise EnvironmentError("The connection has not change. Please check the credentials and try again.")

        sqlserver_db_pool.init_pool()
        set_db_pool(sqlserver_db_pool)

        return JSONResponse(
            content="The connection has been change successfully."
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())
