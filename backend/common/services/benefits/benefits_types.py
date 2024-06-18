from typing import Any
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
        """

        :param benefit_type_name:
        :param benefit_type_code:
        :param deleted:
        :param page:
        :param size:
        """
        self.sqlserver: Any = sqlserver
        self.benefit_type_name: str = benefit_type_name
        self.benefit_type_code: str = benefit_type_code
        self.deleted: bool = deleted
        self.page: int = page
        self.size: int = size

        # Validation size
        if 0 < self.size > 100:
            raise ValueError("The size parameter must be between 0 and 100.")

    def return_benefit_types(self):
        # Set parameters
        params: tuple = tuple(filter(
            lambda bene_type: bene_type is not None,
            (self.deleted if not self.deleted else True,
             self.benefit_type_name if self.benefit_type_name else None,
             self.benefit_type_code if self.benefit_type_code else None
             )
        ))

        # Queries
        query: str = ("SELECT obt.BETY_DESCRIPTION_ES, obt.BETY_CODE, obt.BETY_DELETED, obt.BETY_DELETED_DATE "
                      "FROM [sinasuite].[dbo].[ORMA_BENEFIT_TYPES] obt "
                      "WHERE obt.BETY_DELETED = ?")

        if self.benefit_type_name:
            query += f" AND obt.BETY_DESCRIPTION_ES LIKE ?"

        if self.benefit_type_code:
            query += f" AND obt.BETY_CODE LIKE ?"

        query += (f" ORDER BY obt.BETY_DESCRIPTION_ES OFFSET {self.size * (self.page - 1)} ROWS "
                  f"FETCH NEXT {self.size} ROWS ONLY")

        _get_benefit_types: Any = self.sqlserver.execute_select(
            query=query, params=params
        )

        return [{
            "benefitTypeName": row[0],
            "benefitTypeCode": row[1],
            "isDeleted": row[2],
            "deletedDate": row[3].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[3] else None
        } for row in _get_benefit_types]
