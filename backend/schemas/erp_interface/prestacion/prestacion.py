from pydantic import BaseModel
from typing import Union


class PrestacionModel(BaseModel):
    IdCatalogo: Union[str, None] = None,
    IdPrestacion: Union[str, None] = None,
    IdFamilia: Union[str, None] = None,
    IdSubfamilia: Union[str, None] = None,
    Descripcion: Union[str, None] = None,
    UnidadMedida: Union[str, None] = None,
    Duracion: int = 0
