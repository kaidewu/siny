from pathlib import Path
from typing import Any, List
from datetime import datetime
from dateutil.relativedelta import relativedelta

import aiofiles
import aiofiles.os
from common.services.benefits.benefits import BenefitsUpload, Benefits
from common.services.benefits.benefit_types import BenefitTypes
from common.errors import raise_http_error, ErrorCode
from common.database.sqlserver import sqlserver_db_pool
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from settings.settings import settings

router = APIRouter()


def get_db():
    db = sqlserver_db_pool.get_db_cursor()
    try:
        yield db
    finally:
        db.close()


@router.get(
    path="/benefits/helloworld",
    tags=["Status REST API Benefits"],
    summary="Status of REST API benefits",
    status_code=200,
    #response_model=BaseSuccessDataResponse
    response_class=HTMLResponse
)
def benefits_api_status() -> Any:
    """ Return status of the REST API Benefits """
    return HTMLResponse(content=settings.HELLOWORLD_HTML.read_text())


@router.post(
    path="/benefits/upload",
    tags=["Uploads"],
    summary="Upload Excel file with benefits data"
)
async def upload_benefits_file(
        file: UploadFile = File(...),
        environment: str = "PRE",
        db = Depends(get_db)
):
    """
    REST API of Benefits where need upload an Excel or CSV file to execute the data loading.
    :param db:
    :param file: An Excel or CSV file to upload
    :param environment: Choose the environment of the application. Depends on which environment, returns different results
    :return: Return the text of SQL Script or the path where it's located the SQL Script file. Still in development.
    """
    # Set the absolute path of uploaded file.
    file_path: Path = Path(settings.TEMP_PATH).joinpath(file.filename)
    # Make uppercase the environment param.
    environment = environment.upper()

    # Verification of params.
    if file is None:
        raise_http_error(ErrorCode.UNPROCESSABLE_ENTITY, message="The file param can not be empty. "
                                                                 "Please, verify and try again.")
    if isinstance(file, list):
        raise_http_error(ErrorCode.REQUEST_VALIDATION_ERROR, message="Upload only one file. "
                                                                     "Please, verify and try again.")
    if file_path.suffix not in (".xlsx", ".csv"):
        raise_http_error(ErrorCode.UNPROCESSABLE_ENTITY, message="The file uploaded is not a Excel nor CSV. Please, "
                                                                 "verify the file and try again.")
    if environment is None:
        raise_http_error(ErrorCode.UNPROCESSABLE_ENTITY, message="The environment param can not be empty."
                                                                 "Please, verify and try again.")
    if not isinstance(environment, str):
        raise_http_error(ErrorCode.UNPROCESSABLE_ENTITY, message="The environment param must be a string. "
                                                                 "Please, verify and try again.")
    if environment not in ("PRO", "PRE"):
        raise_http_error(ErrorCode.UNPROCESSABLE_ENTITY, message="The environment param only accepts 'PRO' and 'PRE' "
                                                                 "values . Please, verify and try again.")
    try:
        # Check if exists the uploaded file.
        if not file_path.exists():
            # If exists, save temporary the uploaded file.
            async with aiofiles.open(file_path, "wb") as save_file:
                await save_file.write(await file.read())

        # Set class Benefits
        #benefits = Benefits(type_file=file_path.suffix, filename=file.filename, env=environment, quantity=10)

        row = db.execute("SELECT TOP 10 * FROM ORMA_BENEFITS").fetchall()
        print(row)
        benefits: List[Any] = [dict(result) for result in row]

        return JSONResponse(
            content={
                "environment": environment,
                "sql_script": benefits
            }
        )
    except Exception as e:
        raise_http_error(ErrorCode.INTERNAL_SERVER_ERROR, message=str(e))
    finally:
        # If not errors, it's checks if exists and if it's a file.
        if file_path.exists() and file_path.is_file():
            # If it's true, remove the uploaded file.
            await aiofiles.os.remove(file_path)


@router.get(
    path="/benefits",
    tags=["Benefits"],
    summary="Get all benefits"
)
async def get_orma_benefits(
        benefit_name: str = None,
        benefit_code: str = None,
        active: bool = True,
        start_created_date: str = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        end_created_date: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        deleted: bool = False,
        size: int = 20
):
    try:
        benefits = Benefits(
            benefit_name=benefit_name,
            benefit_code=benefit_code,
            active=active,
            start_created_date=start_created_date,
            end_created_date=end_created_date,
            deleted=deleted,
            size=size
        )

        return JSONResponse(
            content=benefits.return_benefits()
        )
    except Exception as e:
        raise_http_error(ErrorCode.INTERNAL_SERVER_ERROR, message=str(e))


@router.get(
    path="/benefits/types",
    tags=["Families", "Types"],
    summary="Get all benefits types"
)
async def get_orma_benefit_types():
    try:
        benefit_types = BenefitTypes()

        return JSONResponse(
            content=benefit_types.return_benefit_types()
        )
    except Exception as e:
        raise_http_error(ErrorCode.INTERNAL_SERVER_ERROR, message=str(e))