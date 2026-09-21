from pydantic import BaseModel
from uuid import UUID

class SafeSiteBase(BaseModel):
    site_code: str
    site_name: str
    lgd_district_code: str

class SafeSiteResponse(SafeSiteBase):
    id: UUID

    class Config:
        orm_mode = True
