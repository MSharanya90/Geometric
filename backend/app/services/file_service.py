"""
Central File Processing Orchestration Service.
Coordinates file upload, security validation, extraction, geometry repair,
CRS transformation, measurement calculation, and persistence.
"""
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import InvalidDatasetError
from app.models.file import UploadedFile
from app.models.feature import Feature
from app.repositories.file_repository import FileRepository
from app.repositories.feature_repository import FeatureRepository
from app.services.crs_service import CRSService
from app.services.geometry_service import GeometryService
from app.services.kml_service import KMLService
from app.services.measurement_service import MeasurementService
from app.services.shapefile_service import ShapefileService
from app.services.validation_service import ValidationService
from app.utils.security import (
    generate_unique_id,
    sanitize_filename,
    validate_file_metadata,
    inspect_and_extract_zip,
    cleanup_directory,
)


class FileService:
    """Service to process geospatial datasets end-to-end."""

    def __init__(self) -> None:
        self.kml_service = KMLService()
        self.shapefile_service = ShapefileService()
        self.crs_service = CRSService()
        self.geometry_service = GeometryService()
        self.measurement_service = MeasurementService()
        self.validation_service = ValidationService()

    def process_uploaded_file(
        self,
        file_bytes: bytes,
        original_filename: str,
        content_type: str,
        db: Session
    ) -> UploadedFile:
        """
        Execute full pipeline:
        Upload -> Validate -> Extract -> Detect Format -> Parse ->
        Validate Geometries -> Detect CRS -> Transform CRS ->
        Measure -> Store -> Clean up -> Return.
        """
        start_time = time.perf_counter()
        file_size = len(file_bytes)

        # 1. Validation & sanitization
        file_type = validate_file_metadata(original_filename, content_type, file_size)
        file_id = generate_unique_id()
        safe_filename = sanitize_filename(original_filename)

        temp_folder = settings.TEMP_DIR / file_id
        temp_folder.mkdir(parents=True, exist_ok=True)
        temp_file_path = temp_folder / safe_filename

        file_repo = FileRepository(db)
        feature_repo = FeatureRepository(db)

        # Initialize UploadedFile record
        uploaded_record = UploadedFile(
            id=file_id,
            original_filename=original_filename,
            stored_filename=safe_filename,
            file_type=file_type,
            file_size=file_size,
            status="PROCESSING",
        )
        file_repo.create(uploaded_record)

        try:
            # Write uploaded bytes to safe temporary path
            with open(temp_file_path, "wb") as f:
                f.write(file_bytes)

            raw_features: List[Dict[str, Any]] = []
            source_crs = "EPSG:4326"

            # 2. Extract and Parse according to detected file format
            if file_type == "KML":
                raw_features = self.kml_service.parse_kml_file(temp_file_path)
                source_crs = "EPSG:4326"
            elif file_type == "SHAPEFILE_ZIP":
                extracted_dir = temp_folder / "extracted"
                primary_shp = inspect_and_extract_zip(temp_file_path, extracted_dir)
                raw_features, prj_content = self.shapefile_service.parse_shapefile(primary_shp)
                source_crs = self.crs_service.detect_source_crs_from_prj(prj_content)

            if not raw_features:
                raise InvalidDatasetError("No valid geospatial features found in the dataset.")

            # 3. Overall bounding box & CRS strategy determination
            all_bboxes = []
            for rf in raw_features:
                b = self.geometry_service.compute_bbox(rf.get("coordinates"))
                if b:
                    all_bboxes.append(b)

            dataset_bbox = None
            if all_bboxes:
                dataset_bbox = [
                    min(b[0] for b in all_bboxes),
                    min(b[1] for b in all_bboxes),
                    max(b[2] for b in all_bboxes),
                    max(b[3] for b in all_bboxes),
                ]

            measurement_crs, crs_strategy = self.crs_service.select_measurement_crs(
                source_crs, dataset_bbox
            )

            # 4. Process each feature with independent error handling
            processed_features: List[Feature] = []
            geometry_type_counts: Dict[str, int] = {}

            for idx, rf in enumerate(raw_features):
                g_type = rf.get("geometry_type", "Unknown")
                orig_coords = rf.get("coordinates")
                props = rf.get("properties", {})
                feature_warnings = []

                geometry_type_counts[g_type] = geometry_type_counts.get(g_type, 0) + 1

                # Validation & Safe Repair
                is_valid, was_repaired, repaired_coords, repair_warns = (
                    self.geometry_service.validate_and_repair(g_type, orig_coords)
                )
                feature_warnings.extend(repair_warns)

                feat_bbox = self.geometry_service.compute_bbox(orig_coords)

                # Project coordinates to measurement CRS
                try:
                    projected_coords = self.crs_service.project_coordinates(
                        repaired_coords, source_crs, measurement_crs
                    )
                except Exception as proj_err:
                    logger.warning("Feature %d projection error: %s", idx, proj_err)
                    projected_coords = repaired_coords
                    feature_warnings.append(f"CRS projection error: {str(proj_err)}")

                # Calculate measurements
                meas_result = self.measurement_service.measure_feature(g_type, projected_coords)
                if meas_result.get("reason"):
                    feature_warnings.append(meas_result["reason"])

                meas_status = meas_result.get("status", "SUCCESS")
                if not is_valid and was_repaired:
                    meas_status = "WARNING"
                elif not is_valid and not was_repaired:
                    meas_status = "FAILED"

                # Standard GeoJSON geometry dict (kept in source/WGS84 for visualization)
                geojson_geom = {
                    "type": g_type,
                    "coordinates": orig_coords,
                }

                feat_record = Feature(
                    uploaded_file_id=file_id,
                    feature_index=idx,
                    geometry_type=g_type,
                    geometry=geojson_geom,
                    bbox=feat_bbox,
                    properties=props,
                    is_valid=is_valid,
                    was_repaired=was_repaired,
                    measurement_status=meas_status,
                    area_m2=meas_result.get("area_m2"),
                    length_m=meas_result.get("length_m"),
                    sub_measurements=meas_result.get("sub_measurements"),
                    warnings=feature_warnings,
                )
                processed_features.append(feat_record)

            # 5. Bulk insert features into database
            feature_repo.bulk_create(processed_features)

            # 6. Update UploadedFile record metadata
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            uploaded_record.source_crs = source_crs
            uploaded_record.measurement_crs = measurement_crs
            uploaded_record.crs_strategy = crs_strategy
            uploaded_record.feature_count = len(processed_features)
            uploaded_record.geometry_types = geometry_type_counts
            uploaded_record.status = "COMPLETED"
            uploaded_record.processing_time_ms = duration_ms
            file_repo.update(uploaded_record)

            logger.info(
                "Successfully processed file %s (ID: %s, %d features) in %d ms",
                original_filename,
                file_id,
                len(processed_features),
                duration_ms,
            )
            return uploaded_record

        except Exception as e:
            logger.error("Failed processing file %s (ID: %s): %s", original_filename, file_id, str(e))
            uploaded_record.status = "FAILED"
            uploaded_record.error_message = str(e)
            file_repo.update(uploaded_record)
            raise
        finally:
            # 7. Secure cleanup of temporary storage
            cleanup_directory(temp_folder)
