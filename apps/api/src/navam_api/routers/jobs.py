from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from navam_api.dependencies import get_db_session
from navam_api.schemas.job import JobResponse
from navam_api.models.job import Job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("", response_model=list[JobResponse])
def list_jobs(db: Session = Depends(get_db_session)):
    return db.query(Job).limit(10).all()
