from typing import Any, List, Dict
from settings.settings import settings
from common.database.sqlserver import sqlserver_db_pool as sqlserver


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

        self.center_name: str = center_name
        self.center_code: str = center_code
        self.external: bool = external
        self.deleted: bool = deleted
        self.page: int = page
        self.size: int = size

        # Set parameters
        self.params: tuple = tuple(filter(
            lambda center: center is not None,
            (self.deleted,
             self.external,
             f"%{self.center_name}%" if self.center_name else None,
             f"%{self.center_code}%" if self.center_code else None)
        ))

        # Set query
        self.query: str = (f"SELECT oc.CENT_NAME, oc.CENT_CODE, oc.CENT_DELETED, oc.CENT_DELETED_DATE, oc.CENT_EXTERNAL "
                           f"FROM ORMA_CENTERS oc "
                           f"WHERE oc.CENT_DELETED = ? AND oc.CENT_EXTERNAL = ?")

        # Center Name
        if self.center_name:
            self.query += " AND oc.CENT_NAME LIKE ?"

        # Center Name
        if self.center_code:
            self.query += " AND oc.CENT_CODE LIKE ?"

        # FETCH LIMIT ROWS
        self.query += (f" ORDER BY oc.CENT_NAME OFFSET {self.size * (self.page - 1)} ROWS "
                       f"FETCH NEXT {self.size} ROWS ONLY")

        self._get_centers: Any = sqlserver.execute(
            query=self.query, params=self.params
        )

    def return_centers(self) -> List[Dict]:
        return [{
            "centerName": row[0],
            "centerCode": row[1],
            "isDeleted": row[2],
            "deletedDate": row[3].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[3] else None,
            "isExternal": row[4]
        } for row in self._get_centers]