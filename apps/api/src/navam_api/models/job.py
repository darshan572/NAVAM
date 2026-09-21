from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from navam_api.database import Base
import uuid

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "navam"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default='PENDING')
