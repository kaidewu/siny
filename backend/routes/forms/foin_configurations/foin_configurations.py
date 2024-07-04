import sys
import aiofiles
import aiofiles.os
from typing import Any
from pathlib import Path
from common.services.forms.foin_configurations.foin_configurations import FoinConfigurationUpload
from common.database.sqlserver.pool import SQLServerDatabasePool, get_db_pool
from common.errors import raise_http_error
from settings.settings import settings
from fastapi import APIRouter, File, UploadFile, Depends
from fastapi.responses import JSONResponse, FileResponse

router = APIRouter()


@router.post(
    path="/forms/foin/configurations/upload",
    tags=["Upload configurations of forms"],
    summary="Data loading configurations to FOIN_CONF_CONFIGURATIONS and FOIN_CONF_FORMS_LANGUAGES",
    status_code=201
)
async def upload_foin_configurations(
        file: UploadFile = File(...)
) -> Any:
    db_pool: SQLServerDatabasePool = get_db_pool()

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
        if not file_path.exists():
            # If exists, save temporary the uploaded file.
            async with aiofiles.open(file_path, "wb") as save_file:
                await save_file.write(await file.read())

        foin_configurations_upload = FoinConfigurationUpload(
            file_path=file_path,
            environment=db_pool.environment,
            sqlserver=db_pool
        )

        return JSONResponse(
            content=foin_configurations_upload.return_insert_foin_configurations()
        )
    except:
        return raise_http_error(file=__file__, sys_traceback=sys.exc_info())
    finally:
        # If not errors, it's checks if exists and if it's a file.
        if file_path.exists() and file_path.is_file():
            # If it's true, remove the uploaded file.
            await aiofiles.os.remove(file_path)


@router.get(
    path="/forms/foin/configurations/example/excel",
    tags=["Example Excel Forms"],
    summary="Return the Excel for the data loading for Forms"
)
async def get_benefit_excel():

    excel_path: Path = Path(settings.RESOURCES_PATH).joinpath("examples/CARGA FORMS.xlsx")

    if not excel_path.exists() and not excel_path.is_file():
        raise FileNotFoundError("The Excel doesn't exists. Please, contact to the administrator")

    return FileResponse(
        path=excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
