import logging
from typing import Union, Any
from datetime import datetime
from functools import cache
from schemas.activities.sina_bc.sina_bc import ActivitiesNoPassSINABCModel, IntegrationsErrorModel
from .sina_bc_queries import get_activities_no_passed_sina_bc, get_integrations_error_per_patient

logger = logging.Logger(__name__)


class SINA_BC:
    def __init__(
            self,
            appointment_start_date: str,
            appointment_end_date: str,
            sqlserver: Any
    ) -> None:
        if not sqlserver:
            raise ConnectionError("The connection of the pool has not been declared")

        self.sqlserver: Any = sqlserver
        self.appointment_start_date: Union[datetime | None] = datetime.fromisoformat(
            appointment_start_date.replace("Z", "")) if appointment_start_date else None
        self.appointment_end_date: Union[datetime | None] = datetime.fromisoformat(
            appointment_end_date.replace("Z", "")) if appointment_end_date else None

    @cache
    def _get_activities(self) -> Any:
        query: str = get_activities_no_passed_sina_bc()

        if not self.appointment_start_date and not self.appointment_end_date:
            query += " AND aa.APPO_START_DATE BETWEEN DATEADD(DD,-14,GETDATE()) AND DATEADD(DD,-7,GETDATE())"
        else:
            if self.appointment_start_date:
                query += " AND aa.APPO_START_DATE >= ?"

            if self.appointment_end_date:
                query += " AND aa.APPO_START_DATE <= ?"

        return self.sqlserver.execute_select(
            query,
            params=tuple(filter(
                lambda activity: activity is not None,
                (
                    self.appointment_start_date,
                    self.appointment_end_date
                )
            ))
        )

    @cache
    def _get_integrations_error(self, nhc: str, proc_code: str) -> Any:
        query: str = get_integrations_error_per_patient()

        if not self.appointment_start_date and not self.appointment_end_date:
            query += " AND iii.INTI_CREATED_DATE BETWEEN DATEADD(DD,-14,GETDATE()) AND GETDATE()"
        else:
            if self.appointment_start_date:
                query += f" AND iii.INTI_CREATED_DATE >= ?"

            if self.appointment_end_date:
                query += f" AND iii.INTI_CREATED_DATE <= ?"

        return self.sqlserver.execute_select(
            query,
            params=tuple(filter(
                lambda integration: integration is not None,
                (
                    nhc,
                    proc_code,
                    self.appointment_start_date,
                    self.appointment_end_date
                )
            ))
        )

    def _set_activities_model(self) -> list[ActivitiesNoPassSINABCModel]:
        list_activities: list[ActivitiesNoPassSINABCModel] = []

        for activity_patient in self._get_activities():
            list_activities.append(ActivitiesNoPassSINABCModel(
                **
                {
                    "centerName": str(activity_patient[0]),
                    "appointmentDate": activity_patient[1].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if activity_patient[1] else None,
                    "insuranceName": str(activity_patient[2]),
                    "collectiveName": str(activity_patient[3]),
                    "nhc": str(activity_patient[4]),
                    "episodeCode": str(activity_patient[5]),
                    "patientFullName": str(activity_patient[6]),
                    "benefitCode": str(activity_patient[7]),
                    "benefitName": str(activity_patient[8]),
                    "patientIdentifier": str(activity_patient[9]),
                    "authorizationLevel": int(activity_patient[10]),
                    "proposalState": str(activity_patient[11]),
                    "activityState": str(activity_patient[12]),
                    "professionalRealized": str(activity_patient[13]),
                    "professionalInformed": str(activity_patient[14]),
                    "procedureCode": str(activity_patient[15])
                }
            ))

        return list_activities

    def _set_integrations_error_model(self, nhc: str, proc_code: str) -> dict:

        integrations_error_json: dict = {}
        _get_integrations_error: Any = self._get_integrations_error(nhc=nhc, proc_code=proc_code)

        if _get_integrations_error:
            for integration in _get_integrations_error:
                integrations_error = IntegrationsErrorModel(
                    **
                    {
                        "messageCode": str(integration[0]),
                        "messageCreated": integration[1].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if integration[1] else None,
                        "messageType": str(integration[2]),
                        "errorMessage": str(integration[3])
                    }
                )
                integrations_error_json = {
                    "messageCode": integrations_error.messageCode,
                    "messageCreated": integrations_error.messageCreated,
                    "messageType": integrations_error.messageType,
                    "errorMessage": integrations_error.errorMessage
                }

        return integrations_error_json

    def return_patients_activities(self) -> dict:

        results_json: dict = {}

        for activity_patient in self._set_activities_model():
            if activity_patient.nhc not in results_json:
                results_json[activity_patient.nhc] = {
                    "patientFullName": activity_patient.patientFullName,
                    "patientIdentifier": activity_patient.patientIdentifier
                }

            if activity_patient.procedureCode not in results_json[activity_patient.nhc]:
                results_json[activity_patient.nhc].update({
                    activity_patient.procedureCode: []
                })

            results_json[activity_patient.nhc][activity_patient.procedureCode].append(
                {
                    "centerName": activity_patient.centerName,
                    "appointmentDate": activity_patient.appointmentDate,
                    "insuranceName": activity_patient.insuranceName,
                    "collectiveName": activity_patient.collectiveName,
                    "episodeCode": activity_patient.episodeCode,
                    "benefitCode": activity_patient.benefitCode,
                    "benefitName": activity_patient.benefitName,
                    "authorizationLevel": activity_patient.authorizationLevel,
                    "proposalState": activity_patient.proposalState,
                    "activityState": activity_patient.activityState,
                    "professionalRealized": activity_patient.professionalRealized,
                    "professionalInformed": activity_patient.professionalInformed,
                    "integrationError": self._set_integrations_error_model(
                        nhc=activity_patient.nhc,
                        proc_code=activity_patient.procedureCode
                    )
                }
            )
        return results_json
