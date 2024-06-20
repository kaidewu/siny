import pyodbc
from urllib.parse import quote_plus
from settings.settings import settings
from typing import List, Any
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
        self.db_pool = None
        self.driver: str = driver
        self.servername: str = servername
        self.database: str = database
        self.username: str = username
        self.password: str = password

    def init_pool(self) -> None:
        """ Initialize database connection pool """
        try:
            logger.info(f"Init SQL Server with {self.servername}/{self.database}")
            self.db_pool = pyodbc.connect(
                f'DRIVER={self.driver};'
                f'SERVER={self.servername};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password};'
                'TrustServerCertificate=yes;',
                autocommit=True
            )
        except Exception as e:
            raise Exception(f"Error in the initialization of database: {str(e)}")

    def cursor(self) -> Any:
        return self.db_pool.cursor()

    def close_pool(self) -> None:
        """Close database connection pool"""

        if self.cursor() is not None:
            self.cursor().close()
        if self.db_pool is not None:
            logger.info(f"Closing SQL Server with {self.servername}/{self.database}")
            self.db_pool.close()

    def begin(self) -> None:
        """Begin a transaction"""
        if self.db_pool is not None:
            self.db_pool.autocommit = False
        logger.info("Transaction started")

    def commit(self) -> None:
        """Commit a transaction"""
        if self.db_pool is not None:
            self.db_pool.commit()
            self.db_pool.autocommit = True
        logger.info("Transaction committed")

    def rollback(self) -> None:
        """Rollback a transaction"""
        if self.db_pool is not None:
            self.db_pool.rollback()
            self.db_pool.autocommit = True
        logger.info("Transaction rolled back")

    def execute_select(self, query: str, params: tuple) -> Any:
        """Execute select queries to the database"""
        try:
            with self.cursor() as cursor:
                _get_query_data = cursor.execute(
                    query, params
                ).fetchall()

            return _get_query_data
        except Exception as e:
            raise Exception(f"SQL Server Error: {str(e)}")

    def execute_insert(self, query: str, params: tuple) -> Any:
        """Execute select queries to the database"""
        try:
            with self.cursor() as cursor:
                _get_query_data = cursor.execute(
                    query, params
                )

            return _get_query_data
        except Exception as e:
            raise Exception(f"SQL Server Error: {str(e)}")

    def execute_procedures(self, query: str) -> Any:
        """Execute select queries to the database"""
        try:
            with self.cursor() as cursor:
                _get_query_data = cursor.execute(
                    query
                )

            return _get_query_data
        except Exception as e:
            raise Exception(f"SQL Server Error: {str(e)}")


# Init SQL Server db pool instance
sqlserver_db_pool = SQLServerDatabasePool(
    driver=settings.DRIVER,
    servername=settings.SERVERNAME,
    database=settings.DATABASE,
    username=settings.SQL_USERNAME,
    password=settings.SQL_PASSWORD
)

