from pydantic import BaseModel
from uuid import UUID

class HazardScoreBase(BaseModel):
    habitation_id: UUID
    hazard_type: str
    score: float

class HazardScoreResponse(HazardScoreBase):
    id: UUID

    class Config:
        orm_mode = True
