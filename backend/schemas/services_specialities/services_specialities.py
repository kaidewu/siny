from pydantic import BaseModel


class ServicesSpecialitiesModel(BaseModel):
    serviceCode: str
    serviceName: str
    specialityCode: str
    specialityName: str

