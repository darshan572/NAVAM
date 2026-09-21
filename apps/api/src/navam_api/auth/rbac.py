from fastapi import Depends, HTTPException, status
from .oauth import get_current_user
from typing import Annotated

def require_role(role: str):
    def role_checker(user: Annotated[dict, Depends(get_current_user)]):
        if user.get("role") != role and user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user
    return role_checker
