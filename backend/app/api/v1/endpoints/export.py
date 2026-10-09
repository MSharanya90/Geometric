"""
Data Export endpoints: JSON, GeoJSON, and CSV reports.
"""
import csv
import io
import json
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.exceptions import FileNotFoundInDbError
from app.db.session import get_db
from app.repositories.file_repository import FileRepository
from app.repositories.feature_repository import FeatureRepository
from app.utils.geo_math import convert_area_units, convert_length_units

router = APIRouter(prefix="/files/{file_id}/export", tags=["Export"])


@router.get(
    "/json",
    summary="Export Measurements as JSON",
    description="Download complete dataset measurements and metadata as JSON.",
)
def export_json(
    file_id: str,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    file_repo = FileRepository(db)
    feature_repo = FeatureRepository(db)

    uploaded_file = file_repo.get_by_id(file_id)
    if not uploaded_file:
        raise FileNotFoundInDbError(file_id)

    features = feature_repo.get_all_by_file_id(file_id)
    feature_items = []
    for f in features:
        feature_items.append({
            "feature_id": f.id,
            "feature_index": f.feature_index,
            "geometry_type": f.geometry_type,
            "is_valid": f.is_valid,
            "was_repaired": f.was_repaired,
            "measurement_status": f.measurement_status,
            "area_m2": f.area_m2,
            "area": convert_area_units(f.area_m2) if f.area_m2 is not None else None,
            "length_m": f.length_m,
            "length": convert_length_units(f.length_m) if f.length_m is not None else None,
            "sub_measurements": f.sub_measurements,
            "properties": f.properties,
            "warnings": f.warnings,
        })

    payload = {
        "file": {
            "id": uploaded_file.id,
            "filename": uploaded_file.original_filename,
            "file_type": uploaded_file.file_type,
            "source_crs": uploaded_file.source_crs,
            "measurement_crs": uploaded_file.measurement_crs,
            "crs_strategy": uploaded_file.crs_strategy,
            "feature_count": uploaded_file.feature_count,
            "status": uploaded_file.status,
            "processing_time_ms": uploaded_file.processing_time_ms,
        },
        "features": feature_items,
    }

    json_str = json.dumps(payload, indent=2, default=str)
    buffer = io.BytesIO(json_str.encode("utf-8"))
    filename = f"{uploaded_file.stored_filename}_export.json"

    return StreamingResponse(
        buffer,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )


@router.get(
    "/geojson",
    summary="Export Features as GeoJSON",
    description="Download dataset as standard GeoJSON with measurement attributes.",
)
def export_geojson(
    file_id: str,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    file_repo = FileRepository(db)
    feature_repo = FeatureRepository(db)

    uploaded_file = file_repo.get_by_id(file_id)
    if not uploaded_file:
        raise FileNotFoundInDbError(file_id)

    features = feature_repo.get_all_by_file_id(file_id)
    geojson_features = []
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

        geojson_features.append({
            "type": "Feature",
            "id": f.id,
            "geometry": f.geometry,
            "properties": props,
            "bbox": f.bbox,
        })

    collection = {
        "type": "FeatureCollection",
        "name": uploaded_file.original_filename,
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": geojson_features,
    }

    json_str = json.dumps(collection, indent=2, default=str)
    buffer = io.BytesIO(json_str.encode("utf-8"))
    filename = f"{uploaded_file.stored_filename}.geojson"

    return StreamingResponse(
        buffer,
        media_type="application/geo+json",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )


@router.get(
    "/csv",
    summary="Export Measurements as CSV",
    description="Download feature measurement report in tabular CSV format.",
)
def export_csv(
    file_id: str,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    file_repo = FileRepository(db)
    feature_repo = FeatureRepository(db)

    uploaded_file = file_repo.get_by_id(file_id)
    if not uploaded_file:
        raise FileNotFoundInDbError(file_id)

    features = feature_repo.get_all_by_file_id(file_id)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Feature_ID",
        "Feature_Index",
        "Geometry_Type",
        "Is_Valid",
        "Was_Repaired",
        "Measurement_Status",
        "Area_m2",
        "Area_km2",
        "Area_ha",
        "Area_acres",
        "Length_m",
        "Length_km",
        "Length_miles",
        "Length_feet",
        "Properties_JSON",
        "Warnings",
    ])

    for f in features:
        area_conv = convert_area_units(f.area_m2) if f.area_m2 is not None else {}
        len_conv = convert_length_units(f.length_m) if f.length_m is not None else {}

        writer.writerow([
            f.id,
            f.feature_index,
            f.geometry_type,
            "TRUE" if f.is_valid else "FALSE",
            "TRUE" if f.was_repaired else "FALSE",
            f.measurement_status,
            area_conv.get("area_m2", ""),
            area_conv.get("area_km2", ""),
            area_conv.get("area_ha", ""),
            area_conv.get("area_acres", ""),
            len_conv.get("length_m", ""),
            len_conv.get("length_km", ""),
            len_conv.get("length_miles", ""),
            len_conv.get("length_feet", ""),
            json.dumps(f.properties or {}, default=str),
            "; ".join(f.warnings or []),
        ])

    output.seek(0)
    bytes_buffer = io.BytesIO(output.getvalue().encode("utf-8"))
    filename = f"{uploaded_file.stored_filename}_measurements.csv"

    return StreamingResponse(
        bytes_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )
