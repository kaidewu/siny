from pathlib import Path
from typing import Any, Dict
from settings.settings import settings


class ProcGetNavBenefits:
    def __init__(
            self,
            sqlserver: Any,
            prestaciones: Dict,
            environment: str = "PRE"
    ) -> None:
        if not sqlserver:
            raise ConnectionError("The connection of the pool has not been declared")

        self.sqlserver: Any = sqlserver

        if environment not in ("PRO", "PRE", "CAPA"):
            raise ValueError("Environment parameter must be 'PRO' or 'PRE' or 'CAPA'")

        self.environment: str = environment

        self.proc_get_nav_benefits: str = Path(settings.RESOURCES_PATH).joinpath(
            "stored procedures/PROC_GET_NAV_BENEFITS.sql"
        ).read_text(encoding="utf-8").replace("{values_idprestaciones}", prestaciones.get("prestacion"))

        print(self.proc_get_nav_benefits)

    def exec_proc_get_nav_benefits(self) -> None:
        try:
            if self.environment != "PRO":
                self.sqlserver.execute_procedures(
                    self.proc_get_nav_benefits
                )
        except Exception as e:
            raise Exception(str(e))
