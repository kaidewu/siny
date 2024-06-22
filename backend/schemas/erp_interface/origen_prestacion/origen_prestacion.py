from pydantic import BaseModel
from typing import Union


class OrigenPrestacionModel(BaseModel):
    CodCentro: str
    IdAmbito: str
    IdCatalogo: Union[str, None]
    IdPrestacion: str
