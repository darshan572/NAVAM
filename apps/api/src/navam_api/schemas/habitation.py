from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class HabitationBase(BaseModel):
    lgd_village_code: str
    lgd_block_code: str
    lgd_district_code: str
    lgd_state_code: str
    village_name: str

class HabitationCreate(HabitationBase):
    pass

class HabitationResponse(HabitationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True
