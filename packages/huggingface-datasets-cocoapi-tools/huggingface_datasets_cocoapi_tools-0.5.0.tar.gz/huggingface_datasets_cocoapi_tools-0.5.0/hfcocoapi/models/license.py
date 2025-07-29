from pydantic import BaseModel, Field


class LicenseData(BaseModel):
    license_id: int = Field(alias="id")
    url: str
    name: str
