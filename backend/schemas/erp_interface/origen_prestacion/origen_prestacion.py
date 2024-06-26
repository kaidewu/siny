from pydantic import BaseModel
from typing import Union


class OrigenPrestacionModel(BaseModel):
    CodCentro: Union[str, None]
    IdAmbito: str
    IdCatalogo: Union[str, None]
    IdPrestacion: str
