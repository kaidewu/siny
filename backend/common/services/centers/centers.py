import logging
from typing import Any, List, Dict

logger = logging.Logger(__name__)


class Centers:
    def __init__(
            self,
            center_name: str,
            center_code: str,
            external: bool,
            deleted: bool,
            page: int,
            size: int,
            sqlserver: Any
    ) -> None:
        """

        :param center_name:
        :param center_code:
        :param external:
        :param deleted:
        :param page:
        :param size:
        """
        if not sqlserver:
            raise ConnectionError("The connection of the pool has not been declared")

        self.sqlserver: Any = sqlserver
        self.center_name: str = center_name
        self.center_code: str = center_code
        self.external: bool = external
        self.deleted: bool = deleted
        self.page: int = page
        self.size: int = size

        # Validation size
        if 0 < self.size > 100:
            raise ValueError("The size parameter must be between 0 and 100.")

    def return_centers(self) -> List[Dict]:

        # Set parameters
        params: tuple = tuple(filter(
            lambda center: center is not None,
            (self.deleted,
             self.external,
             f"%{self.center_name}%" if self.center_name else None,
             f"%{self.center_code}%" if self.center_code else None)
        ))

        # Set query
        query: str = (
            f"SELECT oc.CENT_NAME, oc.CENT_CODE, oc.CENT_DELETED, oc.CENT_DELETED_DATE, oc.CENT_EXTERNAL "
            f"FROM [sinasuite].[dbo].[ORMA_CENTERS] oc "
            f"WHERE oc.CENT_DELETED = ? AND oc.CENT_EXTERNAL = ?")

        # Center Name
        if self.center_name:
            query += " AND oc.CENT_NAME LIKE ?"

        # Center Name
        if self.center_code:
            query += " AND oc.CENT_CODE LIKE ?"

        # FETCH LIMIT ROWS
        query += (f" ORDER BY oc.CENT_NAME OFFSET {self.size * (self.page - 1)} ROWS "
                       f"FETCH NEXT {self.size} ROWS ONLY")

        _get_centers: Any = self.sqlserver.execute_select(
            query=query, params=params
        )

        return [{
            "centerName": row[0],
            "centerCode": row[1],
            "isDeleted": row[2],
            "deletedDate": row[3].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[3] else None,
            "isExternal": row[4]
        } for row in _get_centers]
