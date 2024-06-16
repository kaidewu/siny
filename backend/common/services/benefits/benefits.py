from pathlib import Path
import pandas
import logging
from typing import Union, Any, List, Dict
from settings.settings import settings
from common.database.sqlserver import sqlserver_db_pool as sqlserver
from datetime import datetime

logger = logging.Logger(__name__)


class BenefitsUpload:
    def __init__(
            self,
            type_file: str,
            filename: str,
            env: str,
            size: int
    ) -> None:
        file_path = Path(settings.TEMP_PATH).joinpath(filename)

        if type_file == ".xlsx":
            self.file_read = pandas.read_excel(file_path, sheet_name="BENEFITS")
        elif type_file == ".csv":
            self.file_read = pandas.read_csv(file_path)
        else:
            raise Exception("The file uploaded is not a Excel nor CSV. Please verify the file and try again.")

        self.environment: str = env
        self.size: int = size

    def to_json(self) -> Union[Dict | None]:
        return self.file_read.to_dict()


class Benefits:
    def __init__(
            self,
            benefit_name: str,
            benefit_code: str,
            active: bool,
            start_created_date: str,
            end_created_date: str,
            deleted: bool,
            page: int,
            size: int
    ) -> None:
        self.benefit_name: str = benefit_name
        self.benefit_code: str = benefit_code
        self.active: bool = active
        self.start_created_date: Union[datetime | None] = datetime.fromisoformat(
            start_created_date.replace("Z", "")) if start_created_date else None
        self.end_created_date: Union[datetime | None] = datetime.fromisoformat(
            end_created_date.replace("Z", "")) if end_created_date else None
        self.deleted: bool = deleted
        self.page: int = page
        self.size: int = size

        # Set params
        self.params: tuple = tuple(
            filter(lambda bene: bene is not None,
                   (self.active if self.active else False,
                    self.deleted if not self.deleted else True,
                    f"%{self.benefit_name}%" if self.benefit_name else None,
                    f"%{self.benefit_code}%" if self.benefit_code else None,
                    self.start_created_date if self.start_created_date else None,
                    self.end_created_date if self.end_created_date else None,
                    )))

        # Validation size
        if 0 < self.size > 100:
            raise Exception("The size parameter must be between 0 and 100.")

        # Set the query
        self.query: str = (f"SELECT ob.BENE_NAME, ob.BENE_CODE, ob.BENE_ACTIVE, "
                           f"ob.BENE_ACTIVE_DATE, ob.BENE_CREATED_DATE, ob.BENE_DELETED, ob.BENE_DELETED_DATE "
                           f"FROM ORMA_BENEFITS ob "
                           f"WHERE ob.BENE_ACTIVE = ? AND ob.BENE_DELETED = ?")

        # BENEFIT NAME
        if self.benefit_name:
            self.query += " AND ob.BENE_NAME LIKE ?"

        # BENEFIT CODE
        if self.benefit_code:
            self.query += " AND ob.BENE_CODE LIKE ?"

        # CREATED DATE
        if (
                (self.start_created_date and not self.end_created_date) or
                (not self.start_created_date and self.end_created_date)
        ):
            raise Exception("The range of created start date or end date can't be empty.")
        elif self.start_created_date and self.end_created_date:
            self.query += " AND ob.BENE_CREATED_DATE BETWEEN ? AND ?"

        # FETCH ROW LIMITS
        self.query += (f" ORDER BY ob.BENE_NAME OFFSET {self.size * (self.page - 1)} ROWS "
                       f"FETCH NEXT {self.size} ROWS ONLY")

        # Execute the query
        self._get_benefits: Any = sqlserver.execute(
            query=self.query, params=self.params
        )

    def return_benefits(self) -> List[Dict]:
        return [{
            "benefitName": row[0],
            "benefitCode": row[1],
            "isActive": row[2],
            "activeDate": row[3].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[3] else None,
            "createdDate": row[4].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[4] else None,
            "isDeleted": row[5],
            "deletedDate": row[6].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[6] else None
        } for row in self._get_benefits]
