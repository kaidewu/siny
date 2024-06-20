from pydantic import BaseModel
from typing import Union


class SubfamiliaModel(BaseModel):
    IdSubfamilia: Union[str, None] = None,
    Descripcion: Union[str, None] = None,
    IdFamilia: Union[str, None] = None
