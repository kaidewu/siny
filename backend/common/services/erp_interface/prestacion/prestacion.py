import logging
from typing import Any, List, Dict
from common.database.sqlserver import sqlserver_db_pool as sqlserver
from schemas.erp_interface.prestacion.prestacion import PrestacionModel

logger = logging.Logger(__name__)


class ERPPrestacion:
    def __init__(
            self,
            catalog_id: str = None,
            prestacion_name: str = None,
            prestacion_code: str = None,
            family_code: str = None,
            subfamily_code: str = None,
            unit_code: str = "UND",
            duration: int = None,
            read: bool = False,
            active: bool = True,
            page: int = 1,
            size: int = 20
    ) -> None:
        """
        Class for the table ERP_Prestacion from SINA_interface_ERP
        :param catalog_id: Catalog ID from ORMA_BENEFIT_CATALOGS
        :param prestacion_name: Descripcion from ERP_Prestacion
        :param prestacion_code: IdPrestacion from ERP_Prestacion
        :param family_code: IdFamilia from ERP_Prestacion
        :param subfamily_code: IdSubfamilia from ERP_Prestacion
        :param read: FLeido from ERP_Prestacion
        :param active: Activo from ERP_Prestacion
        :param page:
        :param size: Number of size of data
        """
        self.sqlserver = sqlserver
        self.catalog_id: str = catalog_id
        self.prestacion_name: str = prestacion_name
        self.prestacion_code: str = prestacion_code
        self.family_code: str = family_code
        self.subfamily_code: str = subfamily_code
        self.unit_code: str = unit_code
        self.duration: int = duration
        self.read: bool = read
        self.active: bool = active
        self.page: int = page
        self.size: int = size

        # Validation size
        if 0 < self.size > 100:
            raise ValueError("The size parameter must be between 0 and 100.")

    def return_prestacion(self) -> List[Dict]:
        try:
            # Set parameters to the SQL query
            params: tuple = tuple(filter(
                lambda prestacion: prestacion is not None,
                (
                    self.active,
                    self.catalog_id if self.catalog_id else None,
                    self.prestacion_name if self.prestacion_name else None,
                    self.prestacion_code if self.prestacion_code else None,
                    self.family_code if self.family_code else None,
                    self.subfamily_code if self.subfamily_code else None,
                    self.unit_code if self.unit_code else None,
                    self.duration if self.duration else None
                )
            ))

            # Set the query to execute
            query: str = ("SELECT p.IdCatalogo, p.IdPrestacion, p.Descripcion, p.UnidadMedida, p.Duracion, "
                          "f.Descripcion, sf.Descripcion, p.Activo, "
                          "CASE WHEN p.FLeido IS NULL THEN 0 ELSE 1 END AS isRead, p.FLeido "
                          "FROM [SINA_interface_ERP].[dbo].[Prestacion] p "
                          "LEFT OUTER JOIN [SINA_interface_ERP].[dbo].[Familia] f ON f.IdFamilia = p.IdFamilia AND f.Activo = 1 "
                          "LEFT OUTER JOIN [SINA_interface_ERP].[dbo].[Subfamilia] sf ON sf.IdSubfamilia = p.IdSubfamilia AND sf.Activo = 1 "
                          "WHERE p.Activo = ?")

            # Set if it's been read or not
            if not self.read:
                query += " AND p.FLeido IS NULL"
            else:
                query += " AND p.FLeido IS NOT NULL"

            # Catalogs
            if self.catalog_id:
                query += " AND p.IdCatalogo = ?"

            # Prestacion Name
            if self.prestacion_name:
                query += " AND p.Descripcion LIKE ?"

            # Prestacion Code
            if self.prestacion_code:
                query += " AND p.IdPrestacion LIKE ?"

            # Family Code
            if self.family_code:
                query += " AND p.IdFamilia = ?"

            # Subfamily Code
            if self.subfamily_code:
                query += " AND p.IdSubfamilia = ?"

            # Unit Code
            if self.unit_code:
                query += " AND p.UnidadMedida = ?"

            # Duration
            if self.duration:
                query += " AND p.Duracion = ?"

            # FETCH LIMIT ROWS
            query += (f" ORDER BY p.Descripcion OFFSET {self.size * (self.page - 1)} ROWS "
                      f"FETCH NEXT {self.size} ROWS ONLY")

            _get_erp_prestacion: Any = self.sqlserver.execute_select(
                query=query, params=params
            )

            return [{
                "catalogId": row[0],
                "prestacionCode": row[1],
                "prestacionName": row[2],
                "measurementUnit": row[3],
                "duration": row[4],
                "familyName": row[5],
                "subfamilyName": row[6],
                "isActive": row[7],
                "isRead": row[8],
                "readDate": row[9].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[9] and row[9] != "" else None
            } for row in _get_erp_prestacion]
        except Exception as e:
            logger.error(f"service.erp_interface.prestacion.prestacion.ERPPrestacion.return_prestacion(): {str(e)}")
            raise Exception(str(e))


class InsertERPPrestacion:
    def __init__(
            self,
            prestacion_body: List[PrestacionModel]
    ) -> None:
        self.sqlserver: Any = sqlserver
        self.prestacion_body: List[PrestacionModel] = prestacion_body

    def insert_prestacion(self):

        existing_prestacion: List[str] = []
        new_prestacion: List[str] = []

        try:
            # Begin transaction
            self.sqlserver.begin()

            for prestacion in self.prestacion_body:
                # Set parameters
                params: tuple = (
                    prestacion.IdCatalogo if prestacion.IdCatalogo else "CAT01",
                    prestacion.IdPrestacion,
                    prestacion.IdFamilia if prestacion.IdFamilia else "",
                    prestacion.IdSubfamilia if prestacion.IdSubfamilia else "",
                    None,
                    1,
                    prestacion.Descripcion,
                    prestacion.UnidadMedida if prestacion.UnidadMedida else "UND",
                    prestacion.Duracion if prestacion.Duracion else 0
                )

                # Validation of each prestacion in ERP_Prestacion
                check_query: Any = self.sqlserver.execute_select(
                    (f"SELECT 1 FROM [SINA_interface_ERP].[dbo].[Prestacion] "
                     f"WHERE IdPrestacion = ?"),
                    params=(
                        prestacion.IdPrestacion
                    )
                )

                # If return 1, that means it exists in ERP_Prestacion
                if check_query:
                    existing_prestacion.append(prestacion.IdPrestacion)
                else:
                    # Set Insert Query
                    self.sqlserver.execute_insert(
                        (f"INSERT INTO [SINA_interface_ERP].[dbo].[Prestacion] (IdCatalogo, IdPrestacion, IdFamilia, IdSubfamilia, FLeido, Activo, Descripcion, UnidadMedida, Duracion) "
                         f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"), params=params
                    )

                    new_prestacion.append(prestacion.IdPrestacion)

            # If there is no error with the insert, it commits the transaction
            self.sqlserver.commit()

            return {
                "prestacionStatus": {
                    "existingPrestacion": ", ".join(f"'{text}'" for text in existing_prestacion),
                    "newPrestacion": ", ".join(f"'{text}'" for text in new_prestacion)
                }
            }
        except Exception as e:
            self.sqlserver.rollback()
            raise Exception(str(e))

