from pydantic import BaseModel
from uuid import UUID

class PolicyConfigBase(BaseModel):
    policy_name: str
    version: int
    weights: dict
    season_weights: dict
    thresholds: dict
    vulnerability_weights: dict
    author_id: str

class PolicyConfigResponse(PolicyConfigBase):
    id: UUID

    class Config:
        orm_mode = True
