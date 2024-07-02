import logging
from typing import Any, List, Dict
from schemas.erp_interface.prestacion_servicio.prestacion_servicio import PrestacionServicioModel

logger = logging.Logger(__name__)


class ERPPrestacionServicio:
    def __init__(
            self,
            sqlserver: Any,
            catalog_id: str = None,
            prestacion_name: str = None,
            prestacion_code: str = None,
            service_code: str = None,
            agendizable: bool = True,
            center_code: str = None,
            duration: int = 0,
            increment: int = 0,
            decrement: int = 0,
            read: bool = False,
            active: bool = True,
            page: int = 1,
            size: int = 20
    ) -> None:
        """
        Class for the table ERP_PrestacionServicio from SINA_interface_ERP
        :param catalog_id: Catalog ID from ORMA_BENEFIT_CATALOGS
        :param prestacion_name: Descripcion from ERP_PrestacionServicio
        :param prestacion_code: IdPrestacion from ERP_PrestacionServicio
        :param service_code: IdSerivcio from ERP_PrestacionServicio
        :param agendizable: Agendable from ERP_PrestacionServicio
        :param duration: Duracion from ERP_PrestacionServicio
        :param increment: Incremento from ERP_PrestacionServicio
        :param decrement: Decremento from ERP_PrestacionServicio
        :param read: FLeido from ERP_PrestacionServicio
        :param active: Activo from ERP_PrestacionServicio
        :param page:
        :param size: Number of size of data
        """
        if not sqlserver:
            raise ConnectionError("The connection of the pool has not been declared")

        self.sqlserver = sqlserver
        self.catalog_id: str = catalog_id
        self.prestacion_name: str = prestacion_name
        self.prestacion_code: str = prestacion_code
        self.service_code: str = service_code
        self.agendizable: bool = agendizable
        self.center_code: str = center_code
        self.duration: int = duration
        self.increment: int = increment
        self.decrement: int = decrement
        self.read: bool = read
        self.active: bool = active
        self.page: int = page
        self.size: int = size

        # Validation size
        if 0 < self.size > 100:
            raise ValueError("The size parameter must be between 0 and 100.")

    def return_prestacionservicio(self) -> List[Dict]:
        try:
            # Set parameters to the SQL query
            params: tuple = tuple(filter(
                lambda prestacionservicio: prestacionservicio is not None,
                (
                    self.active,
                    self.agendizable,
                    self.catalog_id if self.catalog_id else None,
                    self.prestacion_name if self.prestacion_name else None,
                    self.prestacion_code if self.prestacion_code else None,
                    self.service_code if self.service_code else None,
                    self.center_code if self.center_code else None,
                    self.duration if self.duration else None,
                    self.increment if self.increment else None,
                    self.decrement if self.decrement else None
                )
            ))

            # Set the query to execute
            query: str = ("SELECT ps.IdCatalogo, ps.IdPrestacion, p.Descripcion, os.SERV_DESCRIPTION_ES, "
                          "oc.CENT_NAME, p.UnidadMedida, p.Duracion, ps.Agendable, ps.Activo, "
                          "CASE WHEN ps.FLeido IS NULL THEN 0 ELSE 1 END AS isRead, ps.FLeido "
                          "FROM [sinasuite].[dbo].[ERP_PrestacionServicio] ps "
                          "LEFT OUTER JOIN [sinasuite].[dbo].[ERP_Prestacion] p ON p.IdPrestacion = ps.IdPrestacion AND p.Activo = 1 "
                          "LEFT OUTER JOIN [sinasuite].[dbo].[ORMA_CENTERS] oc ON oc.CENT_CODE COLLATE Modern_Spanish_CI_AS = ps.CodCentro "
                          "AND oc.CENT_DELETED = 0 AND oc.CENT_EXTERNAL = 0 "
                          "LEFT OUTER JOIN [sinasuite].[dbo].[ORMA_SERVICES] os ON os.SERV_CODE COLLATE Modern_Spanish_CI_AS = ps.IdServicio AND os.SERV_DELETED = 0 "
                          "WHERE ps.Activo = ? AND ps.Agendable = ?")

            # Set if it's been read or not
            if not self.read:
                query += " AND p.FLeido IS NULL"
            else:
                query += " AND p.FLeido IS NOT NULL"

            # Catalogs
            if self.catalog_id:
                query += " AND ps.IdCatalogo = ?"

            # Prestacion Name
            if self.prestacion_name:
                query += " AND p.Descripcion LIKE ?"

            # Prestacion Code
            if self.prestacion_code:
                query += " AND ps.IdPrestacion LIKE ?"

            # Service Code
            if self.service_code:
                query += " AND ps.IdServicio = ?"

            # Center Code
            if self.center_code:
                query += " AND ps.CodCentro = ?"

            # Duration
            if self.duration:
                query += " AND ps.Duracion = ?"

            # Increment
            if self.increment:
                query += " AND ps.Incremento = ?"

            # Decrement
            if self.decrement:
                query += " AND ps.Decremento = ?"

            # FETCH LIMIT ROWS
            query += (f" ORDER BY p.Descripcion OFFSET {self.size * (self.page - 1)} ROWS "
                      f"FETCH NEXT {self.size} ROWS ONLY")

            print(query)

            _get_erp_prestacion: Any = self.sqlserver.execute_select(
                query=query, params=params
            )

            return [{
                "catalogId": row[0],
                "prestacionCode": row[1],
                "prestacionName": row[2],
                "serviceName": row[3],
                "centerName": row[4],
                "measurementUnit": row[5],
                "duration": row[6],
                "isAgendizable": row[7],
                "isActive": row[8],
                "isRead": row[9],
                "readDate": row[10].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if row[10] and row[10] != "" else None
            } for row in _get_erp_prestacion]
        except Exception as e:
            logger.error(
                f"service.erp_interface.prestacion_servicio.prestacion_servicio.ERPPrestacionServicio.return_prestacionservicio(): {str(e)}")
            raise Exception(str(e))


