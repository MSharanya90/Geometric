"""
Security utilities for file validation, sanitization, and ZIP safety.
"""
import os
import re
import shutil
import uuid
import zipfile
from pathlib import Path
from typing import Tuple, Set

from app.core.config import settings
from app.core.exceptions import (
    FileTooLargeError,
    MaliciousZipError,
    UnsupportedFileTypeError,
)
from app.core.logging import logger


def generate_unique_id() -> str:
    """Generate a collision-resistant unique file identifier."""
    return uuid.uuid4().hex[:12]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize an uploaded filename.
    Never trust user-supplied filenames.
    Strip path characters and dangerous characters.
    """
    clean_name = os.path.basename(filename)
    # Remove any non-alphanumeric, dot, underscore, dash
    clean_name = re.sub(r"[^a-zA-Z0-9._-]", "_", clean_name)
    # Ensure not empty
    if not clean_name or clean_name.startswith("."):
        clean_name = f"dataset_{generate_unique_id()}"
    return clean_name


def validate_file_metadata(filename: str, content_type: str, file_size: int) -> str:
    """
    Validate file extension, size, and detect file type ('KML' or 'SHAPEFILE_ZIP').
    Raises appropriate GeoMeasureException on failure.
    """
    # Size check
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        logger.warning("Upload rejected: file size %d exceeds limit %d", file_size, max_bytes)
        raise FileTooLargeError(settings.MAX_UPLOAD_SIZE_MB)

    # Extension check
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        logger.warning("Upload rejected: unsupported extension '%s'", ext)
        raise UnsupportedFileTypeError(
            f"Unsupported file extension '{ext}'. Only KML (.kml) and ZIP Shapefiles (.zip) are allowed."
        )

    if ext == ".kml":
        return "KML"
    elif ext == ".zip":
        return "SHAPEFILE_ZIP"

    raise UnsupportedFileTypeError()


def inspect_and_extract_zip(zip_path: Path, target_dir: Path) -> Path:
    """
    Inspect a ZIP archive for zip bombs and path traversal vulnerabilities.
    Extracts safely into target_dir.
    Returns path to the primary .shp file.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    resolved_target = target_dir.resolve()

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            infolist = zf.infolist()

            # Entry count limit check
            if len(infolist) > settings.MAX_ZIP_ENTRIES:
                raise MaliciousZipError(
                    f"ZIP contains {len(infolist)} entries, exceeding maximum allowed limit of {settings.MAX_ZIP_ENTRIES}"
                )

            total_uncompressed = 0
            compressed_size = os.path.getsize(zip_path) or 1
            max_uncompressed_bytes = settings.MAX_TOTAL_UNCOMPRESSED_SIZE_MB * 1024 * 1024

            shp_files = []

            for info in infolist:
                # 1. Path traversal check (ZipSlip)
                # Ensure no absolute paths or parent directory traversal
                entry_name = info.filename
                if os.path.isabs(entry_name) or ".." in entry_name.replace("\\", "/").split("/"):
                    raise MaliciousZipError(
                        f"Potential directory traversal attack detected in entry: '{entry_name}'"
                    )

                # 2. Size & Ratio check (Zip Bomb)
                total_uncompressed += info.file_size
                if total_uncompressed > max_uncompressed_bytes:
                    raise MaliciousZipError(
                        f"Uncompressed size exceeds limit of {settings.MAX_TOTAL_UNCOMPRESSED_SIZE_MB} MB"
                    )

                if info.compress_size > 0:
                    ratio = info.file_size / info.compress_size
                    if ratio > settings.MAX_UNCOMPRESSED_RATIO:
                        raise MaliciousZipError(
                            f"Suspicious compression ratio ({ratio:.1f}x) detected in file '{info.filename}'"
                        )

                # Check destination path before extraction
                dest_path = (target_dir / entry_name).resolve()
                if not str(dest_path).startswith(str(resolved_target)):
                    raise MaliciousZipError(
                        f"Extracted path resolves outside destination directory: '{dest_path}'"
                    )

                if entry_name.lower().endswith(".shp") and not entry_name.startswith("__MACOSX"):
                    shp_files.append(entry_name)

            # Check if valid shapefile exists
            if not shp_files:
                raise MaliciousZipError("ZIP archive does not contain a primary .shp Shapefile.")

            # Perform safe extraction
            for info in infolist:
                zf.extract(info, target_dir)

            # Find the primary .shp file
            primary_shp = (target_dir / shp_files[0]).resolve()
            return primary_shp

    except zipfile.BadZipFile as e:
        raise MaliciousZipError(f"Corrupted or invalid ZIP archive: {str(e)}")


def cleanup_directory(path: Path) -> None:
    """Safely delete temporary directory and its contents."""
    try:
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
            logger.debug("Cleaned up directory: %s", path)
    except Exception as e:
        logger.warning("Failed to clean up directory %s: %s", path, str(e))
