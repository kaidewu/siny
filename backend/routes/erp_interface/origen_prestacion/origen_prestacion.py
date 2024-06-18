from typing import Any, List

from common.services.erp_interface.origen_prestacion.origen_prestacion import ERPOrigenPrestacion, InsertERPOrigenPrestacion, check_status_db_erp_origenprestacion
from common.errors import raise_http_error, ErrorCode
from schemas.erp_interface.origen_prestacion.origen_prestacion import OrigenPrestacionModel

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
        service_code: str = None,
        center_code: str = None,
        read: bool = False,
        active: bool = True,
        page: int = 1,
        size: int = 20
) -> Any:
    try:
        erp_origenprestacion = ERPOrigenPrestacion(
            catalog_id=catalog_id,
            prestacion_name=prestacion_name,
            prestacion_code=prestacion_code,
            ambit_code=ambit_code,
            service_code=service_code,
            center_code=center_code,
            read=read,
            active=active,
            page=page,
            size=size
        )

        return JSONResponse(
            content=erp_origenprestacion.return_origenprestacion()
        )
    except Exception as e:
        raise_http_error(ErrorCode.INTERNAL_SERVER_ERROR, message=str(e))


@router.post(
    path="/erp/interface/origen/prestacion/insert",
    tags=["Insert into ERP_OrigenPrestacion"],
    summary="Insert data into ERP_OrigenPrestacion table"
)
async def insert_erp_prestacion(
        origenprestacion_body: List[OrigenPrestacionModel]
):
    try:
        insert_erp_origenprestacion = InsertERPOrigenPrestacion(
            origenprestacion_body=origenprestacion_body
        )

        return JSONResponse(
            content=insert_erp_origenprestacion.insert_origenprestacion()
        )
    except Exception as e:
        raise_http_error(ErrorCode.INTERNAL_SERVER_ERROR, message=str(e))
