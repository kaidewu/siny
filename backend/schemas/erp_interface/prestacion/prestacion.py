from pydantic import BaseModel
from typing import Optional


class PrestacionModel(BaseModel):
    IdCatalogo: Optional[str]
    IdPrestacion: str
    IdFamilia: Optional[str]
    IdSubfamilia: Optional[str]
    Descripcion: str
    UnidadMedida: str
    Duracion: int = 0
