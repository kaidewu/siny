from pydantic import BaseModel
from typing import Union


class PrestacionServicioModel(BaseModel):
    IdCatalogo: Union[str, None] = None,
    IdPrestacion: Union[str, None] = None,
    IdServicio: Union[str, None] = None,
    Agendable: bool = True,
    Duracion: int = 0,
    CodCentro: Union[str, None] = None,
    Departamental: Union[str, None] = None,
    Incremento: int = 0,
    Decremento: int = 0

