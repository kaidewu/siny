import logging
from typing import Any, List
from pathlib import Path
from common.database.sqlserver import sqlserver_db_pool as sqlserver
from schemas.benefits.benefit_subtypes import SubfamiliaModel
from settings.settings import settings

logger = logging.Logger(__name__)


class BenefitSubtypes:
    def __init__(
            self,
            benefit_subtype_name: str,
            benefit_subtype_code: str,
            benefit_type_code: str,
            deleted: bool,
            page: int,
            size: int
    ) -> None:
        """

        :param benefit_subtype_name:
        :param benefit_subtype_code:
        :param benefit_type_code:
        :param deleted:
        :param page:
        :param size:
        """
        self.sqlserver: Any = sqlserver
        self.benefit_subtype_name: str = benefit_subtype_name
        self.benefit_subtype_code: str = benefit_subtype_code
        self.benefit_type_code: str = benefit_type_code
        self.deleted: bool = deleted
        self.page: int = page
        self.size: int = size

        # Validation size
        if 0 < self.size > 100:
            raise ValueError("The size parameter must be between 0 and 100.")

    def return_benefit_subtypes(self):
        # Set parameters
        params: tuple = tuple(filter(
            lambda bene_type: bene_type is not None,
            (self.deleted,
             self.benefit_type_code if self.benefit_type_code else None,
             self.benefit_subtype_name if self.benefit_subtype_name else None,
             self.benefit_subtype_code if self.benefit_subtype_code else None
             )
        ))
        # Queries
        query: str = ("SELECT obs.BEST_DESCRIPTION_ES, obs.BEST_CODE, obs.BEST_DELETED, obs.BEST_DELETED_DATE, "
                      "obt.BETY_DESCRIPTION_ES, obt.BETY_CODE "
                      "FROM [sinasuite].[dbo].[ORMA_BENEFIT_SUBTYPES] obs "
                      "INNER JOIN ORMA_BENEFIT_TYPES obt ON obt.BETY_ID = obs.BETY_ID AND obt.BETY_DELETED = 0 "
                      "WHERE obs.BEST_DELETED = ?")

        if self.benefit_type_code:
            query += " AND obt.BETY_CODE = ?"

        if self.benefit_subtype_name:
            query += f" AND obs.BEST_DESCRIPTION_ES LIKE ?"

        if self.benefit_subtype_code:
            query += f" AND obs.BEST_CODE LIKE ?"

        query += (f" ORDER BY obs.BEST_DESCRIPTION_ES OFFSET {self.size * (self.page - 1)} ROWS "
                  f"FETCH NEXT {self.size} ROWS ONLY")

        _get_benefit_subtypes: Any = self.sqlserver.execute_select(
            query=query, params=params
        )

        return [{
            "benefitSubtypeName": row[0],
            "benefitSubtypeCode": row[1],
            "isDeleted": row[2],
            "deletedDate": row[3].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[3] else None,
            "benefitType": {
                "benefitTypeName": row[4],
                "benefitTypeCode": row[5]
            }
        } for row in _get_benefit_subtypes]


class BenefitSubtypesCreation:
    def __init__(
            self,
            benefit_subtypes_body: List[SubfamiliaModel]
    ) -> None:
        self.sqlserver: Any = sqlserver
        self.benefit_subtypes_body: List[SubfamiliaModel] = benefit_subtypes_body

    def returns_new_subtypes(self):
        benefit_subtypes: List = []

        try:
            self.sqlserver.begin()

            for subtype in self.benefit_subtypes_body:
                params: tuple = (
                    subtype.IdSubfamilia,
                    subtype.IdFamilia,
                    subtype.IdSubfamilia,
                    subtype.Descripcion,
                    subtype.IdFamilia,
                    None,
                    1,
                    None,
                    subtype.IdFamilia,
                )

                self.sqlserver.execute_insert(
                    (f"IF NOT EXISTS (SELECT 1 FROM [dbo].[ERP_Subfamilia] WHERE IdSubfamilia = ? AND IdFamilia = ?)"
                     f"BEGIN "
                     f"INSERT INTO [dbo].[ERP_Subfamilia] (IdSubfamilia, Descripcion, IdFamilia, Servicio, Activo, FLeido, Codtipo) "
                     f"VALUES (?, ?, ?, ?, ?, ?, (SELECT CodTipo FROM [dbo].[ERP_Familia] WHERE IdFamilia = ?)); "
                     f"END"), params=params
                )

                benefit_subtypes.append(subtype.IdSubfamilia)

            self.sqlserver.commit()

            try:
                self.sqlserver.begin()

                self.sqlserver.execute_procedures(
                    Path(settings.RESOURCES_PATH).joinpath("stored procedures/PROC_GET_NAV_BENEFIT_TYPES.sql").read_text()
                )
            except Exception as e:
                self.sqlserver.rollback()
                raise Exception(f"{str(e)}\nCheck the table INTE_ERROR_NOTIFICATIONS for more information.")
            finally:
                self.sqlserver.commit()

            return {
                "benefitSubtypes": ", ".join(f"'{subtype}'" for subtype in list(set(benefit_subtypes)))
            }
        except Exception as e:
            self.sqlserver.rollback()
            raise Exception(str(e))
