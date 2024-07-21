from pydantic import BaseModel
from typing import Optional


class DatabaseCredentials(BaseModel):
    driver: Optional[str]
    servername: str
    database: Optional[str]
    username: str
    password: str
    environment: str
