import sys
from pathlib import Path
import aiofiles
import aiofiles.os
from common.services.services_specialities.services_specialities import ServicesSpecialitiesUpload
from common.errors import raise_http_error, ErrorCode
from common.database.sqlserver.pool import SQLServerDatabasePool, get_db_pool
from settings.settings import settings
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse

router = APIRouter()


@router.post(
    path="/upload/services-specialities",
    tags=["Upload External Services"],
    summary="Data loading to external services",
    status_code=201
)
async def upload_services_specialities(
        file: UploadFile = File(...)
) -> JSONResponse:

    file_path: Path = Path(settings.TEMP_PATH).joinpath(file.filename)

    # Verification of params.
    if file is None:
        raise ValueError("The file param can not be empty. "
                         "Please, verify and try again.")
    if isinstance(file, list):
        raise ValueError("Upload only one file. "
                         "Please, verify and try again.")
    if file_path.suffix == ".CSV":
        raise ValueError("At the moment, the APP only support Excels files.")

    if file_path.suffix != ".xlsx":
        raise ValueError("The file uploaded is not an Excel. Please, "
                         "verify the file and try again.")

    try:
        db_pool: SQLServerDatabasePool = get_db_pool()

        # Check if exists the uploaded file.
        if not file_path.exists():
            # If exists, save temporary the uploaded file.
            async with aiofiles.open(file_path, "wb") as save_file:
                await save_file.write(await file.read())

        services_specialities: ServicesSpecialitiesUpload = ServicesSpecialitiesUpload(
            environment=db_pool.environment,
            file_path=file_path,
            sqlserver=db_pool
        )

        return JSONResponse(
            content=services_specialities.return_services_specialities()
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())
    finally:
        # If not errors, it's checks if exists and if it's a file.
        if file_path.exists() and file_path.is_file():
            # If it's true, remove the uploaded file.
            await aiofiles.os.remove(file_path)


@router.get(
    path="/service-specialities/example/excel"
)
async def get_service_specialities_excel() -> FileResponse:
    excel_path: Path = Path(settings.RESOURCES_PATH).joinpath("examples/CARGA ESPECIALIDADES EXTERNAS.xlsx")

    if not excel_path.exists() and not excel_path.is_file():
        raise FileNotFoundError("The Excel doesn't exists. Please, contact to the administrator")

    return FileResponse(
        path=excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
