from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.policy import PolicyConfigResponse
from navam_api.models.policy import PolicyConfig

router = APIRouter(prefix="/policies", tags=["policies"])

@router.get("", response_model=list[PolicyConfigResponse])
def list_policies(db: Session = Depends(get_db_session)):
    return db.query(PolicyConfig).limit(10).all()
