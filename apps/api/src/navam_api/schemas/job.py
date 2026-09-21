from pydantic import BaseModel
from uuid import UUID

class JobBase(BaseModel):
    job_type: str
    status: str

class JobResponse(JobBase):
    id: UUID

    class Config:
        orm_mode = True
