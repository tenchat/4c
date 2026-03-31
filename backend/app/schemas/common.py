from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

class PageResult(BaseModel, Generic[T]):
    list: list[T]
    total: int
    page: int
    page_size: int
