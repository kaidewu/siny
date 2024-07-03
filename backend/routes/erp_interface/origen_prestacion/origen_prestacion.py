from typing import Any, List
import sys

from common.services.erp_interface.origen_prestacion.origen_prestacion import ERPOrigenPrestacion, InsertERPOrigenPrestacion
from common.errors import raise_http_error, ErrorCode
from schemas.erp_interface.origen_prestacion.origen_prestacion import OrigenPrestacionModel
from common.database.sqlserver.pool import SQLServerDatabasePool, get_db_pool
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get(
    path="/erp/interface/origen/prestacion",
    tags=["ERP_OrigenPrestacion"],
    summary="Get all ERP_OrigenPrestacion"
)
async def get_erp_prestacion(
        catalog_id: str = "CAT01",
        prestacion_name: str = None,
        prestacion_code: str = None,
        ambit_code: str = None,
        center_code: str = None,
        read: bool = False,
        active: bool = True,
        page: int = 1,
        size: int = 20
) -> Any:
    try:
        db_pool: SQLServerDatabasePool = get_db_pool()

        erp_origenprestacion = ERPOrigenPrestacion(
            catalog_id=catalog_id,
            prestacion_name=prestacion_name,
            prestacion_code=prestacion_code,
            ambit_code=ambit_code,
            center_code=center_code,
            read=read,
            active=active,
            page=page,
            size=size,
            sqlserver=db_pool
        )

        return JSONResponse(
            content=erp_origenprestacion.return_origenprestacion()
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())


@router.post(
    path="/erp/interface/origen/prestacion/insert",
    tags=["Insert into ERP_OrigenPrestacion"],
    summary="Insert data into ERP_OrigenPrestacion table",
    status_code=201
)
async def insert_erp_prestacion(
        origenprestacion_body: List[OrigenPrestacionModel]
):
    try:
        db_pool: SQLServerDatabasePool = get_db_pool()

        insert_erp_origenprestacion = InsertERPOrigenPrestacion(
            origenprestacion_body=origenprestacion_body,
            sqlserver=db_pool
        )

        return JSONResponse(
            content=insert_erp_origenprestacion.insert_origenprestacion()
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())
