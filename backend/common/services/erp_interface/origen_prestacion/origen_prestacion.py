import logging
from typing import Any, List, Dict
from common.database.sqlserver import sqlserver_db_pool as sqlserver
from schemas.erp_interface.origen_prestacion.origen_prestacion import OrigenPrestacionModel

logger = logging.Logger(__name__)


def check_status_db_erp_origenprestacion() -> bool:
    try:
        sqlserver.execute("SELECT COUNT(1) FROM [SINA_interface_ERP].[dbo].[Prestacion] WHERE 1=?", 1)
        return True
    except Exception as e:
        logger.error(f"service.erp_interface.origen_prestacion.origen_prestacion.check_status_db_erp_origenprestacion(): {str(e)}")
        return False


class ERPOrigenPrestacion:
    def __init__(
            self,
            catalog_id: str = None,
            prestacion_name: str = None,
            prestacion_code: str = None,
            ambit_code: str = None,
            service_code: str = None,
            center_code: str = None,
            read: bool = False,
            active: bool = True,
            page: int = 1,
            size: int = 20
    ) -> None:
        """
        Class for the table ERP_OrigenPrestacion from SINA_interface_ERP
        :param catalog_id: Catalog ID from ORMA_BENEFIT_CATALOGS
        :param prestacion_name: Descripcion from ERP_Prestacion
        :param prestacion_code: IdPrestacion from ERP_OrigenPrestacion
        :param ambit_code: IdAmbito from ERP_OrigenPrestacion
        :param service_code: IdServicio from ERP_OrigenPrestacion
        :param center_code: CodCentro from ERP_OrigenPrestacion
        :param read: FLeido from ERP_OrigenPrestacion
        :param active: Activo from ERP_OrigenPrestacion
        :param page:
        :param size: Number of size of data
        """
        self.sqlserver = sqlserver
        self.catalog_id: str = catalog_id
        self.prestacion_name: str = prestacion_name
        self.prestacion_code: str = prestacion_code
        self.ambit_code: str = ambit_code
        self.service_code: str = service_code
        self.center_code: str = center_code
        self.read: bool = read
        self.active: bool = active
        self.page: int = page
        self.size: int = size

        # Validation size
        if 0 < self.size > 100:
            raise ValueError("The size parameter must be between 0 and 100.")

    def return_origenprestacion(self) -> List[Dict]:
        try:
            # Set parameters to the SQL query
            params: tuple = tuple(filter(
                lambda origenprestacion: origenprestacion is not None,
                (
                    self.active,
                    self.catalog_id if self.catalog_id else None,
                    self.prestacion_name if self.prestacion_name else None,
                    self.prestacion_code if self.prestacion_code else None,
                    self.ambit_code if self.ambit_code else None,
                    self.service_code if self.service_code else None,
                    self.center_code if self.center_code else None
                )
            ))

            # Set the query to execute
            query: str = ("SELECT op.IdCatalogo, op.IdPrestacion, p.Descripcion, oa.AMBI_DESCRIPTION_ES, os.SERV_DESCRIPTION_ES, "
                          "oc.CENT_NAME, p.UnidadMedida, op.Activo, "
                          "CASE WHEN op.FLeido IS NULL THEN 0 ELSE 1 END AS isRead, op.FLeido "
                          "FROM [SINA_interface_ERP].[dbo].[OrigenPrestacion] op "
                          "LEFT OUTER JOIN [SINA_interface_ERP].[dbo].[Prestacion] p ON p.IdPrestacion = op.IdPrestacion AND p.Activo = 1 "
                          "LEFT OUTER JOIN [sinasuite].[dbo].[ORMA_AMBITS] oa ON oa.AMBI_CODE COLLATE Modern_Spanish_CI_AS = op.IdAmbito "
                          "AND oa.AMBI_DELETED = 0 "
                          "LEFT OUTER JOIN [sinasuite].[dbo].[ORMA_CENTERS] oc ON oc.CENT_CODE COLLATE Modern_Spanish_CI_AS = op.CodCentro "
                          "AND oc.CENT_DELETED = 0 AND oc.CENT_EXTERNAL = 0 "
                          "LEFT OUTER JOIN [sinasuite].[dbo].[ORMA_SERVICES] os ON os.SERV_CODE COLLATE Modern_Spanish_CI_AS = op.IdServicio AND os.SERV_DELETED = 0 "
                          "WHERE op.Activo = ?")

            # Set if it's been read or not
            if not self.read:
                query += " AND op.FLeido IS NULL"
            else:
                query += " AND op.FLeido IS NOT NULL"

            # Catalogs
            if self.catalog_id:
                query += " AND op.IdCatalogo = ?"

            # Prestacion Name
            if self.prestacion_name:
                query += " AND p.Descripcion LIKE ?"

            # Prestacion Code
            if self.prestacion_code:
                query += " AND op.IdPrestacion LIKE ?"

            # Ambit Code
            if self.ambit_code:
                query += " AND op.IdAmbito = ?"

            # Service Code
            if self.service_code:
                query += " AND op.IdServicio = ?"

            # Center Code
            if self.center_code:
                query += " AND op.CodCentro = ?"

            # FETCH LIMIT ROWS
            query += (f" ORDER BY p.Descripcion OFFSET {self.size * (self.page - 1)} ROWS "
                      f"FETCH NEXT {self.size} ROWS ONLY")

            _get_erp_origenprestacion: Any = self.sqlserver.execute_select(
                query=query, params=params
            )

            return [{
                "catalogId": row[0],
                "prestacionCode": row[1],
                "prestacionName": row[2],
                "ambitName": row[3],
                "serviceName": row[4],
                "centerName": row[5],
                "measurementUnit": row[6],
                "isActive": row[7],
                "isRead": row[8],
                "readDate": row[9].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[9] and row[9] != "" else None
            } for row in _get_erp_origenprestacion]
        except Exception as e:
            logger.error(f"service.erp_interface.prestacion.prestacion.ERPPrestacion.return_prestacion(): {str(e)}")
            raise Exception(str(e))


