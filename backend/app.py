from fastapi import FastAPI
from routes import routes
from starlette.middleware.cors import CORSMiddleware
from common.errors.exception_handlers import *
from settings.settings import settings
import logging


# Create a logger object.
logger = logging.getLogger()
logger.setLevel(settings.LOG_LEVEL)

# Configure the log handler and format.
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create a console handler.
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def create_app():
    from common.database.sqlserver import sqlserver_db_pool

    # Set FastAPI
    app = FastAPI()

    @app.on_event("startup")
    def startup_event():
        sqlserver_db_pool.init_pool()
        logger.info("FastAPI app startup...")

    @app.on_event("shutdown")
    def shutdown_event():
        sqlserver_db_pool.close_pool()
        logger.info("FastAPI app shutdown...")
        logger.info(sqlserver_db_pool.db_pool is None)

    app.exception_handler(HTTPException)(custom_http_exception_handler)
    app.exception_handler(RequestValidationError)(custom_request_validation_error_handler)
    app.exception_handler(ValidationError)(custom_validation_error_handler)
    app.exception_handler(Exception)(custom_exception_handler)

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
