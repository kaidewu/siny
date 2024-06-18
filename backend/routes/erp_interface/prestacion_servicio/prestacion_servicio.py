from typing import Any, List

from common.services.erp_interface.prestacion_servicio.prestacion_servicio import ERPPrestacionServicio, InsertERPPrestacionServicio, check_status_db_erp_prestacionservicio
from common.errors import raise_http_error, ErrorCode
from schemas.erp_interface.prestacion_servicio.prestacion_servicio import PrestacionServicioModel

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get(
    path="/erp/interface/prestacion/servicio",
    tags=["ERP_PrestacionServicio"],
    summary="Get all ERP_PrestacionServicio"
)
async def get_erp_prestacionservicio(
        catalog_id: str = None,
        prestacion_name: str = None,
        prestacion_code: str = None,
        service_code: str = None,
        agendizable: bool = True,
        center_code: str = None,
        duration: int = 0,
        increment: int = 0,
        decrement: int = 0,
        read: bool = False,
        active: bool = True,
        page: int = 1,
        size: int = 20
) -> Any:
    try:
        erp_prestacionservicio = ERPPrestacionServicio(
            catalog_id=catalog_id,
            prestacion_name=prestacion_name,
            prestacion_code=prestacion_code,
            service_code=service_code,
            agendizable=agendizable,
            center_code=center_code,
            duration=duration,
            increment=increment,
            decrement=decrement,
            read=read,
            active=active,
            page=page,
            size=size
        )

        return JSONResponse(
            content=erp_prestacionservicio.return_prestacionservicio()
        )
    except Exception as e:
        raise_http_error(ErrorCode.INTERNAL_SERVER_ERROR, message=str(e))


@router.post(
    path="/erp/interface/prestacion/servicio/insert",
    tags=["Insert into ERP_PrestacionServicio"],
    summary="Insert data into ERP_PrestacionServicio table"
)
async def insert_erp_prestacionservicio(
        prestacionservicio_body: List[PrestacionServicioModel]
):
    try:
        insert_erp_prestacionservicio = InsertERPPrestacionServicio(
            prestacionservicio_body=prestacionservicio_body
        )

        return JSONResponse(
            content=insert_erp_prestacionservicio.insert_prestacionservicio()
        )
    except Exception as e:
        raise_http_error(ErrorCode.INTERNAL_SERVER_ERROR, message=str(e))
