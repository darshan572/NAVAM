from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from navam_api.database import Base
import uuid

class PolicyConfig(Base):
    __tablename__ = "policy_configs"
    __table_args__ = {"schema": "navam"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_name = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    weights = Column(JSONB, nullable=False)
    season_weights = Column(JSONB, nullable=False)
    thresholds = Column(JSONB, nullable=False)
    vulnerability_weights = Column(JSONB, nullable=False)
    author_id = Column(String(255), nullable=False)
