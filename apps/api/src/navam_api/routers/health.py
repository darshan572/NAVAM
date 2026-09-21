from fastapi import APIRouter
from navam_api.schemas.health import HealthCheck

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=HealthCheck)
def get_health():
    return HealthCheck(status="ok")
