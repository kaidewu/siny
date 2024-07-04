import logging
from typing import Any, List, Dict
from schemas.erp_interface.prestacion.prestacion import PrestacionModel

logger = logging.Logger(__name__)


class ERPPrestacion:
    def __init__(
            self,
            sqlserver: Any,
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
        if not sqlserver:
            raise ConnectionError("The connection of the pool has not been declared")

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
                          "FROM [sinasuite].[dbo].[ERP_Prestacion] p "
                          "LEFT OUTER JOIN [sinasuite].[dbo].[ERP_Familia] f ON f.IdFamilia = p.IdFamilia AND f.Activo = 1 "
                          "LEFT OUTER JOIN [sinasuite].[dbo].[ERP_Subfamilia] sf ON sf.IdSubfamilia = p.IdSubfamilia AND sf.Activo = 1 "
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
            prestacion_body: List[PrestacionModel],
            sqlserver: Any
    ) -> None:
        self.sqlserver: Any = sqlserver
        self.prestacion_body: List[PrestacionModel] = prestacion_body

    def insert_prestacion(self):

        prestacion: List[str] = []

        try:
            for erp_prestacion in self.prestacion_body:
                # Set parameters
                params: tuple = (
                    erp_prestacion.IdPrestacion,
                    erp_prestacion.IdCatalogo if erp_prestacion.IdCatalogo else "CAT01",
                    erp_prestacion.IdPrestacion,
                    erp_prestacion.IdFamilia,
                    erp_prestacion.IdSubfamilia,
                    None,
                    1,
                    erp_prestacion.Descripcion,
                    erp_prestacion.UnidadMedida if erp_prestacion.UnidadMedida else "UND",
                    erp_prestacion.Duracion if erp_prestacion.Duracion else 0
                )

                # Set Insert Query
                self.sqlserver.execute_insert(
                    (f"""IF NOT EXISTS (SELECT 1 FROM [dbo].[ERP_Prestacion] WHERE IdPrestacion = ?)
                    BEGIN
                        INSERT INTO [dbo].[ERP_Prestacion] (IdCatalogo, IdPrestacion, IdFamilia, IdSubfamilia, FLeido, Activo, Descripcion, UnidadMedida, Duracion) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    END
                    """
                     ), params=params
                )

                prestacion.append(erp_prestacion.IdPrestacion)

            # Commits
            self.sqlserver.commit()

            return {
                "prestacion": ", ".join(f"'{text}'" for text in list(set(prestacion)))
            }
        except Exception as e:
            raise Exception(str(e))

