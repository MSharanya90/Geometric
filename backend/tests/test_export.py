"""
Tests for Data Export endpoints (JSON, GeoJSON, CSV).
"""
import json
import csv
import io
from fastapi import status


def test_export_endpoints(client, sample_shapefile_path):
    # Upload shapefile to get a file ID
    with open(sample_shapefile_path, "rb") as f:
        file_bytes = f.read()

    upload_res = client.post(
        "/api/v1/files/",
        files={"file": ("parcels.zip", file_bytes, "application/zip")},
    )
    assert upload_res.status_code == status.HTTP_201_CREATED
    file_id = upload_res.json()["file"]["id"]

    # 1. Export JSON
    json_res = client.get(f"/api/v1/files/{file_id}/export/json")
    assert json_res.status_code == status.HTTP_200_OK
    assert "application/json" in json_res.headers["content-type"]
    exported_data = json.loads(json_res.content.decode("utf-8"))
    assert "file" in exported_data
    assert "features" in exported_data
    assert len(exported_data["features"]) == 3

    # 2. Export GeoJSON
    geojson_res = client.get(f"/api/v1/files/{file_id}/export/geojson")
    assert geojson_res.status_code == status.HTTP_200_OK
    assert "application/geo+json" in geojson_res.headers["content-type"]
    geojson_data = json.loads(geojson_res.content.decode("utf-8"))
    assert geojson_data["type"] == "FeatureCollection"
    assert len(geojson_data["features"]) == 3

    # 3. Export CSV
    csv_res = client.get(f"/api/v1/files/{file_id}/export/csv")
    assert csv_res.status_code == status.HTTP_200_OK
    assert "text/csv" in csv_res.headers["content-type"]
    csv_text = csv_res.content.decode("utf-8")
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)
    # Header + 3 feature rows
    assert len(rows) == 4
    header = rows[0]
    assert "Feature_ID" in header
    assert "Area_m2" in header
    assert "Geometry_Type" in header
