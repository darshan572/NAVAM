from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.site import SafeSiteResponse
from navam_api.models.site import SafeSite

router = APIRouter(prefix="/sites", tags=["sites"])

@router.get("", response_model=list[SafeSiteResponse])
def list_sites(db: Session = Depends(get_db_session)):
    return db.query(SafeSite).limit(10).all()
