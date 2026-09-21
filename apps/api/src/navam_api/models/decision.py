from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET
from navam_api.database import Base
import uuid

class RelocationPlan(Base):
    __tablename__ = "relocation_plans"
    __table_args__ = {"schema": "navam"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_name = Column(String(255), nullable=False)
    district_code = Column(String(5), nullable=False)
    created_by = Column(String(255), nullable=False)

class RelocationDecision(Base):
    __tablename__ = "relocation_decisions"
    __table_args__ = {"schema": "navam"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('navam.relocation_plans.id'))
    habitation_id = Column(UUID(as_uuid=True), ForeignKey('navam.habitations.id'), nullable=False)
    target_site_id = Column(UUID(as_uuid=True), ForeignKey('navam.safe_sites.id'), nullable=False)
    decision_type = Column(String(50), nullable=False)
    decision_by_user_id = Column(String(255), nullable=False)
    decision_by_role = Column(String(50), nullable=False)
