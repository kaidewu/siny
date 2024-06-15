import pyodbc
from urllib.parse import quote_plus
from settings.settings import settings
from typing import List
import logging

logger = logging.Logger(__name__)


def connection_string(driver: str, server: str, database: str, username: str, password: str) -> str:
    return (
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        'TrustServerCertificate=yes;'
    )


class SQLServerDatabasePool:
    def __init__(
            self,
            driver: str,
            servername: str,
            database: str,
            username: str,
            password: str
    ) -> None:
        self.cursor = None
        self.db_pool = None
        self.driver: str = driver
        self.servername: str = servername
        self.database: str = database
        self.username: str = username
        self.password: str = password

    def init_pool(self) -> None:
        """ Initialize database connection pool """

        logger.info(f"Init SQL Server with {self.servername}/{self.database}")
        self.db_pool = pyodbc.connect(
            f'DRIVER={self.driver};'
            f'SERVER={self.servername};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            'TrustServerCertificate=yes;'
        )

        self.cursor = self.db_pool.cursor()

    def close_pool(self) -> None:
        """Close database connection pool"""

        if self.cursor is not None:
            self.cursor.close()
        if self.db_pool is not None:
            logger.info(f"Closing SQL Server with {self.servername}/{self.database}")
            self.db_pool.close()

    def get_db_cursor(self):
        """Get database connection from pool"""

        return self.cursor


# Init SQL Server db pool instance
sqlserver_db_pool = SQLServerDatabasePool(
    driver=settings.DRIVER,
    servername=settings.SERVERNAME,
    database=settings.DATABASE,
    username=settings.SQL_USERNAME,
    password=settings.SQL_PASSWORD
)

