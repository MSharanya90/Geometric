"""
Pydantic schemas for file information and upload responses.
"""
from datetime import datetime
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field


class FileResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    feature_count: int
    geometry_types: Dict[str, int] = Field(default_factory=dict)
    crs: str
    measurement_crs: Optional[str] = None
    crs_strategy: Optional[str] = None
    status: str
    processing_time_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


class FileUploadResponse(BaseModel):
    message: str = "File uploaded and processed successfully."
    file: FileResponse
