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
            benefit_type_code: str,
            benefit_subtype_code: str,
            active: bool,
            start_created_date: str,
            end_created_date: str,
            deleted: bool,
            page: int,
            size: int
    ) -> None:
        self.benefit_name: str = benefit_name
        self.benefit_code: str = benefit_code
        self.benefit_type_code: str = benefit_type_code
        self.benefit_subtype_code: str = benefit_subtype_code
        self.active: bool = active
        self.start_created_date: Union[datetime | None] = datetime.fromisoformat(
            start_created_date.replace("Z", "")) if start_created_date else None
        self.end_created_date: Union[datetime | None] = datetime.fromisoformat(
            end_created_date.replace("Z", "")) if end_created_date else None
        self.deleted: bool = deleted
        self.page: int = page
        self.size: int = size

        # Validation size
        if 0 < self.size > 100:
            raise ValueError("The size parameter must be between 0 and 100.")

    def return_benefits(self) -> List[Dict]:
        # Set params
        params: tuple = tuple(
            filter(lambda bene: bene is not None,
                   (self.active if self.active else False,
                    self.deleted if not self.deleted else True,
                    self.benefit_name if self.benefit_name else None,
                    self.benefit_code if self.benefit_code else None,
                    self.benefit_type_code if self.benefit_type_code else None,
                    self.benefit_subtype_code if self.benefit_subtype_code else None,
                    self.start_created_date if self.start_created_date else None,
                    self.end_created_date if self.end_created_date else None,
                    )))

        # Set the query
        query: str = (
            f"SELECT ob.BENE_NAME, ob.BENE_CODE, obt.BETY_DESCRIPTION_ES, obs.BEST_DESCRIPTION_ES, ob.BENE_ACTIVE, "
            f"ob.BENE_ACTIVE_DATE, ob.BENE_CREATED_DATE, ob.BENE_DELETED, ob.BENE_DELETED_DATE "
            f"FROM [sinasuite].[dbo].[ORMA_BENEFITS] ob "
            f"LEFT OUTER JOIN [sinasuite].[dbo].[ORMA_BENEFIT_TYPES] obt ON obt.BETY_ID = ob.BETY_ID AND obt.BETY_DELETED = 0 "
            f"LEFT OUTER JOIN [sinasuite].[dbo].[ORMA_BENEFIT_SUBTYPES] obs ON obs.BEST_ID = ob.BEST_ID AND obs.BEST_DELETED = 0 "
            f"WHERE ob.BENE_ACTIVE = ? AND ob.BENE_DELETED = ?")

        # BENEFIT NAME
        if self.benefit_name:
            query += " AND ob.BENE_NAME LIKE ?"

        # BENEFIT CODE
        if self.benefit_code:
            query += " AND ob.BENE_CODE LIKE ?"

        # BENEFIT TYPE CODE
        if self.benefit_type_code:
            query += " AND obt.BETY_CODE = ?"

        # BENEFIT SUBTYPE CODE
        if self.benefit_subtype_code:
            query += " AND obs.BEST_CODE = ?"

        # CREATED DATE
        if (
                (self.start_created_date and not self.end_created_date) or
                (not self.start_created_date and self.end_created_date)
        ):
            raise Exception("The range of created start date or end date can't be empty.")
        elif self.start_created_date and self.end_created_date:
            query += " AND ob.BENE_CREATED_DATE BETWEEN ? AND ?"

        # FETCH ROW LIMITS
        query += (f" ORDER BY ob.BENE_NAME OFFSET {self.size * (self.page - 1)} ROWS "
                       f"FETCH NEXT {self.size} ROWS ONLY")

        # Execute the query
        _get_benefits: Any = sqlserver.execute_select(
            query=query, params=params
        )

        return [{
            "benefitName": row[0],
            "benefitCode": row[1],
            "benefitTypeName": row[2],
            "benefitSubtypeName": row[3],
            "isActive": row[4],
            "activeDate": row[5].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[5] else None,
            "createdDate": row[6].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[6] else None,
            "isDeleted": row[7],
            "deletedDate": row[8].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[8] else None
        } for row in _get_benefits]
