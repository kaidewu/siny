from pathlib import Path
import pandas
from pandas import DataFrame
import logging
from typing import Any, List, Dict
from schemas.services_specialities.services_specialities import ServicesSpecialitiesModel

logger = logging.Logger(__name__)


class ServicesSpecialitiesUpload:
    def __init__(
            self,
            sqlserver: Any,
            file_path: Path,
            environment: str = "PRE"
    ) -> None:
        if not sqlserver:
            raise ConnectionError("The connection of the pool has not been declared")

        self.sqlserver: Any = sqlserver
        self.environment: str = environment
        self.file_path: Path = file_path
        self.df_excel: DataFrame = pandas.read_excel(self.file_path, sheet_name="HOJA ESPECIALIDADES EXTERNAS")
        self.services_specialities_data: List[ServicesSpecialitiesModel] = []

        external_center: Any = None

        for index, row in self.df_excel.iterrows():
            # Validations of required data
            if pandas.isna(row["Codigo Servicio"]):
                raise ValueError(f"The column 'Codigo Servicio' in the row {index + 2} can not be empty")
            if pandas.isna(row["Nombre Servicio"]):
                raise ValueError(f"The column 'Nombre Servicio' in the row {index + 2} can not be empty")
            if pandas.isna(row["Codigo Speciality"]):
                raise ValueError(f"The column 'Codigo Speciality' in the row {index + 2} can not be empty")
            if pandas.isna(row["Nombre Speciality"]):
                raise ValueError(f"The column 'Nombre Speciality' in the row {index + 2} can not be empty")

            # Set each row values into the Model
            self.services_specialities_data.append(
                ServicesSpecialitiesModel(
                    **
                    {
                        "serviceCode": str(row["Codigo Servicio"]),
                        "serviceName": str(row["Nombre Servicio"]),
                        "specialityCode": str(row["Codigo Speciality"]),
                        "specialityName": str(row["Nombre Speciality"])
                    }
                )
            )

    def _select_orma_center_services(self, serv_id: int) -> Any:
        # GET CESE_ID AND CENT_ID FROM ORMA_CENTER_SERVICES FILTERING WITH SERVICE
        return self.sqlserver.execute_select(
            "SELECT CESE_ID, CENT_ID FROM ORMA_CENTER_SERVICES WHERE SERV_ID = ?",
            params=serv_id
        )

    def _select_total_external_centers(self) -> int:
        cent_external_total: Any = self.sqlserver.execute_select(
            "SELECT COUNT(*) FROM ORMA_CENTERS WHERE CENT_EXTERNAL = 1 AND CENT_DELETED = 0 AND 1=?", params=1
        )

        return int(cent_external_total[0][0])

    def return_services_specialities(self) -> Dict[str, str]:

        try:
            # Start BEGIN TRANSACTION
            self.sqlserver.begin()

            # Insert into ORMA_SERVICES, ORMA_CENTER_SERVICES, ORMA_SPECIALITIES AND ORMA_SERVICE_SPECIALITIES
            for service_speciality in self.services_specialities_data:
                cents_id: List[int] = []
                ceses_id: List[int] = []

                # ORMA_SERVICES
                serv_query: str = "SELECT SERV_ID FROM ORMA_SERVICES WHERE SERV_CODE = ? AND SERV_DESCRIPTION_ES = ?"

                serv_id: Any = self.sqlserver.execute_select(
                    serv_query, params=(service_speciality.serviceCode, service_speciality.serviceName)
                )

                if not serv_id:
                    self.sqlserver.execute_insert(
                        "INSERT INTO [dbo].[ORMA_SERVICES] (SERV_CODE, SERV_DELETED, SERV_DELETED_DATE, SERV_COLOUR, "
                        "SERV_LEVEL, SERV_DESCRIPTION_ES, SERV_DESCRIPTION_LT, SERV_DESCRIPTION_EN, "
                        "SERV_DESCRIPTION_OPT, SERV_SHOW_BLOCK_HOURS, SERV_PRINT_TICKET, SERV_CODE_TC, "
                        "SERV_PATIENT_CAN_SCHEDULE, SERV_SHORT_DESCRIPTION_ES, SERV_SHORT_DESCRIPTION_EN, "
                        "SERV_SHORT_DESCRIPTION_LT, SERV_SHORT_DESCRIPTION_OPT) "
                        f"VALUES (?, 0, NULL, NULL, NULL, ?, ?, ?, ?, 0, 1, NULL, 1, ?, ?, ?, ?)",
                        params=(service_speciality.serviceCode, service_speciality.serviceName,
                                service_speciality.serviceName, service_speciality.serviceName,
                                service_speciality.serviceName, service_speciality.serviceCode,
                                service_speciality.serviceCode, service_speciality.serviceCode,
                                service_speciality.serviceCode)
                    )

                    serv_id: Any = self.sqlserver.execute_select(
                        serv_query, params=(service_speciality.serviceCode, service_speciality.serviceName)
                    )

                # ORMA_CENTER_SERVICES
                cese_insert_query: str = (
                    "INSERT INTO [dbo].[ORMA_CENTER_SERVICES] (CENT_ID, SERV_ID, CESE_ORDER, CESE_DELETED, CESE_DELETED_DATE, CESE_ALLOW_DERIVATION) "
                    f"SELECT CENT_ID, ?, (SELECT ISNULL(MAX(CESE_ORDER), 0) + 1 FROM ORMA_CENTER_SERVICES), 0, NULL, 1 "
                    f"FROM ORMA_CENTERS WHERE CENT_EXTERNAL = 1 AND CENT_DELETED = 0"
                )

                cent_external_total: int = self._select_total_external_centers()
                list_cese_cent_id: Any = self._select_orma_center_services(serv_id=int(serv_id[0][0]))

                if list_cese_cent_id:
                    for cese_id, cent_id in list_cese_cent_id:
                        ceses_id.append(cese_id)
                        cents_id.append(cent_id)

                    if cents_id:
                        cese_insert_query += f" AND CENT_ID NOT IN ({", ".join(f"'{cent}'" for cent in cents_id)})"
                if cent_external_total != list_cese_cent_id.__len__():

                    self.sqlserver.execute_insert(
                        cese_insert_query, params=int(serv_id[0][0])
                    )

                if not self._select_orma_center_services(serv_id=int(serv_id[0][0])):
                    raise Exception(f"SQL Error: Not found any CESE_ID in ORMA_CENTER_SERVICES with the service: "
                                    f"'{int(serv_id[0][0])}'")

                # ORMA_SPECIALITIES
                spec_query: str = "SELECT SPEC_ID FROM ORMA_SPECIALITIES WHERE SPEC_CODE = ? AND SPEC_DESCRIPTION_ES = ?"

                spec_id: Any = self.sqlserver.execute_select(
                    spec_query, params=(service_speciality.specialityCode, service_speciality.specialityName)
                )

                if not spec_id:
                    self.sqlserver.execute_insert(
                        "INSERT INTO [dbo].[ORMA_SPECIALITIES] (SPEC_ORDER, SPEC_DELETED, SPEC_DELETED_DATE, SPEC_EDITABLE, SPEC_DESCRIPTION_ES, SPEC_DESCRIPTION_LT, SPEC_DESCRIPTION_EN, SPEC_DESCRIPTION_OPT, SPEC_CODE, ORSP_ID) "
                        f"VALUES ((SELECT ISNULL(MAX(SPEC_ORDER), 0) + 1 FROM ORMA_SPECIALITIES), 0, NULL, 1, ?, ?, ?, ?, ?, NULL);",
                        params=(service_speciality.specialityName, service_speciality.specialityName,
                                service_speciality.specialityName, service_speciality.specialityName,
                                service_speciality.specialityCode)
                    )

                    spec_id: Any = self.sqlserver.execute_select(
                        spec_query, params=(service_speciality.specialityCode, service_speciality.specialityName)
                    )

                # ORMA_SERVICE_SPECIALITIES
                cssp_select_query: str = "SELECT COUNT(*) FROM ORMA_SERVICE_SPECIALITIES WHERE SPEC_ID = ? "

                cssp_id: Any = self.sqlserver.execute_select(
                    cssp_select_query,
                    params=(int(spec_id[0][0]))
                )

                if int(cssp_id[0][0]) != len(ceses_id):
                    self.sqlserver.execute_insert(
                        "INSERT INTO [dbo].[ORMA_SERVICE_SPECIALITIES] (CESE_ID, SPEC_ID, CSSP_DELETED, CSSP_DELETED_DATE) "
                        f"SELECT CESE_ID, ?, 0, NULL "
                        f"FROM ORMA_CENTER_SERVICES "
                        f"WHERE SERV_ID = ? AND CESE_ID IN ({", ".join(f"'{cese_id}'" for cese_id in ceses_id)})",
                        params=(int(spec_id[0][0]), int(serv_id[0][0]))
                    )

            # COMMIT TRANSACTION
            self.sqlserver.commit()

            return {
                "servicesCode": ", ".join(
                    f"'{service_speciality.serviceCode}'" for service_speciality in self.services_specialities_data),
                "servicesName": ", ".join(
                    f"'{service_speciality.serviceName}'" for service_speciality in self.services_specialities_data),
                "specialitiesCode": ", ".join(
                    f"'{service_speciality.specialityCode}'" for service_speciality in self.services_specialities_data),
                "specialitiesName": ", ".join(
                    f"'{service_speciality.specialityName}'" for service_speciality in self.services_specialities_data)
            }
        except Exception as e:
            # ROLLBACK TRANSACTION
            self.sqlserver.rollback()
            raise Exception(str(e))
