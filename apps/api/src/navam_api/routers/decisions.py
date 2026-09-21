from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.decision import RelocationDecisionResponse
from navam_api.models.decision import RelocationDecision

router = APIRouter(prefix="/decisions", tags=["decisions"])

@router.get("", response_model=list[RelocationDecisionResponse])
def list_decisions(db: Session = Depends(get_db_session)):
    return db.query(RelocationDecision).limit(10).all()
