from pathlib import Path
import pandas
import logging
from typing import Union
from settings.settings import settings
from common.database.sqlserver import sqlserver_db_pool
from datetime import datetime

logger = logging.Logger(__name__)


class BenefitsUpload:
    def __init__(self, type_file: str, filename: str, env: str, size: int):
        file_path = Path(settings.TEMP_PATH).joinpath(filename)

        if type_file == ".xlsx":
            self.file_read = pandas.read_excel(file_path, sheet_name="BENEFITS")
        elif type_file == ".csv":
            self.file_read = pandas.read_csv(file_path)
        else:
            raise Exception("The file uploaded is not a Excel nor CSV. Please verify the file and try again.")

        self.environment: str = env
        self.size: int = size


class Benefits:
    def __init__(
            self,
            benefit_name: str,
            benefit_code: str,
            active: bool,
            start_created_date: str,
            end_created_date: str,
            deleted: bool,
            size: int
    ):
        self.benefit_name: str = benefit_name
        self.benefit_code: str = benefit_code
        self.active: bool = active
        self.start_created_date: Union[datetime | None] = datetime.fromisoformat(start_created_date.replace("Z", "")) if start_created_date else None
        self.end_created_date: Union[datetime | None] = datetime.fromisoformat(end_created_date.replace("Z", "")) if end_created_date else None
        self.deleted: bool = deleted
        self.size: int = size

        # Set params
        self.params: tuple = tuple(
            filter(lambda bene: bene is not None,
                   (f"%{self.benefit_name}%" if self.benefit_name else None,
                    f"%{self.benefit_code}%" if self.benefit_code else None,
                    self.active if self.active else False,
                    self.start_created_date if self.start_created_date else None,
                    self.end_created_date if self.end_created_date else None,
                    self.deleted if not self.deleted else True
                    )))

        # Set the query
        self.query: str = (f"SELECT ob.BENE_NAME, ob.BENE_CODE, ob.BENE_ACTIVE, ob.BENE_ACTIVE_DATE, ob.BENE_CREATED_DATE, "
                           f"ob.BENE_DELETED, ob.BENE_DELETED_DATE FROM ORMA_BENEFITS ob WHERE 1=1")

        # BENEFIT NAME
        if self.benefit_name:
            self.query += " AND ob.BENE_NAME LIKE ?"

        # BENEFIT CODE
        if self.benefit_code:
            self.query += " AND ob.BENE_CODE LIKE ?"

        # ACTIVE BENEFIT
        if self.active or not self.active:
            self.query += " AND ob.BENE_ACTIVE = ?"

        # CREATED DATE
        if (
                (self.start_created_date and not self.end_created_date) or
                (not self.start_created_date and self.end_created_date)
        ):
            raise Exception("The range of created start date or end date can't be empty.")
        elif self.start_created_date and self.end_created_date:
            self.query += " AND ob.BENE_CREATED_DATE BETWEEN ? AND ?"

        # DELETED BENEFIT
        if self.deleted or not self.deleted:
            self.query += " AND ob.BENE_DELETED = ?"

        # FETCH ROW LIMITS
        self.query += f" ORDER BY ob.BENE_NAME OFFSET {self.size} ROWS FETCH NEXT {self.size} ROWS ONLY"

    def return_benefits(self):
        with sqlserver_db_pool.get_db_cursor() as cursor:
            rows = cursor.execute(
                self.query, self.params
            ).fetchall()

        return [{
            "benefitName": row[0] if row[0] else None,
            "benefitCode": row[1] if row[1] else None,
            "isActive": True if row[2] == 1 else False,
            "activeDate": row[3].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[3] else None,
            "createdDate": row[4].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[4] else None,
            "isDeleted": True if row[5] == 0 else False,
            "deletedDate": row[6].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[6] else None
        } for row in rows]
