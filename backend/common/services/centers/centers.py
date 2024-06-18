import logging
from typing import Any, List, Dict
from common.database.sqlserver import sqlserver_db_pool as sqlserver

logger = logging.Logger(__name__)


def check_status_db_orma_centers() -> bool:
    try:
        sqlserver.execute("SELECT COUNT(1) FROM [sinasuite].[dbo].[ORMA_CENTERS] WHERE 1=?", 1)
        return True
    except Exception as e:
        logger.error(f"services.centers.centers.check_status_db_orma_centers(): {str(e)}")
        return False


class Centers:
    def __init__(
            self,
            center_name: str,
            center_code: str,
            external: bool,
            deleted: bool,
            page: int,
            size: int
    ) -> None:
        """

        :param center_name:
        :param center_code:
        :param external:
        :param deleted:
        :param page:
        :param size:
        """
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