import os

ROOT = r"d:\Coding World\MyPractices\SIH_2026\NAVAM\apps\api\src\navam_api"

def write(path, content):
    full_path = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

write("__init__.py", "")

write("py.typed", "")

write("config.py", """
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(default="postgresql://user:password@localhost/navam")
    redis_url: str = Field(default="redis://localhost:6379/0")
    secret_key: str = Field(default="supersecretkey")
    algorithm: str = Field(default="HS256")
    environment: str = Field(default="dev")

    class Config:
        env_file = ".env"

settings = Settings()
""")

write("database.py", """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

write("dependencies.py", """
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db

def get_db_session(db: Session = Depends(get_db)):
    return db
""")

write("main.py", """
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .routers import habitations, scores, sites, decisions, policies, jobs, audit, integrations, health, dashboard
from .middleware.correlation import CorrelationMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.audit_middleware import AuditMiddleware

app = FastAPI(title="NAVAM API")

app.add_middleware(CorrelationMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditMiddleware)

app.include_router(health.router)
app.include_router(habitations.router)
app.include_router(scores.router)
app.include_router(sites.router)
app.include_router(decisions.router)
app.include_router(policies.router)
app.include_router(jobs.router)
app.include_router(audit.router)
app.include_router(integrations.router)
app.include_router(dashboard.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"type": "about:blank", "title": "Internal Server Error", "status": 500, "detail": str(exc)},
    )
""")

write("auth/__init__.py", "")
write("auth/oauth.py", """
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    if token != "fake-super-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user_id": "test_user", "role": "admin"}
""")
write("auth/rbac.py", """
from fastapi import Depends, HTTPException, status
from .oauth import get_current_user
from typing import Annotated

def require_role(role: str):
    def role_checker(user: Annotated[dict, Depends(get_current_user)]):
        if user.get("role") != role and user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user
    return role_checker
""")
write("auth/audit.py", """
def log_audit_event(action: str, resource: str):
    pass
""")

write("middleware/__init__.py", "")
write("middleware/correlation.py", """
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
""")
write("middleware/rate_limit.py", """
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Redis-based rate limiting logic placeholder
        return await call_next(request)
""")
write("middleware/audit_middleware.py", """
from starlette.middleware.base import BaseHTTPMiddleware

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        return response
""")

# Models
write("models/__init__.py", """
from .habitation import Habitation
from .site import SafeSite
from .policy import PolicyConfig
from .hazard import HazardScore
from .priority import PriorityScore
from .decision import RelocationPlan, RelocationDecision
from .job import Job
from .field_report import FieldReport
from .audit import AuditLog
""")

write("models/habitation.py", """
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
""")

write("models/site.py", """
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
""")

write("models/policy.py", """
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
""")

write("models/hazard.py", """
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
""")

write("models/priority.py", """
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
""")

write("models/decision.py", """
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
""")

write("models/job.py", """
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
""")

write("models/field_report.py", """
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
""")

write("models/audit.py", """
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy import BigInteger
from navam_api.database import Base

class AuditLog(Base):
    __tablename__ = "log"
    __table_args__ = {"schema": "audit"}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    action = Column(String(100), nullable=False)
""")

# Schemas
write("schemas/__init__.py", "")
write("schemas/common.py", """
from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List

T = TypeVar('T')

class Pagination(BaseModel):
    total: int
    page: int
    size: int

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    pagination: Pagination
""")

write("schemas/health.py", """
from pydantic import BaseModel

class HealthCheck(BaseModel):
    status: str
""")

write("schemas/habitation.py", """
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class HabitationBase(BaseModel):
    lgd_village_code: str
    lgd_block_code: str
    lgd_district_code: str
    lgd_state_code: str
    village_name: str

class HabitationCreate(HabitationBase):
    pass

class HabitationResponse(HabitationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True
""")

write("schemas/site.py", """
from pydantic import BaseModel
from uuid import UUID

class SafeSiteBase(BaseModel):
    site_code: str
    site_name: str
    lgd_district_code: str

class SafeSiteResponse(SafeSiteBase):
    id: UUID

    class Config:
        orm_mode = True
""")

write("schemas/policy.py", """
from pydantic import BaseModel
from uuid import UUID

class PolicyConfigBase(BaseModel):
    policy_name: str
    version: int
    weights: dict
    season_weights: dict
    thresholds: dict
    vulnerability_weights: dict
    author_id: str

class PolicyConfigResponse(PolicyConfigBase):
    id: UUID

    class Config:
        orm_mode = True
""")

write("schemas/hazard.py", """
from pydantic import BaseModel
from uuid import UUID

class HazardScoreBase(BaseModel):
    habitation_id: UUID
    hazard_type: str
    score: float

class HazardScoreResponse(HazardScoreBase):
    id: UUID

    class Config:
        orm_mode = True
""")

write("schemas/priority.py", """
from pydantic import BaseModel
from uuid import UUID

class PriorityScoreBase(BaseModel):
    habitation_id: UUID
    policy_config_id: UUID
    score: float
    priority_tier: str
    score_breakdown: dict

class PriorityScoreResponse(PriorityScoreBase):
    id: UUID

    class Config:
        orm_mode = True
""")

write("schemas/decision.py", """
from pydantic import BaseModel
from uuid import UUID

class RelocationDecisionBase(BaseModel):
    habitation_id: UUID
    target_site_id: UUID
    decision_type: str
    decision_by_user_id: str
    decision_by_role: str

class RelocationDecisionResponse(RelocationDecisionBase):
    id: UUID

    class Config:
        orm_mode = True
""")

write("schemas/job.py", """
from pydantic import BaseModel
from uuid import UUID

class JobBase(BaseModel):
    job_type: str
    status: str

class JobResponse(JobBase):
    id: UUID

    class Config:
        orm_mode = True
""")

# Routers
write("routers/__init__.py", "")

write("routers/health.py", """
from fastapi import APIRouter
from navam_api.schemas.health import HealthCheck

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=HealthCheck)
def get_health():
    return HealthCheck(status="ok")
