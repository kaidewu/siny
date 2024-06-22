from pydantic import BaseModel


class SubfamiliaModel(BaseModel):
    IdSubfamilia: str
    Descripcion: str
    IdFamilia: str
