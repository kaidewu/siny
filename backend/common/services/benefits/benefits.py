from pathlib import Path
import pandas
import logging
from typing import Union, Any, List, Dict, Tuple
from settings.settings import settings
from common.database.sqlserver import sqlserver_db_pool as sqlserver
from datetime import datetime

logger = logging.Logger(__name__)


class BenefitsUpload:
    def __init__(
            self,
            environment: str,
            filename: str
    ) -> None:
        """
        Class BenefitsUpload read the Excel provided and loading the ERP_Prestacion, ERP_PrestacionServicio and
        ERP_OrigenPrestacion endpoint to data loading massively
        :param filename: the name of the Excel file
        """
        self.sqlserver: Any = sqlserver
        self.file_read = pandas.read_excel(Path(settings.TEMP_PATH).joinpath(filename), sheet_name="HOJA PRESTACION")
        self.environment: str = environment

    def _to_erp_interface_json(self) -> Tuple[List, List, List]:
        from schemas.erp_interface.prestacion.prestacion import PrestacionModel
        from schemas.erp_interface.prestacion_servicio.prestacion_servicio import PrestacionServicioModel
        from schemas.erp_interface.origen_prestacion.origen_prestacion import OrigenPrestacionModel

        # Defined JSON variables
        erp_prestacion_json: List = []
        erp_prestacionservicio_json: List = []
        erp_origenprestacion_json: List = []

        for index, row in self.file_read.iterrows():

            # Validation that required field are not NULL
            if pandas.isna(row["Codigo Prestacion"]):
                raise Exception("Codigo Prestacion in the row {index} can't no be empty")

            if pandas.isna(row["Nombre Prestacion"]):
                raise Exception("Nombre Prestacion in the row {index} can't no be empty")

            if pandas.isna(row["Servicio"]):
                raise Exception("Servicio in the row {index} can't no be empty")

            if pandas.isna(row["Ambito"]):
                raise Exception("Ambito in the row {index} can't no be empty")

            service_query: Any = self.sqlserver.execute_select(
                "SELECT s.IdServicio FROM [sinasuite].[dbo].[ERP_Servicio] s "
                "WHERE s.Activo = 1 AND CAST(s.Descripcion AS NVARCHAR(MAX)) = ?", params=str(row["Servicio"])
            )

            if not service_query:
                raise Exception(f"The service {str(row['Servicio'])} in the row {index} doesn't exists. Please, verify and try again.")

            service_code: str = str(service_query[0][0])

            if not pandas.isna(row["Unidad Medida"]):
                unit_validation: Any = self.sqlserver.execute_select(
                    "SELECT 1 FROM [sinasuite].[dbo].[PARA_MEASUREMENT_UNITS] "
                    "WHERE MEUN_DELETED = 0 AND MEUN_CODE = ?", params=str(row["Unidad Medida"])
                )

                if not unit_validation:
                    raise ValueError(f"The column 'Unidad Medida' in the row {index} doesn't exists. Please, verify and try again.")

            # Set each Model with the Excel data
            # Creation of ERP_Prestacion JSON
            erp_prestacion_json.append(
                PrestacionModel(**
                    {
                        "IdCatalogo": str(row["Catalogo"]) if not pandas.isna(row["Catalogo"]) else None,
                        "IdPrestacion": str(row["Codigo Prestacion"]),
                        "IdFamilia": str(row["Codigo Familia"]),
                        "IdSubfamilia": str(row["Codigo Subfamilia"]),
                        "Descripcion": str(row["Nombre Prestacion"]),
                        "UnidadMedida": str(row["Unidad Medida"]) if not pandas.isna(
                            row["Unidad Medida"]) else None,
                        "Duracion": int(row["Duracion"]) if not pandas.isna(row["Duracion"]) else 0,
                    }
                )
            )

            # Creation of ERP_PrestacionServicio JSON
            centers_code: List = []

            if pandas.isna(row["Centro"]):
                centers_query: Any = self.sqlserver.execute_select(
                    "SELECT oc.CENT_CODE FROM [sinasuite].[dbo].[ORMA_CENTERS] oc "
                    "WHERE oc.CENT_DELETED = 0 AND oc.CENT_EXTERNAL = 0 AND 1=?", params=1
                )
                for center in centers_query:
                    centers_code.append(str(center[0]))
            else:
                centers_query: Any = self.sqlserver.execute_select(
                    "SELECT oc.CENT_CODE FROM [sinasuite].[dbo].[ORMA_CENTERS] oc "
                    "WHERE oc.CENT_DELETED = 0 AND oc.CENT_EXTERNAL = 0 AND oc.CENT_NAME = ?", params=str(row["Centro"])
                )
                centers_code.append(str(centers_query[0][0]))

            for center_code in centers_code:
                erp_prestacionservicio_json.append(
                    PrestacionServicioModel(**
                        {
                            "IdCatalogo": str(row["Catalogo"]) if not pandas.isna(row["Catalogo"]) else None,
                            "IdPrestacion": str(row["Codigo Prestacion"]),
                            "IdServicio": service_code,
                            "Agendable": True,
                            "Duracion": int(row["Duracion"]) if not pandas.isna(row["Duracion"]) else 0,
                            "CodCentro": center_code,
                            "Departamental": str(row["Codigo Prestacion"]),
                            "Incremento": int(row["Duracion"]) + 10 if not pandas.isna(
                                row["Duracion"]) else 0,
                            "Decremento": int(10)
                        }
                    )
                )

            ambits_query: Any = self.sqlserver.execute_select(
                "SELECT oa.AMBI_CODE FROM [sinasuite].[dbo].[ORMA_AMBITS] oa "
                "WHERE oa.AMBI_DELETED = 0 AND oa.AMBI_DESCRIPTION_ES = ?", params=str(row["Ambito"])
            )
            if not ambits_query:
                raise Exception("Ambito not supported")

            ambits_code: str = str(ambits_query[0][0])

            # Creation of ERP_PrestacionServicio JSON
            for center_code in centers_code:
                erp_origenprestacion_json.append(
                    OrigenPrestacionModel(**
                        {
                            "CodCentro": center_code,
                            "IdAmbito": ambits_code,
                            "IdCatalogo": str(row["Catalogo"]) if not pandas.isna(row["Catalogo"]) else None,
                            "IdPrestacion": str(row["Codigo Prestacion"])
                        }
                    )
                )

        return erp_prestacion_json, erp_prestacionservicio_json, erp_origenprestacion_json

    def return_erp_interface_benefits_insertions(self):
        from common.services.erp_interface.prestacion.prestacion import InsertERPPrestacion
        from common.services.erp_interface.prestacion_servicio.prestacion_servicio import InsertERPPrestacionServicio
        from common.services.erp_interface.origen_prestacion.origen_prestacion import InsertERPOrigenPrestacion

        erp_prestacion_json, erp_prestacionservicio_json, erp_origenprestacion_json = self._to_erp_interface_json()
        returns_codes: Dict = {}

        insert_erp_prestacion = InsertERPPrestacion(
            prestacion_body=erp_prestacion_json
        )

        returns_codes.update(insert_erp_prestacion.insert_prestacion())

        insert_erp_prestacionservicio = InsertERPPrestacionServicio(
            prestacionservicio_body=erp_prestacionservicio_json
        )

        returns_codes.update(insert_erp_prestacionservicio.insert_prestacionservicio())

        insert_erp_origenprestacion = InsertERPOrigenPrestacion(
            origenprestacion_body=erp_origenprestacion_json
        )

        returns_codes.update(insert_erp_origenprestacion.insert_origenprestacion())

        if self.environment != "PRO":
            try:
                self.sqlserver.begin()

                self.sqlserver.execute_procedures(
                    Path(settings.RESOURCES_PATH).joinpath("stored procedures/PROC_GET_NAV_BENEFITS.sql").read_text().replace("{values_idprestaciones}", returns_codes.get("prestacion"))
                )
            except Exception as e:
                self.sqlserver.rollback()
                raise Exception(f"{str(e)}\nCheck the table INTE_ERROR_NOTIFICATIONS.")
            finally:
                self.sqlserver.commit()

        return returns_codes


