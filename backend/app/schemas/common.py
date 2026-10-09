"""
Common reusable schemas including Pagination, Error and Health responses.
"""
from typing import Generic, List, Optional, TypeVar, Any, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationResponse(BaseModel, Generic[T]):
    """Standardized paginated list response."""
    file_id: str
    total: int
    page: int
    page_size: int
    total_pages: int
    results: List[T]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str = "healthy"
    database: str = "connected"
    version: str = "1.0.0"
    environment: str = "development"
