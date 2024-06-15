from pathlib import Path
from typing import List, Any
from settings.settings import settings
from common.database.sqlserver import sqlserver_db_pool


class BenefitTypes:
    def __init__(self, benefit_type_name: str = None, benefit_type_code: str = None):
        self.params: str = " WHERE "
        self.benefit_type_name: str = benefit_type_name
        self.benefit_type_code: str = benefit_type_code

        if self.benefit_type_name:
            self.params += f"BETY_DESCRIPTION_ES LIKE '%{self.benefit_type_name}%'"

        if self.benefit_type_code:
            self.params += f"BETY_CODE LIKE '%{self.benefit_type_code}%'"

    def return_benefit_types(self):

        with sqlserver_db_pool.get_db_cursor() as cursor:
            rows = cursor.execute(
                f"SELECT BETY_DESCRIPTION_ES, BETY_CODE FROM ORMA_BENEFIT_TYPES"
            ).fetchall()

        return [{
            "benefitTypeName": row[0],
            "benefitTypeCode": row[1]
        } for row in rows]
