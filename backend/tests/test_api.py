"""
End-to-end API integration tests for all REST endpoints.
"""
from fastapi import status


def test_full_api_lifecycle(client, sample_kml_path):
    # 1. Health check
    h_res = client.get("/health")
    assert h_res.status_code == status.HTTP_200_OK
    assert h_res.json()["status"] == "healthy"

    # 2. Upload sample KML
    with open(sample_kml_path, "rb") as f:
        file_bytes = f.read()

    upload_res = client.post(
        "/api/v1/files/",
        files={"file": ("campus_survey.kml", file_bytes, "application/vnd.google-earth.kml+xml")},
    )
    assert upload_res.status_code == status.HTTP_201_CREATED
    file_id = upload_res.json()["file"]["id"]
    assert file_id is not None

    # 3. List files
    list_res = client.get("/api/v1/files/")
    assert list_res.status_code == status.HTTP_200_OK
    files_list = list_res.json()
    assert any(f["id"] == file_id for f in files_list)

    # 4. Get file detail
    detail_res = client.get(f"/api/v1/files/{file_id}")
    assert detail_res.status_code == status.HTTP_200_OK
    detail_data = detail_res.json()
    assert detail_data["id"] == file_id
    assert detail_data["file_type"] == "KML"
    assert detail_data["feature_count"] > 0

    # 5. Get paginated measurements
    meas_res = client.get(f"/api/v1/files/{file_id}/measurements?page=1&page_size=10")
    assert meas_res.status_code == status.HTTP_200_OK
    meas_data = meas_res.json()
    assert meas_data["file_id"] == file_id
    assert len(meas_data["results"]) > 0

    # 6. Filter measurements by geometry_type=Polygon
    poly_res = client.get(f"/api/v1/files/{file_id}/measurements?geometry_type=Polygon")
    assert poly_res.status_code == status.HTTP_200_OK
    poly_data = poly_res.json()
    assert all(r["geometry_type"] == "Polygon" for r in poly_data["results"])

    # 7. Get summary statistics
    sum_res = client.get(f"/api/v1/files/{file_id}/summary")
    assert sum_res.status_code == status.HTTP_200_OK
    sum_data = sum_res.json()
    assert sum_data["file_id"] == file_id
    stats = sum_data["summary"]
    assert stats["total_features"] > 0
    assert stats["number_of_polygons"] > 0
    assert stats["total_polygon_area_m2"] > 0

    # 8. Get GeoJSON
    geo_res = client.get(f"/api/v1/files/{file_id}/geojson")
    assert geo_res.status_code == status.HTTP_200_OK
    geo_data = geo_res.json()
    assert geo_data["type"] == "FeatureCollection"
    assert len(geo_data["features"]) > 0
    first_feat = geo_data["features"][0]
    assert "geometry" in first_feat
    assert "properties" in first_feat
    assert "feature_id" in first_feat["properties"]

    # 9. Delete file
    del_res = client.delete(f"/api/v1/files/{file_id}")
    assert del_res.status_code == status.HTTP_204_NO_CONTENT

    # 10. Verify 404 after deletion
    verify_res = client.get(f"/api/v1/files/{file_id}")
    assert verify_res.status_code == status.HTTP_404_NOT_FOUND
