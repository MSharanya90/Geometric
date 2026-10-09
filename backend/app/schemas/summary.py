"""
Pydantic schemas for summary statistics of geospatial files.
"""
from typing import Optional, Dict
from pydantic import BaseModel, Field
from app.schemas.measurement import AreaUnits, LengthUnits


class SummaryStats(BaseModel):
    total_features: int
    number_of_polygons: int
    number_of_lines: int
    number_of_points: int
    other_geometries: int = 0

    # Total area & lengths
    total_polygon_area_m2: float
    total_polygon_area: AreaUnits
    total_line_length_m: float
    total_line_length: LengthUnits

    # Area distribution
    min_area_m2: Optional[float] = None
    max_area_m2: Optional[float] = None
    avg_area_m2: Optional[float] = None

    # Length distribution
    min_line_length_m: Optional[float] = None
    max_line_length_m: Optional[float] = None
    avg_line_length_m: Optional[float] = None

    # Quality & Validity
    invalid_geometry_count: int
    repaired_geometry_count: int
    valid_geometry_count: int


class SummaryResponse(BaseModel):
    file_id: str
    filename: str
    status: str
    crs: str
    measurement_crs: Optional[str] = None
    summary: SummaryStats
