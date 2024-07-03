import pyodbc
from typing import Any, Union
from settings.settings import settings
import logging

logger = logging.Logger(__name__)


class SQLServerDatabasePool:
    def __init__(
            self,
            servername: str,
            username: str,
            password: str,
            database: Union[str, None] = None,
            driver: Union[str, None] = None,
            environment: str = "PRE"
    ) -> None:
        self.db_pool = None
        self.driver: str = driver if driver else settings.DRIVER
        self.servername: str = servername
        self.database: str = database if database else "sinasuite"
        self.username: str = username
        self.password: str = password
        self.environment: str = environment

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

    def environment(self) -> str:
        return self.environment


db_pool_instance: Union[SQLServerDatabasePool, None] = None


def get_db_pool() -> SQLServerDatabasePool:
    if db_pool_instance is None:
        raise Exception("Database connection has not been initialized.")
    return db_pool_instance


def set_db_pool(pool: SQLServerDatabasePool) -> None:
    global db_pool_instance
    db_pool_instance = pool
