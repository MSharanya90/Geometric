"""
Unit tests for geometry validation, repair, bounding box, and topology checks.
"""
from app.services.geometry_service import GeometryService


def test_valid_polygon_validation():
    geom_service = GeometryService()
    # A standard closed square polygon
    coords = [
        [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]
    ]
    is_valid, was_repaired, repaired, warnings = geom_service.validate_and_repair("Polygon", coords)
    assert is_valid is True
    assert was_repaired is False
    assert len(warnings) == 0
    assert repaired == coords


def test_unclosed_polygon_automatic_repair():
    geom_service = GeometryService()
    # Unclosed polygon (first != last)
    unclosed_coords = [
        [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
    ]
    is_valid, was_repaired, repaired, warnings = geom_service.validate_and_repair("Polygon", unclosed_coords)
    assert was_repaired is True
    assert len(warnings) > 0
    # Must now be closed
    assert repaired[0][0] == repaired[0][-1]


def test_polygon_duplicate_vertices_removal():
    geom_service = GeometryService()
    # Consecutive duplicate vertices
    redundant_coords = [
        [[0.0, 0.0], [0.0, 0.0], [5.0, 0.0], [5.0, 5.0], [0.0, 5.0], [0.0, 0.0]]
    ]
    is_valid, was_repaired, repaired, warnings = geom_service.validate_and_repair("Polygon", redundant_coords)
    assert was_repaired is True
    assert len(repaired[0]) < len(redundant_coords[0])


def test_linestring_validation_and_deduplication():
    geom_service = GeometryService()
    line_coords = [[0.0, 0.0], [0.0, 0.0], [5.0, 5.0], [10.0, 10.0]]
    is_valid, was_repaired, repaired, warnings = geom_service.validate_and_repair("LineString", line_coords)
    assert was_repaired is True
    assert len(repaired) == 3


def test_empty_null_geometry_handling():
    geom_service = GeometryService()
    is_valid, was_repaired, repaired, warnings = geom_service.validate_and_repair("Polygon", [])
    assert is_valid is False
    assert was_repaired is False
    assert "empty" in warnings[0].lower()


def test_bounding_box_computation():
    geom_service = GeometryService()
    coords = [
        [[12.5, 45.2], [13.1, 45.2], [13.1, 46.0], [12.5, 46.0], [12.5, 45.2]]
    ]
    bbox = geom_service.compute_bbox(coords)
    assert bbox == [12.5, 45.2, 13.1, 46.0]
