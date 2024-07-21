from pydantic import BaseModel
from typing import Optional


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
    benefitId: Optional[int]
    benefitName: Optional[str]
    catalogId: Optional[int]
    anesthesiaId: Optional[int]
    formId: int
    languageId: int
