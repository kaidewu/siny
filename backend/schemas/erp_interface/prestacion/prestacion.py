from pydantic import BaseModel
from typing import Union


class PrestacionModel(BaseModel):
    IdCatalogo: Union[str, None]
    IdPrestacion: str
    IdFamilia: str
    IdSubfamilia: str
    Descripcion: str
    UnidadMedida: str
    Duracion: int = 0
