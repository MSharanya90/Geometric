"""
Measurement, summary statistics, and GeoJSON endpoints.
"""
import math
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import FileNotFoundInDbError
from app.db.session import get_db
from app.repositories.file_repository import FileRepository
from app.repositories.feature_repository import FeatureRepository
from app.schemas.common import PaginationResponse
from app.schemas.measurement import (
    FeatureMeasurementItem,
    AreaUnits,
    LengthUnits,
)
from app.schemas.summary import SummaryResponse, SummaryStats
from app.schemas.feature import GeoJSONFeature, GeoJSONFeatureCollection
from app.utils.geo_math import convert_area_units, convert_length_units

router = APIRouter(prefix="/files/{file_id}", tags=["Measurements"])


@router.get(
    "/measurements",
    response_model=PaginationResponse[FeatureMeasurementItem],
    summary="Get Paginated Measurements",
    description="Retrieve paginated feature measurements with sorting and filtering options.",
)
def get_measurements(
    file_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    geometry_type: Optional[str] = Query(None, description="Filter by geometry type (e.g. Polygon, LineString)"),
    sort_by: Optional[str] = Query(None, description="Sort field: 'area', 'length', 'geometry_type'"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    min_area: Optional[float] = Query(None, ge=0, description="Minimum area in m2"),
    max_area: Optional[float] = Query(None, ge=0, description="Maximum area in m2"),
    min_length: Optional[float] = Query(None, ge=0, description="Minimum length in meters"),
    max_length: Optional[float] = Query(None, ge=0, description="Maximum length in meters"),
    db: Session = Depends(get_db),
) -> PaginationResponse[FeatureMeasurementItem]:
    file_repo = FileRepository(db)
    uploaded_file = file_repo.get_by_id(file_id)
    if not uploaded_file:
        raise FileNotFoundInDbError(file_id)

    feature_repo = FeatureRepository(db)
    features, total_count = feature_repo.get_by_file_id(
        file_id=file_id,
        page=page,
        page_size=page_size,
        geometry_type=geometry_type,
        sort_by=sort_by,
        order=order,
        min_area=min_area,
        max_area=max_area,
        min_length=min_length,
        max_length=max_length,
    )

    items: List[FeatureMeasurementItem] = []
    for f in features:
        is_point = "point" in f.geometry_type.lower()
        meas_avail = (f.area_m2 is not None or f.length_m is not None) and not is_point

        area_obj = None
        if f.area_m2 is not None:
            area_obj = AreaUnits(**convert_area_units(f.area_m2))

        length_obj = None
        if f.length_m is not None:
            length_obj = LengthUnits(**convert_length_units(f.length_m))

        reason = None
        if is_point:
            reason = "Point geometry does not require measurement."
        elif not meas_avail:
            reason = "Measurement unavailable for this geometry."

        items.append(
            FeatureMeasurementItem(
                feature_id=f.id,
                feature_index=f.feature_index,
                geometry_type=f.geometry_type,
                status=f.measurement_status,
                measurement_available=meas_avail,
                area=area_obj,
                length=length_obj,
                sub_measurements=f.sub_measurements,
                warnings=f.warnings or [],
                reason=reason,
            )
        )

    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

    return PaginationResponse[FeatureMeasurementItem](
        file_id=file_id,
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        results=items,
    )


@router.get(
    "/summary",
    response_model=SummaryResponse,
    summary="Get Summary Statistics",
    description="Retrieve comprehensive aggregate statistics, bounding totals, and quality indicators.",
)
def get_summary(
    file_id: str,
    db: Session = Depends(get_db),
) -> SummaryResponse:
    file_repo = FileRepository(db)
    uploaded_file = file_repo.get_by_id(file_id)
    if not uploaded_file:
        raise FileNotFoundInDbError(file_id)

    feature_repo = FeatureRepository(db)
    stats_data = feature_repo.get_summary_stats(file_id)

    tot_area_m2 = stats_data["total_polygon_area_m2"]
    tot_len_m = stats_data["total_line_length_m"]

    summary_stats = SummaryStats(
        total_features=stats_data["total_features"],
        number_of_polygons=stats_data["number_of_polygons"],
        number_of_lines=stats_data["number_of_lines"],
        number_of_points=stats_data["number_of_points"],
        other_geometries=stats_data["other_geometries"],
        total_polygon_area_m2=round(tot_area_m2, 2),
        total_polygon_area=AreaUnits(**convert_area_units(tot_area_m2)),
        total_line_length_m=round(tot_len_m, 2),
        total_line_length=LengthUnits(**convert_length_units(tot_len_m)),
        min_area_m2=round(stats_data["min_area_m2"], 2) if stats_data["min_area_m2"] is not None else None,
        max_area_m2=round(stats_data["max_area_m2"], 2) if stats_data["max_area_m2"] is not None else None,
        avg_area_m2=round(stats_data["avg_area_m2"], 2) if stats_data["avg_area_m2"] is not None else None,
        min_line_length_m=round(stats_data["min_line_length_m"], 2) if stats_data["min_line_length_m"] is not None else None,
        max_line_length_m=round(stats_data["max_line_length_m"], 2) if stats_data["max_line_length_m"] is not None else None,
        avg_line_length_m=round(stats_data["avg_line_length_m"], 2) if stats_data["avg_line_length_m"] is not None else None,
        invalid_geometry_count=stats_data["invalid_geometry_count"],
        repaired_geometry_count=stats_data["repaired_geometry_count"],
        valid_geometry_count=stats_data["valid_geometry_count"],
    )

    return SummaryResponse(
        file_id=file_id,
        filename=uploaded_file.original_filename,
        status=uploaded_file.status,
        crs=uploaded_file.source_crs or "EPSG:4326",
        measurement_crs=uploaded_file.measurement_crs,
        summary=summary_stats,
    )


@router.get(
    "/geojson",
    response_model=GeoJSONFeatureCollection,
    summary="Get GeoJSON with Embedded Measurements",
    description="Retrieve full GeoJSON FeatureCollection formatted specifically for Leaflet map display.",
)
def get_geojson(
    file_id: str,
    db: Session = Depends(get_db),
) -> GeoJSONFeatureCollection:
    file_repo = FileRepository(db)
    uploaded_file = file_repo.get_by_id(file_id)
    if not uploaded_file:
        raise FileNotFoundInDbError(file_id)

    feature_repo = FeatureRepository(db)
    features = feature_repo.get_all_by_file_id(file_id)

    geojson_features: List[GeoJSONFeature] = []
    for f in features:
        props = dict(f.properties or {})
        props["feature_id"] = f.id
        props["feature_index"] = f.feature_index
        props["geometry_type"] = f.geometry_type
        props["is_valid"] = f.is_valid
        props["was_repaired"] = f.was_repaired
        props["status"] = f.measurement_status

        if f.area_m2 is not None:
            area_conv = convert_area_units(f.area_m2)
            props["area_m2"] = area_conv["area_m2"]
            props["area_ha"] = area_conv["area_ha"]
            props["area_km2"] = area_conv["area_km2"]
            props["area_acres"] = area_conv["area_acres"]

        if f.length_m is not None:
            len_conv = convert_length_units(f.length_m)
            props["length_m"] = len_conv["length_m"]
            props["length_km"] = len_conv["length_km"]
            props["length_miles"] = len_conv["length_miles"]
            props["length_feet"] = len_conv["length_feet"]

        geojson_features.append(
            GeoJSONFeature(
                type="Feature",
                geometry=f.geometry,
                properties=props,
                id=f.id,
                bbox=f.bbox,
            )
        )

    metadata = {
        "file_id": uploaded_file.id,
        "filename": uploaded_file.original_filename,
        "source_crs": uploaded_file.source_crs,
        "measurement_crs": uploaded_file.measurement_crs,
        "crs_strategy": uploaded_file.crs_strategy,
        "feature_count": len(geojson_features),
    }

    return GeoJSONFeatureCollection(
        type="FeatureCollection",
        features=geojson_features,
        metadata=metadata,
    )
