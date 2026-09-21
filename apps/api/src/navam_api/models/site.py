from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from navam_api.database import Base
import uuid

class SafeSite(Base):
    __tablename__ = "safe_sites"
    __table_args__ = {"schema": "navam"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_code = Column(String(50), unique=True, nullable=False)
    site_name = Column(String(255), nullable=False)
    lgd_district_code = Column(String(5), nullable=False)
