from pydantic import BaseModel


class OrigenPrestacionModel(BaseModel):
    Codcentro: str = None,
    IdAmbito: str = None,
    IdServicio: str = None,
    IdCatalogo: str = None,
    IdPrestacion: str = None
