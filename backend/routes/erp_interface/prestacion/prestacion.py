from typing import Any, List
import sys

from common.services.erp_interface.prestacion.prestacion import ERPPrestacion, InsertERPPrestacion
from common.errors import raise_http_error, ErrorCode
from schemas.erp_interface.prestacion.prestacion import PrestacionModel
from common.database.sqlserver.pool import SQLServerDatabasePool, get_db_pool
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get(
    path="/erp/interface/prestacion",
    tags=["ERP_Prestacion"],
    summary="Get all ERP_Prestacion"
)
async def get_erp_prestacion(
        catalog_id: str = "CAT01",
        prestacion_name: str = None,
        prestacion_code: str = None,
        family_code: str = None,
        subfamily_code: str = None,
        unit_code: str = "UND",
        duration: int = None,
        read: bool = False,
        active: bool = True,
        page: int = 1,
        size: int = 20,

) -> Any:
    try:
        db_pool: SQLServerDatabasePool = get_db_pool()

        erp_prestacion = ERPPrestacion(
            catalog_id=catalog_id,
            prestacion_name=prestacion_name,
            prestacion_code=prestacion_code,
            family_code=family_code,
            subfamily_code=subfamily_code,
            unit_code=unit_code,
            duration=duration,
            read=read,
            active=active,
            page=page,
            size=size,
            sqlserver=db_pool
        )

        return JSONResponse(
            content=erp_prestacion.return_prestacion()
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())


@router.post(
    path="/erp/interface/prestacion/insert",
    tags=["Insert into ERP_Prestacion"],
    summary="Insert data into ERP_Prestacion table",
    status_code=201
)
async def insert_erp_prestacion(
        prestacion_body: List[PrestacionModel]
):
    try:
        db_pool: SQLServerDatabasePool = get_db_pool()

        insert_erp_prestacion = InsertERPPrestacion(
            prestacion_body=prestacion_body,
            sqlserver=db_pool
        )

        return JSONResponse(
            content=insert_erp_prestacion.insert_prestacion()
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())
