from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.habitation import HabitationResponse
from navam_api.models.habitation import Habitation

router = APIRouter(prefix="/habitations", tags=["habitations"])

@router.get("", response_model=list[HabitationResponse])
def list_habitations(db: Session = Depends(get_db_session)):
    return db.query(Habitation).limit(10).all()
