from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from navam_api.database import Base
import uuid
from datetime import datetime

class Habitation(Base):
    __tablename__ = "habitations"
    __table_args__ = {"schema": "navam"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lgd_village_code = Column(String(11), unique=True, nullable=False)
    lgd_block_code = Column(String(7), nullable=False)
    lgd_district_code = Column(String(5), nullable=False)
    lgd_state_code = Column(String(3), nullable=False)
    village_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
