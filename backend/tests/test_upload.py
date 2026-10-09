"""
Unit and integration tests for secure file upload and validation.
"""
import io
import zipfile
from pathlib import Path
from fastapi import status


def test_upload_valid_kml(client, sample_kml_path):
    """Test uploading a valid KML file returns 201 and populated metadata."""
    assert sample_kml_path.exists(), "Sample KML must exist"
    with open(sample_kml_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/files/",
        files={"file": ("campus_survey.kml", file_bytes, "application/vnd.google-earth.kml+xml")},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "file" in data
    file_info = data["file"]
    assert file_info["file_type"] == "KML"
    assert file_info["feature_count"] > 0
    assert file_info["status"] == "COMPLETED"
    assert file_info["crs"] == "EPSG:4326"
    assert file_info["measurement_crs"].startswith("EPSG:")
    assert "Polygon" in file_info["geometry_types"]


def test_upload_valid_shapefile_zip(client, sample_shapefile_path):
    """Test uploading a valid zipped Shapefile archive returns 201."""
    assert sample_shapefile_path.exists(), "Sample Shapefile ZIP must exist"
    with open(sample_shapefile_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/v1/files/",
        files={"file": ("parcels_shapefile.zip", file_bytes, "application/zip")},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    file_info = data["file"]
    assert file_info["file_type"] == "SHAPEFILE_ZIP"
    assert file_info["feature_count"] == 3
    assert file_info["status"] == "COMPLETED"
    assert "Polygon" in file_info["geometry_types"]


def test_upload_unsupported_file_extension(client):
    """Test uploading an unsupported extension returns 400 UNSUPPORTED_FILE_TYPE."""
    fake_content = b"This is not a geospatial file."
    response = client.post(
        "/api/v1/files/",
        files={"file": ("report.pdf", fake_content, "application/pdf")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    err = response.json()["error"]
    assert err["code"] == "UNSUPPORTED_FILE_TYPE"


def test_upload_malformed_corrupt_zip(client):
    """Test uploading corrupted ZIP data returns 400 Bad Request."""
    corrupt_bytes = b"PK\x03\x04corrupted_zip_payload_with_invalid_headers"
    response = client.post(
        "/api/v1/files/",
        files={"file": ("bad_archive.zip", corrupt_bytes, "application/zip")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    err = response.json()["error"]
    assert err["code"] == "MALICIOUS_ZIP_DETECTED"


def test_upload_zip_missing_shp_file(client):
    """Test uploading a valid ZIP archive that does not contain a .shp file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("readme.txt", "No shapefile here.")
    buf.seek(0)

    response = client.post(
        "/api/v1/files/",
        files={"file": ("empty_gis.zip", buf.getvalue(), "application/zip")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    err = response.json()["error"]
    assert err["code"] == "MALICIOUS_ZIP_DETECTED"
    assert "primary .shp" in err["message"]


def test_upload_zip_path_traversal_protection(client):
    """Test uploading a ZIP entry attempting path traversal ('../etc/passwd') is blocked."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("../evil.shp", "malicious payload")
    buf.seek(0)

    response = client.post(
        "/api/v1/files/",
        files={"file": ("traversal.zip", buf.getvalue(), "application/zip")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    err = response.json()["error"]
    assert err["code"] == "MALICIOUS_ZIP_DETECTED"
    assert "traversal" in err["message"].lower()
