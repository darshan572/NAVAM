from pydantic import BaseModel
from uuid import UUID

class PriorityScoreBase(BaseModel):
    habitation_id: UUID
    policy_config_id: UUID
    score: float
    priority_tier: str
    score_breakdown: dict

class PriorityScoreResponse(PriorityScoreBase):
    id: UUID

    class Config:
        orm_mode = True