class InsertERPPrestacionServicio:
    def __init__(
            self,
            prestacionservicio_body: List[PrestacionServicioModel],
            sqlserver: Any
    ) -> None:
        if not sqlserver:
            raise ConnectionError("The connection of the pool has not been declared")

        self.sqlserver: Any = sqlserver
        self.prestacionservicio_body: List[PrestacionServicioModel] = prestacionservicio_body

    def insert_prestacionservicio(self):

        prestacioneservicio: List[str] = []

        try:
            for prestacion in self.prestacionservicio_body:
                # Set parameters
                params_delete: tuple = tuple(filter(
                    lambda delete: delete is not None, (
                        prestacion.IdCatalogo if prestacion.IdCatalogo else "CAT01",
                        prestacion.IdPrestacion,
                        prestacion.IdServicio,
                        prestacion.CodCentro if prestacion.CodCentro else None
                    )
                ))
                query_delete: str = ("DELETE FROM [sinasuite].[dbo].[ERP_PrestacionServicio] WHERE IdCatalogo = ? "
                                     "AND IdPrestacion = ? AND IdServicio = ? AND Activo = 1")

                if prestacion.CodCentro:
                    query_delete += " AND CodCentro = ?"

                self.sqlserver.execute_insert(
                    query_delete, params=params_delete
                )

                # Set parameters
                params_insert: tuple = (
                    prestacion.IdCatalogo if prestacion.IdCatalogo else "CAT01",
                    prestacion.IdPrestacion,
                    prestacion.IdServicio,
                    None,
                    1,
                    prestacion.Agendable,
                    prestacion.Duracion,
                    prestacion.CodCentro,
                    prestacion.Departamental,
                    prestacion.Incremento,
                    prestacion.Decremento
                )

                # Set Insert Query
                self.sqlserver.execute_insert(
                    ("INSERT INTO [dbo].[ERP_PrestacionServicio] (IdCatalogo, IdPrestacion, IdServicio, FLeido, Activo, Agendable, Duracion, Codcentro, Departamental, Incremento, Decremento) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
                     ), params=params_insert
                )

                prestacioneservicio.append(prestacion.IdPrestacion)

            # Commits
            self.sqlserver.commit()

            return {
                "prestacionServicio": ", ".join(f"'{text}'" for text in list(set(prestacioneservicio)))
            }
        except Exception as e:
            raise Exception(str(e))
