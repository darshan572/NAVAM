from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from navam_api.database import Base
import uuid

class HazardScore(Base):
    __tablename__ = "hazard_scores"
    __table_args__ = {"schema": "navam"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habitation_id = Column(UUID(as_uuid=True), ForeignKey('navam.habitations.id'), nullable=False)
    hazard_type = Column(String(50), nullable=False)
    score = Column(Numeric(5, 2), nullable=False)
