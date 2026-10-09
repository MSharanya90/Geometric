"""
Custom exceptions and error response definitions for GeoMeasure.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class GeoMeasureException(HTTPException):
    """Base exception class for GeoMeasure platform errors."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "details": self.details,
            },
        )


class UnsupportedFileTypeError(GeoMeasureException):
    def __init__(self, message: str = "Only KML and ZIP Shapefile datasets are supported."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="UNSUPPORTED_FILE_TYPE",
            message=message,
        )


class FileTooLargeError(GeoMeasureException):
    def __init__(self, max_size_mb: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            code="FILE_TOO_LARGE",
            message=f"Uploaded file exceeds maximum allowed size of {max_size_mb} MB.",
            details={"max_size_mb": max_size_mb},
        )


class MaliciousZipError(GeoMeasureException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="MALICIOUS_ZIP_DETECTED",
            message=f"ZIP archive failed security checks: {reason}",
            details={"reason": reason},
        )


class InvalidDatasetError(GeoMeasureException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="INVALID_DATASET",
            message=message,
            details=details,
        )


class FileNotFoundInDbError(GeoMeasureException):
    def __init__(self, file_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="FILE_NOT_FOUND",
            message=f"Geospatial file with ID '{file_id}' was not found.",
            details={"file_id": file_id},
        )


class CRSTransformationError(GeoMeasureException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="CRS_TRANSFORMATION_ERROR",
            message=message,
            details=details,
        )
