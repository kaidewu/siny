import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.Logger(__name__)
load_dotenv(Path(__file__).parents[1].joinpath(".env"))


def load_str_env(name: str, required: bool = False) -> str:
    """
    Load environment variable as string
    :param name: name of the environment variable
    :param required: whether the environment variable is required
    """
    if os.environ.get(name):
        return os.environ.get(name)

    if required:
        raise Exception(f"Env {name} is not set")


def load_int_env(name: str, required: bool = False) -> int:
    """
    Load environment variable as int
    :param name: name of the environment variable
    :param required: whether the environment variable is required
    """
    if os.environ.get(name):
        return int(os.environ.get(name))

    if required:
        raise Exception(f"Env {name} is not set")


class Settings:
    """ Backend configuration """

    def __init__(self):
        logger.info("Init Config")

        # APP Information
        self.APP_NAME: str = "sinasuite-dl"
        self.ROOT_PATH: Path = Path("../").resolve()
        #if not Path("../backend/temp/").exists():
        #    Path("../backend/temp/").mkdir()
        self.TEMP_PATH: Path = Path("../backend/temp/")
        self.RESOURCES_PATH: Path = Path("../backend/resources/")
        self.ERROR_LOG_PATH: Path = Path("../backend/common/errors/logs")
        self.API_ROUTE_PREFIX: str = "/api/v1"
        self.HOST: str = "localhost"  # It can be your local IP
        self.SERVICE_PORT: int = 8080

        self.HELLOWORLD_HTML: Path = Path("../backend/resources/templates/helloworld.html")

        # LOGGER LEVEL
        self.LOG_LEVEL: str = load_str_env("LOG_LEVEL", required=True)

        # Mode
        self.MODE: str = load_str_env("MODE", required=True)
        self.MODE: str = self.MODE.lower()
        logger.info(f"MODE = {self.MODE}")
        self.DEV: bool = True if self.MODE == "dev" else False
        self.TEST: bool = True if self.MODE == "test" else False
        self.PROD: bool = True if self.MODE == "prod" else False

        # Database Information
        self.SERVERNAME: str = load_str_env("SQLSERVER_SERVERNAME", required=True)
        self.DATABASE: str = load_str_env("SQLSERVER_DATABASE", required=True)
        logger.debug(f"{self.SERVERNAME}:1433/{self.DATABASE}")
        self.SQL_USERNAME: str = load_str_env("SQLSERVER_USERNAME", required=True)
        self.SQL_PASSWORD: str = load_str_env("SQLSERVER_PASSWORD", required=True)
        self.DRIVER: str = load_str_env("SQLSERVER_DRIVER", required=True)


settings = Settings()