""")

write("routers/habitations.py", """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.habitation import HabitationResponse
from navam_api.models.habitation import Habitation

router = APIRouter(prefix="/habitations", tags=["habitations"])

@router.get("", response_model=list[HabitationResponse])
def list_habitations(db: Session = Depends(get_db_session)):
    return db.query(Habitation).limit(10).all()
""")

write("routers/scores.py", """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.priority import PriorityScoreResponse
from navam_api.models.priority import PriorityScore

router = APIRouter(prefix="/scores", tags=["scores"])

@router.get("/priority", response_model=list[PriorityScoreResponse])
def list_priority_scores(db: Session = Depends(get_db_session)):
    return db.query(PriorityScore).limit(10).all()
""")

write("routers/sites.py", """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.site import SafeSiteResponse
from navam_api.models.site import SafeSite

router = APIRouter(prefix="/sites", tags=["sites"])

@router.get("", response_model=list[SafeSiteResponse])
def list_sites(db: Session = Depends(get_db_session)):
    return db.query(SafeSite).limit(10).all()
""")

write("routers/decisions.py", """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.decision import RelocationDecisionResponse
from navam_api.models.decision import RelocationDecision

router = APIRouter(prefix="/decisions", tags=["decisions"])

@router.get("", response_model=list[RelocationDecisionResponse])
def list_decisions(db: Session = Depends(get_db_session)):
    return db.query(RelocationDecision).limit(10).all()
""")

write("routers/policies.py", """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.policy import PolicyConfigResponse
from navam_api.models.policy import PolicyConfig

router = APIRouter(prefix="/policies", tags=["policies"])

@router.get("", response_model=list[PolicyConfigResponse])
def list_policies(db: Session = Depends(get_db_session)):
    return db.query(PolicyConfig).limit(10).all()
""")

write("routers/jobs.py", """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.job import JobResponse
from navam_api.models.job import Job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("", response_model=list[JobResponse])
def list_jobs(db: Session = Depends(get_db_session)):
    return db.query(Job).limit(10).all()
""")

write("routers/audit.py", """
from fastapi import APIRouter

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("")
def list_audit_logs():
    return []
""")

write("routers/integrations.py", """
from fastapi import APIRouter

router = APIRouter(prefix="/integrations", tags=["integrations"])

@router.get("")
def integrations_status():
    return {"status": "ok"}
""")

write("routers/dashboard.py", """
from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
def get_dashboard_metrics():
    return {"metrics": {}}
""")

# Services
write("services/__init__.py", "")
write("services/scoring.py", """
def calculate_score():
    pass
""")
write("services/site_ranker.py", """
def rank_sites():
    pass
""")
write("services/capacity.py", """
def assess_capacity():
    pass
""")
write("services/ml_client.py", """
class MLClient:
    pass
""")

# Tests
write("tests/__init__.py", "")
write("tests/conftest.py", """
import pytest
from fastapi.testclient import TestClient
from navam_api.main import app

@pytest.fixture
def client():
    return TestClient(app)
""")

write("tests/test_health.py", """
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
""")

write("tests/test_habitations.py", """
def test_habitations(client):
    pass
""")

write("tests/test_scores.py", """
def test_scores(client):
    pass
""")

write("tests/test_decisions.py", """
def test_decisions(client):
    pass
""")

write("tests/test_rbac.py", """
def test_rbac(client):
    pass
""")

# App-level files
def write_app_file(path, content):
    full_path = os.path.join(r"d:\Coding World\MyPractices\SIH_2026\NAVAM\apps\api", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

write_app_file("Dockerfile", """
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install .

COPY src/ src/

CMD ["uvicorn", "navam_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
""")

write_app_file("pyproject.toml", """
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "navam_api"
version = "0.1.0"
description = "NAVAM API"
authors = [{name = "NAVAM Team"}]
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.100",
    "uvicorn>=0.23",
    "sqlalchemy>=2.0",
    "pydantic>=2.0",
    "pydantic-settings",
    "alembic",
    "psycopg2-binary",
    "redis"
]

[project.optional-dependencies]
dev = [
    "pytest",
    "httpx"
]
""")

print("Files created successfully.")
