from pydantic import BaseModel
from typing import Union


class OrigenPrestacionModel(BaseModel):
    CodCentro: Union[str, None] = None,
    IdAmbito: Union[str, None] = None,
    IdCatalogo: Union[str, None] = None,
    IdPrestacion: Union[str, None] = None
