from pydantic import BaseModel
from typing import LiteralString


class FoinConfigurationUploadModel(BaseModel):
    title: str
    groupId: int
    actionId: int
    specialityId: int
    specialityName: str
    serviceId: int
    serviceName: str
    centerId: int
    centerName: str
    ambitId: int
    ambitName: str
    rolId: int
    rolName: str
    benefitId: int | None
    benefitName: str | None
    catalogId: int | None
    anesthesiaId: int | None
    formId: int
    languageId: int
