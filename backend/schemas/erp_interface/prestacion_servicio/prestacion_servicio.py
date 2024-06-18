from pydantic import BaseModel


class PrestacionServicioModel(BaseModel):
    IdCatalogo: str = "CAT01",
    IdPrestacion: str = None,
    IdServicio: str = None,
    Agendable: bool = True,
    Duracion: int = 0,
    CodCentro: str = None,
    Departamental: str = IdPrestacion,
    Incremento: int = 10,
    Decremento: int = 10

