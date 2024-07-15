from pydantic import BaseModel


class BenefitsModel(BaseModel):
    benefitsCode: list[str]
