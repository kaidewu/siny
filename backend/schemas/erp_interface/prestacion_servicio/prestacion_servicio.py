from pydantic import BaseModel
from typing import Optional


class PrestacionServicioModel(BaseModel):
    IdCatalogo: Optional[str]
    IdPrestacion: str
    IdServicio: str
    Agendable: bool = True
    Duracion: int = 0
    CodCentro: Optional[str]
    Departamental: str
    Incremento: int = 0
    Decremento: int = 0

