from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List

T = TypeVar('T')

class Pagination(BaseModel):
    total: int
    page: int
    size: int

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    pagination: Pagination
