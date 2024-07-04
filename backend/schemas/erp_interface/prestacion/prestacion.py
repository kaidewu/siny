from pydantic import BaseModel
from typing import Union


class PrestacionModel(BaseModel):
    IdCatalogo: Union[str, None]
    IdPrestacion: str
    IdFamilia: Union[str, None]
    IdSubfamilia: Union[str, None]
    Descripcion: str
    UnidadMedida: str
    Duracion: int = 0
