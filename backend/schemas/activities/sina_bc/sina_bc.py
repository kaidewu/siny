from pydantic import BaseModel
from typing import Optional


class ActivitiesNoPassSINABCModel(BaseModel):
    centerName: Optional[str]
    appointmentDate: Optional[str]
    insuranceName: Optional[str]
    collectiveName: Optional[str]
    nhc: Optional[str]
    episodeCode: Optional[str]
    patientFullName: Optional[str]
    benefitCode: Optional[str]
    benefitName: Optional[str]
    patientIdentifier: Optional[str]
    authorizationLevel: Optional[int]
    proposalState: Optional[str]
    activityState: Optional[str]
    professionalRealized: Optional[str]
    professionalInformed: Optional[str]
    procedureCode: Optional[str]


class IntegrationsErrorModel(BaseModel):
    messageCode: Optional[str]
    messageCreated: Optional[str]
    messageType: Optional[str]
    errorMessage: Optional[str]
