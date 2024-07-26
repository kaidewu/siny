from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import routes
from pathlib import Path
from starlette.middleware.cors import CORSMiddleware
from common.errors.exception_handlers import *
from common.database.sqlserver.pool import db_pool_instance
from common.database.mongodb.pool import MongoDBPool, set_db_pool
from settings.settings import settings
import logging


# Create a logger object.
logger = logging.getLogger()
logger.setLevel(settings.LOG_LEVEL)

# Configure the log handler and format.
formatter = logging.Formatter(f"%(asctime)s - {Path('%(name)s').suffix} - %(levelname)s - %(message)s")

# Create a console handler.
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start up parameters
    logger.info("FastAPI app startup...")

    # Start up MongoDB
    client_mongo: MongoDBPool = MongoDBPool()
    client_mongo.init_pool()
    set_db_pool(client_mongo)

    try:
        yield
    finally:
        # Database shutdown parameters
        if db_pool_instance:
            db_pool_instance.close_pool()

        # MongoDB shutdown parameters
        if client_mongo:
            client_mongo.close_pool()

        logger.info("FastAPI app shutdown...")


def create_app():
    # Set FastAPI
    app = FastAPI(lifespan=lifespan)

    app.exception_handler(HTTPException)(custom_http_exception_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routes)

    return app


app = create_app()
