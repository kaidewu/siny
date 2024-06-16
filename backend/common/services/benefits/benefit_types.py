from typing import Any
from settings.settings import settings
from common.database.sqlserver import sqlserver_db_pool as sqlserver


class BenefitTypes:
    def __init__(
            self,
            benefit_type_name: str,
            benefit_type_code: str,
            deleted: bool,
            page: int,
            size: int
    ) -> None:
        self.query: str = ("SELECT obt.BETY_DESCRIPTION_ES, obt.BETY_CODE, obt.BETY_DELETED, obt.BETY_DELETED_DATE "
                           "FROM ORMA_BENEFIT_TYPES obt "
                           "WHERE obt.BETY_DELETED = ?")

        self.benefit_type_name: str = benefit_type_name
        self.benefit_type_code: str = benefit_type_code
        self.deleted: bool = deleted
        self.page: int = page
        self.size: int = size

        if self.benefit_type_name:
            self.query += f" AND obt.BETY_DESCRIPTION_ES LIKE ?"

        if self.benefit_type_code:
            self.query += f" AND obt.BETY_CODE LIKE ?"

        self.params: tuple = tuple(filter(
            lambda bene_type: bene_type is not None,
            (self.deleted if not self.deleted else True,
             f"%{self.benefit_type_name}%" if self.benefit_type_name else None,
             f"%{self.benefit_type_code}%" if self.benefit_type_code else None
             )
        ))

        self.query += (f" ORDER BY obt.BETY_DESCRIPTION_ES OFFSET {self.size * (self.page - 1)} ROWS "
                       f"FETCH NEXT {self.size} ROWS ONLY")

        self._get_benefit_types: Any = sqlserver.execute(
            query=self.query, params=self.params
        )

    def return_benefit_types(self):
        return [{
            "benefitTypeName": row[0],
            "benefitTypeCode": row[1],
            "isdeleted": row[2],
            "deletedDate": row[3].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[3] else None
        } for row in self._get_benefit_types]
