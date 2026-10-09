"""
Pydantic schemas for features and GeoJSON responses.
"""
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from app.schemas.measurement import AreaUnits, LengthUnits


class FeatureResponse(BaseModel):
    id: int
    uploaded_file_id: str
    feature_index: int
    geometry_type: str
    geometry: Dict[str, Any]
    bbox: Optional[List[float]] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    is_valid: bool
    was_repaired: bool
    measurement_status: str
    area_m2: Optional[float] = None
    length_m: Optional[float] = None
    area: Optional[AreaUnits] = None
    length: Optional[LengthUnits] = None
    sub_measurements: Optional[List[Dict[str, Any]]] = None
    warnings: List[str] = Field(default_factory=list)
    created_at: datetime


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]
    id: Optional[int] = None
    bbox: Optional[List[float]] = None


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    crs: Optional[Dict[str, Any]] = None
    features: List[GeoJSONFeature]
    metadata: Optional[Dict[str, Any]] = None
