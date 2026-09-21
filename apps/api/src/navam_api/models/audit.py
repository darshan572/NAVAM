from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy import BigInteger
from navam_api.database import Base

class AuditLog(Base):
    __tablename__ = "log"
    __table_args__ = {"schema": "audit"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    action = Column(String(100), nullable=False)
