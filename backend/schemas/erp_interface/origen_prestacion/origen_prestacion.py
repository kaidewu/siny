from pydantic import BaseModel
from typing import Optional


class OrigenPrestacionModel(BaseModel):
    CodCentro: Optional[str]
    IdAmbito: Optional[str]
    IdCatalogo: Optional[str]
    IdPrestacion: str
