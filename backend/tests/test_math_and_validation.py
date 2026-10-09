"""
Supplementary unit tests for spatial math functions, unit conversions, and validation service.
"""
from app.utils.geo_math import (
    haversine_distance,
    latlon_to_utm,
    convert_area_units,
    convert_length_units,
    planar_polygon_area,
    calculate_polygon_with_holes_area,
    planar_linestring_length,
)
from app.services.validation_service import ValidationService


def test_haversine_distance():
    # Equator 1 degree longitude ~ 111.32 km = 111,319 meters
    dist = haversine_distance((0.0, 0.0), (1.0, 0.0))
    assert 111000 < dist < 112000


def test_latlon_to_utm_direct():
    # Greenwich 0, 51.5 (London) -> UTM zone 30 or 31
    easting, northing, zone, is_north = latlon_to_utm(0.0, 51.5)
    assert zone in (30, 31)
    assert is_north is True
    assert easting > 0
    assert northing > 0


def test_conversions_units():
    area_c = convert_area_units(10000.0)
    assert area_c["area_m2"] == 10000.0
    assert area_c["area_ha"] == 1.0
    assert area_c["area_km2"] == 0.01

    len_c = convert_length_units(1609.344)
    assert len_c["length_m"] == 1609.34
    assert len_c["length_miles"] == 1.0


def test_validation_service():
    val_svc = ValidationService()
    ok, warns = val_svc.validate_feature_structure({"geometry_type": "Polygon", "coordinates": [[[0,0]]]})
    assert ok is True

    bad, warns_bad = val_svc.validate_feature_structure({"geometry_type": "InvalidType", "coordinates": []})
    assert bad is False

    no_coords, _ = val_svc.validate_feature_structure({"geometry_type": "Polygon", "coordinates": None})
    assert no_coords is False


def test_planar_math_helpers():
    # 10x10 square
    ring = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
    assert planar_polygon_area(ring) == 100.0

    # 10x10 with 2x2 hole
    hole = [(1, 1), (3, 1), (3, 3), (1, 3), (1, 1)]
    assert calculate_polygon_with_holes_area(ring, [hole]) == 96.0

    line = [(0, 0), (3, 4)]
    assert planar_linestring_length(line) == 5.0
