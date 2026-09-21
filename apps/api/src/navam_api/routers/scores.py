from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.priority import PriorityScoreResponse
from navam_api.models.priority import PriorityScore

router = APIRouter(prefix="/scores", tags=["scores"])

@router.get("/priority", response_model=list[PriorityScoreResponse])
def list_priority_scores(db: Session = Depends(get_db_session)):
    return db.query(PriorityScore).limit(10).all()
