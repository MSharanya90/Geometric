"""
Pydantic schemas for measurement representation and conversions.
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class AreaUnits(BaseModel):
    area_m2: float = Field(..., description="Area in square meters (canonical)")
    area_km2: float = Field(..., description="Area in square kilometers")
    area_ha: float = Field(..., description="Area in hectares")
    area_acres: float = Field(..., description="Area in acres")


class LengthUnits(BaseModel):
    length_m: float = Field(..., description="Length in meters (canonical)")
    length_km: float = Field(..., description="Length in kilometers")
    length_miles: float = Field(..., description="Length in miles")
    length_feet: float = Field(..., description="Length in feet")


class PointMeasurement(BaseModel):
    measurement_available: bool = False
    reason: str = "Point geometry does not require measurement."


class FeatureMeasurementItem(BaseModel):
    feature_id: int
    feature_index: int
    geometry_type: str
    status: str
    measurement_available: bool
    area: Optional[AreaUnits] = None
    length: Optional[LengthUnits] = None
    sub_measurements: Optional[List[Dict[str, Any]]] = None
    warnings: List[str] = Field(default_factory=list)
    reason: Optional[str] = None
