from pathlib import Path

list = []

sql = Path("../resources/").joinpath("stored procedures/PROC_GET_NAV_BENEFITS.sql").read_text(encoding="utf-8")

sql = sql.replace("{values_idprestaciones}", ", ".join(f"'{text}'" for text in list))

print(sql)