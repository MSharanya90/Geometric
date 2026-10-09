"""
Unit tests for CRS detection, intelligent UTM zone selection, and coordinate transformation.
"""
from app.services.crs_service import CRSService
from app.utils.geo_math import get_utm_epsg_for_centroid, latlon_to_utm


def test_utm_zone_selection_northern_hemisphere():
    # San Francisco Bay Area: lon -122.25, lat 37.87 -> UTM Zone 10N (EPSG:32610)
    epsg_code, strategy = get_utm_epsg_for_centroid(-122.25, 37.87)
    assert epsg_code == 32610
    assert "UTM Zone 10N" in strategy
    assert "32610" in strategy


def test_utm_zone_selection_southern_hemisphere():
    # Sydney, Australia: lon 151.20, lat -33.86 -> UTM Zone 56S (EPSG:32756)
    epsg_code, strategy = get_utm_epsg_for_centroid(151.20, -33.86)
    assert epsg_code == 32756
    assert "UTM Zone 56S" in strategy


def test_select_measurement_crs_for_geographic_dataset():
    crs_service = CRSService()
    # Bay Area bounding box
    bbox = [-122.30, 37.80, -122.20, 37.90]
    target_crs, strategy = crs_service.select_measurement_crs("EPSG:4326", bbox)
    assert target_crs == "EPSG:32610"
    assert "UTM Zone 10N" in strategy


def test_select_measurement_crs_for_continental_span():
    crs_service = CRSService()
    # Spanning across >60 degrees of longitude (e.g. Atlantic to Pacific)
    wide_bbox = [-130.0, 30.0, -65.0, 50.0]
    target_crs, strategy = crs_service.select_measurement_crs("EPSG:4326", wide_bbox)
    assert target_crs == "EPSG:6933"
    assert "Equal Earth" in strategy


def test_prj_wkt_parsing():
    crs_service = CRSService()
    wgs84_wkt = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]]]'
    detected = crs_service.detect_source_crs_from_prj(wgs84_wkt)
    assert detected == "EPSG:4326"

    utm_wkt = 'PROJCS["WGS_1984_UTM_Zone_18N",GEOGCS["GCS_WGS_1984"]]'
    detected_utm = crs_service.detect_source_crs_from_prj(utm_wkt)
    assert detected_utm == "EPSG:32618"


def test_coordinate_projection_transformation():
    crs_service = CRSService()
    lon, lat = -122.2580, 37.8720
    coords = [[lon, lat], [lon + 0.001, lat + 0.001]]
    projected = crs_service.project_coordinates(coords, "EPSG:4326", "EPSG:32610")
    assert len(projected) == 2
    # In UTM Zone 10N, easting is around 565000 m and northing is around 4191000 m
    assert 400000 < projected[0][0] < 700000
    assert 4000000 < projected[0][1] < 5000000
