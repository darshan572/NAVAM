from fastapi import APIRouter

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("")
def list_audit_logs():
    return []
