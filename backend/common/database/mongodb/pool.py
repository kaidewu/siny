import pymongo
from typing import Any, Union
from settings.settings import settings
import logging

logger = logging.Logger(__name__)


class MongoDBPool:
    def __init__(
            self
    ) -> None:
        self.client: Any = None
        self.mongodb_endpoint: str = settings.MONGO_ENDPOINT
        self.mongo_port: int = settings.MONGO_PORT

    def init_pool(self):
        print("Initial MongoDB...")

        self.client = pymongo.MongoClient(self.mongodb_endpoint, self.mongo_port)

    def get_database(self):
        return self.client["chatbot"]

    def get_collection(self):
        db = self.get_database()

        return db["messages"]

    def close_pool(self):
        print("Shutdown MongoDB...")

        self.client.close()


mongodb_pool_instance: Union[MongoDBPool, None] = None


def get_db_pool() -> MongoDBPool:
    if mongodb_pool_instance is None:
        raise Exception("Database connection has not been initialized.")
    return mongodb_pool_instance


def set_db_pool(pool: MongoDBPool) -> None:
    global mongodb_pool_instance
    mongodb_pool_instance = pool
