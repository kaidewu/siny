from pydantic import BaseModel


class PrestacionModel(BaseModel):
    IdCatalogo: str = "CAT01",
    IdPrestacion: str = None,
    IdFamilia: str = None,
    IdSubfamilia: str = None,
    Descripcion: str = None,
    UnidadMedida: str = "UND",
    Duracion: int = 0
