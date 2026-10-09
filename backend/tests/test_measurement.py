"""
Unit tests for the measurement engine and unit conversions.
"""
from app.services.measurement_service import MeasurementService
from app.utils.geo_math import convert_area_units, convert_length_units


def test_polygon_area_exact():
    engine = MeasurementService()
    # 100m x 100m square in projected meters
    square_coords = [
        [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0], [0.0, 0.0]]
    ]
    res = engine.measure_feature("Polygon", square_coords)
    assert res["measurement_available"] is True
    assert res["status"] == "SUCCESS"
    assert res["area_m2"] == 10000.0

    # Conversions
    area_dict = res["area"]
    assert area_dict["area_m2"] == 10000.0
    assert area_dict["area_ha"] == 1.0
    assert area_dict["area_km2"] == 0.01
    assert 2.45 < area_dict["area_acres"] < 2.50


def test_polygon_with_hole_area():
    engine = MeasurementService()
    # 100m x 100m exterior (10,000 m2) with 20m x 20m interior hole (400 m2) -> 9,600 m2
    exterior = [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0], [0.0, 0.0]]
    hole = [[10.0, 10.0], [30.0, 10.0], [30.0, 30.0], [10.0, 30.0], [10.0, 10.0]]
    poly_coords = [exterior, hole]

    res = engine.measure_feature("Polygon", poly_coords)
    assert res["measurement_available"] is True
    assert res["area_m2"] == 9600.0


def test_multipolygon_area_and_sub_measurements():
    engine = MeasurementService()
    poly1 = [[[0.0, 0.0], [50.0, 0.0], [50.0, 50.0], [0.0, 50.0], [0.0, 0.0]]]  # 2500 m2
    poly2 = [[[100.0, 100.0], [200.0, 100.0], [200.0, 200.0], [100.0, 200.0], [100.0, 100.0]]]  # 10000 m2
    multi_coords = [poly1, poly2]

    res = engine.measure_feature("MultiPolygon", multi_coords)
    assert res["measurement_available"] is True
    assert res["area_m2"] == 12500.0
    assert len(res["sub_measurements"]) == 2
    assert res["sub_measurements"][0]["area_m2"] == 2500.0
    assert res["sub_measurements"][1]["area_m2"] == 10000.0


def test_linestring_length_exact():
    engine = MeasurementService()
    # 3 segments: 300m East, 400m North (hypot=500m diagonal) + 500m East -> total 1000m
    line_coords = [
        [0.0, 0.0],
        [300.0, 400.0],  # 500m
        [800.0, 400.0],  # 500m
    ]
    res = engine.measure_feature("LineString", line_coords)
    assert res["measurement_available"] is True
    assert res["length_m"] == 1000.0
    length_dict = res["length"]
    assert length_dict["length_m"] == 1000.0
    assert length_dict["length_km"] == 1.0
    assert 0.62 < length_dict["length_miles"] < 0.63
    assert 3280.0 < length_dict["length_feet"] < 3282.0


def test_multilinestring_length():
    engine = MeasurementService()
    line1 = [[0.0, 0.0], [100.0, 0.0]]  # 100m
    line2 = [[0.0, 0.0], [0.0, 200.0]]  # 200m
    res = engine.measure_feature("MultiLineString", [line1, line2])
    assert res["measurement_available"] is True
    assert res["length_m"] == 300.0
    assert len(res["sub_measurements"]) == 2


def test_point_measurement_skip():
    engine = MeasurementService()
    res = engine.measure_feature("Point", [500000.0, 4000000.0])
    assert res["measurement_available"] is False
    assert res["status"] == "SKIPPED"
    assert "Point geometry does not require measurement" in res["reason"]
