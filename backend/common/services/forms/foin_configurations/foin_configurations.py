import logging
import pandas
from pandas import DataFrame
from typing import Any, List, Tuple, Dict
from pathlib import Path
from common.database.sqlserver import sqlserver_db_pool as sqlserver
from schemas.forms.foin_configurations.foin_configurations import FoinConfigurationUploadModel

logger = logging.Logger(__name__)


class FoinConfigurationUpload:
    def __init__(
            self,
            file_path: Path,
            environment: str = "PRE"
    ) -> None:
        self.sqlserver: Any = sqlserver
        self.excel_read: DataFrame = pandas.read_excel(Path(file_path).resolve(), sheet_name="HOJA FORMULARIO")
        self.data_json: List[FoinConfigurationUploadModel] = []
        self.environment: str  = environment

        for index, row in self.excel_read.iterrows():
            # Declares of variables
            index = index + 2
            group_id: int
            action_id: int
            benefit_id: int | None = None
            benefit_name: str | None = None
            speciality_id: int
            speciality_name: str
            service_id: int
            service_name: str
            ambit_id: int
            rol_id: int = 0
            catalog_id: int | None = None
            anesthesia_id: int | None = None
            lang_id: int
            form_id: int

            # Validations of Excel rows
            if pandas.isna(row["Titulo"]):
                raise ValueError(f"Line {index}: The parameter 'Titulo' can not be empty.")

            if pandas.isna(row["Grupo"]):
                raise ValueError(f"Line {index}: The parameter 'Grupo' can not be empty.")
            else:
                # Search the group ID
                group_query: Any = self.sqlserver.execute_select(
                    "SELECT DISTINCT COGR_ID FROM [dbo].[FOIN_CONF_GROUPS] "
                    "WHERE COGR_DELETED = 0 AND COGR_NAME = ?", params=str(row["Grupo"])
                )
                if not group_query:
                    raise ValueError(f"The group '{str(row["Grupo"])}' do not exists.")
                group_id = int(group_query[0][0])

            if pandas.isna(row["Accion"]):
                raise ValueError(f"Line {index}: The parameter 'Accion' can not be empty.")
            else:
                # Search the action ID
                action_query: Any = self.sqlserver.execute_select(
                    "SELECT DISTINCT COAC_ID FROM [dbo].[FOIN_CONF_ACTIONS] "
                    "WHERE COAC_DELETED = 0 AND COAC_DESCRIPTION_ES = ?", params=str(row["Accion"])
                )
                if not action_query:
                    raise ValueError(f"The action '{str(row["Accion"])}' do not exists.")
                action_id = int(action_query[0][0])

            if str(row["Grupo"]) == "Consentimientos Informados por Prestación":
                if pandas.isna(row["Codigo Prestacion"]):
                    raise ValueError(f"Line {index}: The parameter 'Codigo Prestacion' can not be empty.")
                else:
                    # Search the benefit name
                    benefit_query: Any = self.sqlserver.execute_select(
                        "SELECT DISTINCT BENE_ID, BENE_NAME FROM [dbo].[ORMA_BENEFITS] "
                        "WHERE BENE_DELETED = 0 AND BENE_ACTIVE = 1 "
                        "AND BENE_CODE = ?", params=str(int(float(row["Codigo Prestacion"])))
                    )
                    if not benefit_query:
                        raise ValueError(f"The benefit '{str(row["Codigo Prestacion"])}' do not exists.")

                    benefit_id, benefit_name = (int(benefit_query[0][0]), str(benefit_query[0][1]))

            if str(row["Grupo"]) == "Consentimientos Informados por Procedimiento":
                if pandas.isna(row["Codigo Procedimiento"]):
                    raise ValueError(f"Line {index}: The parameter 'Codigo Procedimiento' can not be empty.")
                else:
                    # Search the catalog ID
                    catalog_query: Any = self.sqlserver.execute_select(
                        "SELECT DISTINCT cc.COCA_ID FROM [dbo].[CODR_CATALOGS] cc "
                        "WHERE cc.COCA_DELETED = 0 AND cc.COCA_CODE = ?",
                        params=str(row["Codigo Procedimiento"])
                    )
                    if not catalog_query:
                        raise ValueError(f"The catalog '{str(row["Codigo Procedimiento"])}' do not exists.")
                    catalog_id = int(catalog_query[0][0])

            if str(row["Grupo"]) == "Consentimientos Informados por Tipo de Anestesia":
                if pandas.isna(row["Tipo Anestesia"]):
                    raise ValueError(f"Line {index}: The parameter 'Tipo Anestesia' can not be empty.")
                else:
                    # Search the anesthesia ID
                    anesthesia_query: Any = self.sqlserver.execute_select(
                        "SELECT DISTINCT sat.ANTY_ID FROM [dbo].[SURG_ANESTHESIA_TYPES] sat "
                        "WHERE sat.ANTY_DELETED = 0 AND sat.ANTY_DESCRIPTION_ES = ?",
                        params=str(row["Tipo Anestesia"])
                    )
                    if not anesthesia_query:
                        raise ValueError(f"The anesthesia '{str(row["Tipo Anestesia"])}' do not exists.")
                    anesthesia_id = int(anesthesia_query[0][0])

            if pandas.isna(row["Servicio"]):
                raise ValueError(f"Line {index}: The parameter 'Servicio' can not be empty.")
            else:
                # Search the service Code
                service_query: Any = self.sqlserver.execute_select(
                    "SELECT DISTINCT os.SERV_ID, os.SERV_DESCRIPTION_ES FROM [dbo].[ORMA_SERVICES] os "
                    "INNER JOIN [dbo].[ERP_Servicio] s ON s.IdServicio COLLATE Modern_Spanish_CI_AI = os.SERV_CODE AND s.Activo = 1 "
                    "WHERE os.SERV_DELETED = 0 AND CAST(s.Descripcion AS NVARCHAR(MAX)) = ?",
                    params=str(row["Servicio"])
                )
                if not service_query:
                    raise ValueError(f"The service '{str(row["Servicio"])}' do not exists.")
                service_id, service_name = (int(service_query[0][0]), str(service_query[0][1]))

            if pandas.isna(row["Ambito"]):
                raise ValueError(f"Line {index}: The parameter 'Ambito' can not be empty.")
            else:
                # Search the ambit Code
                ambit_query: Any = self.sqlserver.execute_select(
                    "SELECT DISTINCT AMBI_ID FROM [dbo].[ORMA_AMBITS] WHERE AMBI_DELETED = 0 "
                    "AND AMBI_DESCRIPTION_ES = ?",
                    params=str(row["Ambito"])
                )
                if not ambit_query:
                    raise ValueError(f"The ambit '{str(row["Ambito"])}' do not exists.")
                ambit_id = int(ambit_query[0][0])

            if not pandas.isna(row["Rol"]):
                rol_query: Any = self.sqlserver.execute_select(
                    "SELECT DISTINCT SROL_ID FROM [dbo].[SECU_ROLES] WHERE SROL_DELETED = 0 AND SROL_DESCRIPTION_ES = ?",
                    params=str(row["Rol"])
                )
                if not rol_query:
                    raise ValueError(f"The rol '{str(row["Rol"])}' do not exists.")
                rol_id = int(rol_query[0][0])

            # If the center is not empty, search the Center Code. Otherwise, bring all center code non-external
            centers_id: List[Tuple[int, str]] = []
            if not pandas.isna(row["Centro"]):
                center_query: Any = self.sqlserver.execute_select(
                    "SELECT DISTINCT CENT_ID, CENT_NAME FROM [dbo].[ORMA_CENTERS] "
                    "WHERE CENT_DELETED = 0 AND CENT_EXTERNAL = 0 AND CENT_NAME = ?",
                    params=str(row["Centro"])
                )
                if not center_query:
                    raise ValueError(f"The center '{str(row["Centro"])}' do not exists.")
                centers_id.append((int(center_query[0][0]), str(center_query[0][1])))
            else:
                center_query: Any = self.sqlserver.execute_select(
                    "SELECT DISTINCT CENT_ID, CENT_NAME FROM [dbo].[ORMA_CENTERS] "
                    "WHERE CENT_DELETED = 0 AND CENT_EXTERNAL = 0 AND 1=?",
                    params=1
                )
                if not center_query:
                    raise ValueError(f"Not found any centers.")

                for center in center_query:
                    centers_id.append((int(center[0]), str(center[1])))

            if pandas.isna(row["Formulario"]):
                raise ValueError(f"Line {index}: The parameter 'Formulario' can not be empty.")
            else:
                # Check if exists
                form_query: Any = self.sqlserver.execute_select(
                    "SELECT FORM_ID FROM [dbo].[FORM_FORMS] WHERE FORM_NAME = ?",
                    params=str(row["Formulario"])
                )
                if not form_query:
                    if self.environment == "PRO":
                        raise ValueError(f"Line {index}: The form: 'Formulario' not exists.")
                    else:
                        self.sqlserver.execute_insert(
                            "INSERT INTO [dbo].[FORM_FORMS] VALUES (?, 0, 0, 4, 1, 1);",
                            params=str(row["Formulario"])
                        )

                form_id = int(form_query[0][0])

            if pandas.isna(row["Idioma"]):
                raise ValueError(f"Line {index}: The parameter 'Idioma' can not be empty.")
            else:
                # Search language code
                lang_query: Any = self.sqlserver.execute_select(
                    "SELECT DISTINCT LANG_ID FROM [dbo].[I18N_LANGUAGES] WHERE LANG_DESCRIPTION_ES = ?",
                    params=str(row["Idioma"])
                )
                if not lang_query:
                    raise ValueError(f"Line {index}: The language: 'Idioma' not exists.")
                lang_id = int(lang_query[0][0])

            # Charge all the Excel information into the Model
            for center_id, center_name in centers_id:
                # Search speciality from ORMA_SPECIALITIES
                speciality_query: Any = self.sqlserver.execute_select(
                    "SELECT DISTINCT os.SPEC_ID, os.SPEC_DESCRIPTION_ES FROM [dbo].[ORMA_SPECIALITIES] os "
                    "INNER JOIN [dbo].[ORMA_SERVICE_SPECIALITIES] oss ON oss.SPEC_ID = os.SPEC_ID AND oss.CSSP_DELETED = 0 "
                    "INNER JOIN [dbo].[ORMA_CENTER_SERVICES] ocs ON ocs.CESE_ID = oss.CESE_ID AND ocs.CESE_DELETED = 0 "
                    "WHERE os.SPEC_DELETED = 0 AND ocs.CENT_ID = ? AND ocs.SERV_ID = ?",
                    params=(
                        center_id,
                        service_id
                    )
                )
                if not speciality_query:
                    raise ValueError(f"Not found any speciality with '{center_name}' and '{str(row["Servicio"])}'")

                speciality_id, speciality_name = (int(speciality_query[0][0]), str(speciality_query[0][1]))

                self.data_json.append(
                    FoinConfigurationUploadModel(**
                     {
                         "title": str(row["Titulo"]),
                         "groupId": group_id,
                         "actionId": action_id,
                         "specialityId": speciality_id,
                         "specialityName": speciality_name,
                         "serviceId": service_id,
                         "serviceName": service_name,
                         "centerId": int(center_id),
                         "centerName": str(row["Centro"]),
                         "ambitId": ambit_id,
                         "ambitName": str(row["Ambito"]),
                         "rolId": rol_id,
                         "rolName": str(row["Rol"]) if not pandas.isna(row["Rol"]) else "NONE",
                         "benefitId": benefit_id if benefit_id != 0 else None,
                         "benefitName": benefit_name if benefit_name else None,
                         "catalogId": catalog_id,
                         "anesthesiaId": anesthesia_id,
                         "formId": form_id,
                         "languageId": lang_id
                     }
                    )
                )

    def _insert_auditories_foin_configurations(self, coco_id: int):
        self.sqlserver.execute_insert(
            "INSERT INTO [dbo].[AUDI_FOIN_CONF_CONFIGURATIONS] (COCO_ID, AUDI_REVISION_ID, AUDI_REVISION_TYPE, AUDI_END_REVISION_ID, AUDI_REVISION_END_DATE, COCO_TITLE, COGR_ID, COAC_ID, CENTER_ID, CENTER_NAME, AMBIT_ID, AMBIT_NAME, SPECIALITY_ID, SPECIALITY_NAME, SERVICE_ID, SERVICE_NAME, ROL_ID, ROL_NAME, PRESTATION_ID, PRESTATION_NAME, CLINIC_ACTIVITY, COCO_SIGN_PATI, COCO_SIGN_PROF, COCO_CLOSE_ATTENTION, COCO_NEW_WHEN_SIGNED, CPTE_ID, COCA_ID, ANTY_ID, COCO_DELETED, COCO_DELETED_DATE) "
            "SELECT COCO_ID, 1, 1, NULL, NULL, COCO_TITLE, COGR_ID, COAC_ID, CENTER_ID, CENTER_NAME, AMBIT_ID, AMBIT_NAME, SPECIALITY_ID, SPECIALITY_NAME, SERVICE_ID, SERVICE_NAME, ROL_ID, ROL_NAME, PRESTATION_ID, PRESTATION_NAME, 1, COCO_SIGN_PATI, COCO_SIGN_PROF, COCO_CLOSE_ATTENTION, COCO_NEW_WHEN_SIGNED, CPTE_ID, COCA_ID, ANTY_ID, COCO_DELETED, COCO_DELETED_DATE "
            "FROM [dbo].[FOIN_CONF_CONFIGURATIONS] "
            "WHERE COCO_ID = ?",
            params=coco_id
        )

    def _insert_foin_form_language(self, coco_id: int, form_id: int, language_id: int):
        self.sqlserver.execute_insert(
            "INSERT INTO [dbo].[FOIN_CONF_FORMS_LANGUAGES] (COCO_ID, FORM_ID, LANG_ID) "
            "VALUES (?, ?, ?)",
            params=(coco_id, form_id, language_id)
        )

    def _insert_foin_configurations(self) -> List[str]:
        coco_titles: List[str] = []

        for configuration in self.data_json:
            params_insert: tuple = (
                configuration.title,
                configuration.groupId,
                configuration.actionId,
                configuration.centerId,
                configuration.centerName,
                configuration.ambitId,
                configuration.ambitName,
                configuration.specialityId,
                configuration.specialityName,
                configuration.serviceId,
                configuration.serviceName,
                configuration.rolId,
                configuration.rolName,
                configuration.benefitId,
                configuration.benefitName,
                configuration.catalogId,
                configuration.anesthesiaId
            )

            self.sqlserver.execute_insert(
                "INSERT INTO [dbo].[FOIN_CONF_CONFIGURATIONS] (COCO_TITLE, COGR_ID, COAC_ID, CENTER_ID, CENTER_NAME, AMBIT_ID, AMBIT_NAME, SPECIALITY_ID, SPECIALITY_NAME, SERVICE_ID, SERVICE_NAME, ROL_ID, ROL_NAME, PRESTATION_ID, PRESTATION_NAME, COCO_SIGN_PATI, COCO_SIGN_PROF, COCO_CLOSE_ATTENTION, COCO_NEW_WHEN_SIGNED, CPTE_ID, COCA_ID, ANTY_ID, COCO_DELETED, COCO_DELETED_DATE) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 1, 0, NULL, ?, ?, 0, NULL);",
                params=params_insert
            )

            params_foin_configurations_select: tuple = tuple(filter(
                lambda foin_configurations: foin_configurations is not None,
                (
                    configuration.title,
                    configuration.groupId,
                    configuration.actionId,
                    configuration.centerId,
                    configuration.centerName,
                    configuration.serviceId,
                    configuration.serviceName,
                    configuration.ambitId,
                    configuration.ambitName,
                    configuration.rolId,
                    configuration.rolName,
                    configuration.benefitId if configuration.benefitId else None,
                    configuration.benefitName if configuration.benefitName else None,
                    configuration.catalogId if configuration.catalogId else None,
                    configuration.anesthesiaId if configuration.anesthesiaId else None
                )
            ))

            select_foin_configurations_query: str = (
                "SELECT TOP 1 COCO_ID FROM [dbo].[FOIN_CONF_CONFIGURATIONS] WHERE COCO_TITLE = ? AND COGR_ID = ? "
                "AND COAC_ID = ? AND CENTER_ID = ? AND CENTER_NAME = ? AND SERVICE_ID = ? AND SERVICE_NAME = ? "
                "AND AMBIT_ID = ? AND AMBIT_NAME = ? AND ROL_ID = ? AND ROL_NAME = ?"
            )

            if configuration.benefitId:
                select_foin_configurations_query += " AND PRESTATION_ID = ? AND PRESTATION_NAME = ?"

            if configuration.catalogId:
                select_foin_configurations_query += " AND COCA_ID = ?"

            if configuration.anesthesiaId:
                select_foin_configurations_query += " AND ANTY_ID = ?"

            select_foin_configurations_query += " ORDER BY COCO_ID DESC"

            coco_id_query: Any = self.sqlserver.execute_select(
                select_foin_configurations_query, params=params_foin_configurations_select
            )

            coco_id: int = coco_id_query[0][0]

            # Insert to AUDI_FOIN_CONF_CONFIGURATIONS
            if not isinstance(coco_id, int):
                raise Exception("The COCO_ID is not an integer")
            self._insert_auditories_foin_configurations(coco_id=coco_id)

            coco_titles.append(configuration.title)

            # Insert to FOIN_CONF_FORMS_LANGUAGES
            foin_conf_forms_languages_query: Any = self.sqlserver.execute_select(
                "SELECT 1 FROM [dbo].[FOIN_CONF_FORMS_LANGUAGES] fcfl "
                "WHERE fcfl.LANG_ID = ? AND fcfl.COCO_ID = ?",
                params=(
                    configuration.languageId,
                    coco_id
                )
            )

            if not foin_conf_forms_languages_query:
                self.sqlserver.execute_insert(
                    "INSERT INTO [dbo].[FOIN_CONF_FORMS_LANGUAGES] (COCO_ID, FORM_ID, LANG_ID) "
                    "VALUES (?, ?, ?);",
                    params=(coco_id, configuration.formId, configuration.languageId)
                )

        return coco_titles

    def return_insert_foin_configurations(self) -> Dict:
        try:
            self.sqlserver.begin()

            coco_titles: List[str] = self._insert_foin_configurations()

        except Exception as e:
            self.sqlserver.rollback()
            raise Exception(str(e))
        finally:
            self.sqlserver.commit()

        return {
            "foinConfigurations": ", ".join(f"'{text}'" for text in list(set(coco_titles)))
        }
