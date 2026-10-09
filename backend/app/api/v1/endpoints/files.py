"""
File management endpoints: upload, inspect, list, and delete.
"""
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.exceptions import FileNotFoundInDbError
from app.db.session import get_db
from app.repositories.file_repository import FileRepository
from app.schemas.file import FileResponse, FileUploadResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["Files"])


@router.post(
    "/",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Secure Geospatial File Upload",
    description="Upload a KML (.kml) or Zipped Shapefile (.zip). The file is securely inspected, validated, and processed.",
)
async def upload_file(
    file: UploadFile = File(..., description="Geospatial dataset file (.kml or .zip)"),
    db: Session = Depends(get_db),
) -> FileUploadResponse:
    content = await file.read()
    file_service = FileService()
    record = file_service.process_uploaded_file(
        file_bytes=content,
        original_filename=file.filename or "unknown.dat",
        content_type=file.content_type or "application/octet-stream",
        db=db,
    )
    return FileUploadResponse(
        message="Geospatial file uploaded, validated, and measured successfully.",
        file=FileResponse(
            id=record.id,
            filename=record.original_filename,
            file_type=record.file_type,
            file_size=record.file_size,
            feature_count=record.feature_count,
            geometry_types=record.geometry_types or {},
            crs=record.source_crs or "EPSG:4326",
            measurement_crs=record.measurement_crs,
            crs_strategy=record.crs_strategy,
            status=record.status,
            processing_time_ms=record.processing_time_ms,
            created_at=record.created_at,
            updated_at=record.updated_at,
            error_message=record.error_message,
        ),
    )


@router.get(
    "/",
    response_model=List[FileResponse],
    summary="List Uploaded Files",
    description="Retrieve all previously uploaded geospatial datasets.",
)
def list_files(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> List[FileResponse]:
    repo = FileRepository(db)
    records = repo.list_all(limit=limit, offset=offset)
    return [
        FileResponse(
            id=r.id,
            filename=r.original_filename,
            file_type=r.file_type,
            file_size=r.file_size,
            feature_count=r.feature_count,
            geometry_types=r.geometry_types or {},
            crs=r.source_crs or "EPSG:4326",
            measurement_crs=r.measurement_crs,
            crs_strategy=r.crs_strategy,
            status=r.status,
            processing_time_ms=r.processing_time_ms,
            created_at=r.created_at,
            updated_at=r.updated_at,
            error_message=r.error_message,
        )
        for r in records
    ]


@router.get(
    "/{file_id}",
    response_model=FileResponse,
    summary="Get File Information",
    description="Retrieve detailed processing metadata and CRS configuration for a file.",
)
def get_file(
    file_id: str,
    db: Session = Depends(get_db),
) -> FileResponse:
    repo = FileRepository(db)
    record = repo.get_by_id(file_id)
    if not record:
        raise FileNotFoundInDbError(file_id)

    return FileResponse(
        id=record.id,
        filename=record.original_filename,
        file_type=record.file_type,
        file_size=record.file_size,
        feature_count=record.feature_count,
        geometry_types=record.geometry_types or {},
        crs=record.source_crs or "EPSG:4326",
        measurement_crs=record.measurement_crs,
        crs_strategy=record.crs_strategy,
        status=record.status,
        processing_time_ms=record.processing_time_ms,
        created_at=record.created_at,
        updated_at=record.updated_at,
        error_message=record.error_message,
    )


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete File",
    description="Delete a file and all its associated features and measurements.",
)
def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
) -> None:
    repo = FileRepository(db)
    if not repo.delete(file_id):
        raise FileNotFoundInDbError(file_id)
