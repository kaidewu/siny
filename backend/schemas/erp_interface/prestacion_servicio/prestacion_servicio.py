from pydantic import BaseModel
from typing import Union


class PrestacionServicioModel(BaseModel):
    IdCatalogo: Union[str, None]
    IdPrestacion: str
    IdServicio: str
    Agendable: bool = True
    Duracion: int = 0
    CodCentro: Union[str, None]
    Departamental: str
    Incremento: int = 0
    Decremento: int = 0

