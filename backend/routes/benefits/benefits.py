from pathlib import Path
from typing import Any, Dict
from datetime import datetime
import sys

import aiofiles
import aiofiles.os
from common.services.benefits.benefits import BenefitsUpload, Benefits
from common.services.stored_procedures.proc_get_nav_benefits import ProcGetNavBenefits
from common.errors import raise_http_error, ErrorCode
from common.database.sqlserver.pool import SQLServerDatabasePool, get_db_pool
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from settings.settings import settings

router = APIRouter()


@router.post(
    path="/create/benefits/upload",
    tags=["Uploads"],
    summary="Upload Excel file with benefits data",
    status_code=201
)
async def upload_benefits_file(
        file: UploadFile = File(...)
) -> Any:
    """
    REST API of Benefits where need upload an Excel or CSV file to execute the data loading.
    :param file: An Excel or CSV file to upload
    :return: Return the text of SQL Script or the path where it's located the SQL Script file. Still in development.
    """
    # Set the absolute path of uploaded file.
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

        # Set class Benefits
        benefits_upload: BenefitsUpload = BenefitsUpload(
            environment=db_pool.environment,
            filename=file.filename,
            sqlserver=db_pool
        )

        dict_prestaciones: Dict = benefits_upload.return_erp_interface_benefits_insertions()

        """
        proc_get_bav_benefits: ProcGetNavBenefits = ProcGetNavBenefits(
            environment=db_pool.environment,
            sqlserver=db_pool,
            prestaciones=dict_prestaciones
        )

        proc_get_bav_benefits.exec_proc_get_nav_benefits()
        """

        return JSONResponse(
            content=dict_prestaciones
        )
    except:
        raise raise_http_error(file=__file__, sys_traceback=sys.exc_info())
    finally:
        # If not errors, it's checks if exists and if it's a file.
        if file_path.exists() and file_path.is_file():
            # If it's true, remove the uploaded file.
            await aiofiles.os.remove(file_path)


@router.get(
    path="/benefits/example/excel",
    tags=["Example Excel benefits"],
    summary="Return the Excel for the data loading for benefits"
)
async def get_benefit_excel():
    excel_path: Path = Path(settings.RESOURCES_PATH).joinpath("examples/CARGA PRESTACION.xlsx")

    if not excel_path.exists() and not excel_path.is_file():
        raise FileNotFoundError("The Excel doesn't exists. Please, contact to the administrator")

    return FileResponse(
        path=excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get(
    path="/benefits",
    tags=["ORMA_BENEFITS"],
    summary="Get all benefits"
)
async def get_orma_benefits(
        benefit_name: str = None,
        benefit_code: str = None,
        benefit_type_code: str = None,
        benefit_subtype_code: str = None,
        active: bool = True,
        start_created_date: str = None,
        end_created_date: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        deleted: bool = False,
        page: int = 1,
        size: int = 20
) -> Any:
    try:
        db_pool: SQLServerDatabasePool = get_db_pool()

        benefits = Benefits(
            benefit_name=benefit_name,
            benefit_code=benefit_code,
            benefit_type_code=benefit_type_code,
            benefit_subtype_code=benefit_subtype_code,
            active=active,
            start_created_date=start_created_date,
            end_created_date=end_created_date,
            deleted=deleted,
            page=page,
            size=size,
            sqlserver=db_pool
        )

        return JSONResponse(
            content=benefits.return_benefits()
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())