class Benefits:
    def __init__(
            self,
            benefit_name: str,
            benefit_code: str,
            benefit_type_code: str,
            benefit_subtype_code: str,
            active: bool,
            start_created_date: str,
            end_created_date: str,
            deleted: bool,
            page: int,
            size: int
    ) -> None:
        self.benefit_name: str = benefit_name
        self.benefit_code: str = benefit_code
        self.benefit_type_code: str = benefit_type_code
        self.benefit_subtype_code: str = benefit_subtype_code
        self.active: bool = active
        self.start_created_date: Union[datetime | None] = datetime.fromisoformat(
            start_created_date.replace("Z", "")) if start_created_date else None
        self.end_created_date: Union[datetime | None] = datetime.fromisoformat(
            end_created_date.replace("Z", "")) if end_created_date else None
        self.deleted: bool = deleted
        self.page: int = page
        self.size: int = size

        # Validation size
        if 0 < self.size > 100:
            raise ValueError("The size parameter must be between 0 and 100.")

    def return_benefits(self) -> List[Dict]:
        # Set params
        params: tuple = tuple(
            filter(lambda bene: bene is not None,
                   (self.active if self.active else False,
                    self.deleted if not self.deleted else True,
                    self.benefit_name if self.benefit_name else None,
                    self.benefit_code if self.benefit_code else None,
                    self.benefit_type_code if self.benefit_type_code else None,
                    self.benefit_subtype_code if self.benefit_subtype_code else None,
                    self.start_created_date if self.start_created_date else None,
                    self.end_created_date if self.end_created_date else None,
                    )))

        # Set the query
        query: str = (
            f"SELECT ob.BENE_NAME, ob.BENE_CODE, obt.BETY_DESCRIPTION_ES, obs.BEST_DESCRIPTION_ES, ob.BENE_ACTIVE, "
            f"ob.BENE_ACTIVE_DATE, ob.BENE_CREATED_DATE, ob.BENE_DELETED, ob.BENE_DELETED_DATE "
            f"FROM [sinasuite].[dbo].[ORMA_BENEFITS] ob "
            f"LEFT OUTER JOIN [sinasuite].[dbo].[ORMA_BENEFIT_TYPES] obt ON obt.BETY_ID = ob.BETY_ID AND obt.BETY_DELETED = 0 "
            f"LEFT OUTER JOIN [sinasuite].[dbo].[ORMA_BENEFIT_SUBTYPES] obs ON obs.BEST_ID = ob.BEST_ID AND obs.BEST_DELETED = 0 "
            f"WHERE ob.BENE_ACTIVE = ? AND ob.BENE_DELETED = ?")

        # BENEFIT NAME
        if self.benefit_name:
            query += " AND ob.BENE_NAME LIKE ?"

        # BENEFIT CODE
        if self.benefit_code:
            query += " AND ob.BENE_CODE LIKE ?"

        # BENEFIT TYPE CODE
        if self.benefit_type_code:
            query += " AND obt.BETY_CODE = ?"

        # BENEFIT SUBTYPE CODE
        if self.benefit_subtype_code:
            query += " AND obs.BEST_CODE = ?"

        # CREATED DATE
        if (
                (self.start_created_date and not self.end_created_date) or
                (not self.start_created_date and self.end_created_date)
        ):
            raise ValueError("The range of created start date or end date can't be empty.")
        elif self.start_created_date and self.end_created_date:
            query += " AND ob.BENE_CREATED_DATE BETWEEN ? AND ?"

        # FETCH ROW LIMITS
        query += (f" ORDER BY ob.BENE_NAME OFFSET {self.size * (self.page - 1)} ROWS "
                  f"FETCH NEXT {self.size} ROWS ONLY")

        # Execute the query
        _get_benefits: Any = sqlserver.execute_select(
            query=query, params=params
        )

        return [{
            "benefitName": row[0],
            "benefitCode": row[1],
            "benefitTypeName": row[2],
            "benefitSubtypeName": row[3],
            "isActive": row[4],
            "activeDate": row[5].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[5] else None,
            "createdDate": row[6].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[6] else None,
            "isDeleted": row[7],
            "deletedDate": row[8].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[8] else None
        } for row in _get_benefits]
