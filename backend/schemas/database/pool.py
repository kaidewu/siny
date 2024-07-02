from pydantic import BaseModel
from typing import Union


class DatabaseCredentials(BaseModel):
    driver: Union[str, None]
    servername: str
    database: Union[str, None]
    username: str
    password: str
