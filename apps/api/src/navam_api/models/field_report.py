from sqlalchemy import Column, String, DateTime, ForeignKey, Date, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from navam_api.database import Base
import uuid

class FieldReport(Base):
    __tablename__ = "field_reports"
    __table_args__ = {"schema": "navam"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habitation_id = Column(UUID(as_uuid=True), ForeignKey('navam.habitations.id'), nullable=False)
    reported_by_user_id = Column(String(255), nullable=False)
    visit_date = Column(Date, nullable=False)
    observation_text = Column(Text, nullable=False)
