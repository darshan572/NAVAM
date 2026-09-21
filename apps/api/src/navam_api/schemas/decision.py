from pydantic import BaseModel
from uuid import UUID

class RelocationDecisionBase(BaseModel):
    habitation_id: UUID
    target_site_id: UUID
    decision_type: str
    decision_by_user_id: str
    decision_by_role: str

class RelocationDecisionResponse(RelocationDecisionBase):
    id: UUID

    class Config:
        orm_mode = True