class InsertERPOrigenPrestacion:
    def __init__(
            self,
            origenprestacion_body: List[OrigenPrestacionModel]
    ) -> None:
        self.sqlserver: Any = sqlserver
        self.origenprestacion_body: List[OrigenPrestacionModel] = origenprestacion_body

    def insert_origenprestacion(self) -> Dict[str, Dict[str, List[str]]]:

        existing_origenprestacion: List[str] = []
        new_origenprestacion: List[str] = []

        try:
            # Begin transaction
            self.sqlserver.begin()

            for prestacion in self.origenprestacion_body:
                # Set parameters
                params: tuple = (
                    prestacion.Codcentro,
                    prestacion.IdAmbito,
                    prestacion.IdServicio,
                    prestacion.IdCatalogo,
                    prestacion.IdPrestacion,
                    None,
                    1,
                )

                # Validation of each prestacion in ERP_Prestacion
                check_query: Any = self.sqlserver.execute_select(
                    (f"SELECT 1 FROM [SINA_interface_ERP].[dbo].[OrigenPrestacion] "
                     f"WHERE IdCatalogo = ? AND IdPrestacion = ? AND IdAmbito = ? AND IdServicio = ? AND CodCentro = ?"),
                    params=(
                        prestacion.IdCatalogo,
                        prestacion.IdPrestacion,
                        prestacion.IdAmbito,
                        prestacion.IdServicio,
                        prestacion.CodCentro
                    )
                )

                # If return 1, that means it exists in ERP_Prestacion
                if check_query:
                    existing_origenprestacion.append(prestacion.IdPrestacion)
                else:
                    # Set Insert Query
                    self.sqlserver.execute_insert(
                        (f"INSERT INTO [SINA_interface_ERP].[dbo].[OrigenPrestacion] (CodCentro, IdAmbito, IdServicio, IdCatalogo, IdPrestacion, FLeido, Activo) "
                         f"VALUES (?, ?, ?, ?, ?, ?, ?)"), params=params
                    )

                    new_origenprestacion.append(prestacion.IdPrestacion)

            # If there is no error with the insert, it commits the transaction
            self.sqlserver.commit()

            return {
                "origenPrestacionStatus": {
                    "existingOrigenPrestacion": existing_origenprestacion,
                    "newOrigenPrestacion": new_origenprestacion
                }
            }
        except Exception as e:
            self.sqlserver.rollback()
            raise Exception(str(e))

