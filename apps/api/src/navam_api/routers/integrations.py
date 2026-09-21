from fastapi import APIRouter

router = APIRouter(prefix="/integrations", tags=["integrations"])

@router.get("")
def integrations_status():
    return {"status": "ok"}
