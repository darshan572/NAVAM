from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from navam_api.database import Base
import uuid

class PriorityScore(Base):
    __tablename__ = "priority_scores"
    __table_args__ = {"schema": "navam"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habitation_id = Column(UUID(as_uuid=True), ForeignKey('navam.habitations.id'), nullable=False)
    policy_config_id = Column(UUID(as_uuid=True), ForeignKey('navam.policy_configs.id'), nullable=False)
    score = Column(Numeric(5, 2), nullable=False)
    priority_tier = Column(String(20), nullable=False)
    score_breakdown = Column(JSONB, nullable=False)
