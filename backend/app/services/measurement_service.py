"""
Geospatial Measurement Engine.
Performs precise measurements on projected coordinates (meters):
- Polygon: area in m2, km2, ha, acres
- MultiPolygon: total area and individual polygon areas
- LineString: length in m, km, miles, feet
- MultiLineString: total length and individual line lengths
- Point / MultiPoint: graceful measurement_available=false indicator
"""
from typing import Dict, Any, List, Optional, Tuple
from app.utils.geo_math import (
    calculate_polygon_with_holes_area,
    planar_linestring_length,
    convert_area_units,
    convert_length_units,
)
from app.core.logging import logger

try:
    import shapely
    from shapely.geometry import shape
    HAS_SHAPELY = True
except Exception:
    HAS_SHAPELY = False


class MeasurementService:
    """Dedicated measurement engine for projected geospatial features."""

    def __init__(self) -> None:
        self.has_shapely = HAS_SHAPELY

    def measure_feature(
        self,
        geometry_type: str,
        projected_coordinates: Any
    ) -> Dict[str, Any]:
        """
        Measure a feature using its projected coordinates (in meters).
        Returns a dictionary with measurement details, unit conversions, and status.
        """
        if not projected_coordinates:
            return {
                "measurement_available": False,
                "status": "FAILED",
                "reason": "Empty or null geometry coordinates."
            }

        # 1. Point / MultiPoint
        if geometry_type in ("Point", "MultiPoint"):
            return {
                "measurement_available": False,
                "status": "SKIPPED",
                "reason": "Point geometry does not require measurement."
            }

        # 2. Polygon
        if geometry_type == "Polygon":
            area_m2 = self._calculate_polygon_area(projected_coordinates)
            return {
                "measurement_available": True,
                "status": "SUCCESS",
                "area_m2": area_m2,
                "area": convert_area_units(area_m2),
                "length_m": None,
                "length": None,
                "sub_measurements": None,
            }

        # 3. MultiPolygon
        if geometry_type == "MultiPolygon":
            total_area_m2, individual_areas = self._calculate_multipolygon_area(projected_coordinates)
            return {
                "measurement_available": True,
                "status": "SUCCESS",
                "area_m2": total_area_m2,
                "area": convert_area_units(total_area_m2),
                "length_m": None,
                "length": None,
                "sub_measurements": individual_areas,
            }

        # 4. LineString
        if geometry_type == "LineString":
            length_m = self._calculate_linestring_length(projected_coordinates)
            return {
                "measurement_available": True,
                "status": "SUCCESS",
                "area_m2": None,
                "area": None,
                "length_m": length_m,
                "length": convert_length_units(length_m),
                "sub_measurements": None,
            }

        # 5. MultiLineString
        if geometry_type == "MultiLineString":
            total_length_m, individual_lengths = self._calculate_multilinestring_length(projected_coordinates)
            return {
                "measurement_available": True,
                "status": "SUCCESS",
                "area_m2": None,
                "area": None,
                "length_m": total_length_m,
                "length": convert_length_units(total_length_m),
                "sub_measurements": individual_lengths,
            }

        # 6. Fallback / Unknown Geometry
        return {
            "measurement_available": False,
            "status": "SKIPPED",
            "reason": f"Measurement not supported for geometry type '{geometry_type}'."
        }

    def _calculate_polygon_area(self, rings: List[List[List[float]]]) -> float:
        """Calculate area for a Polygon (exterior ring minus interior rings)."""
        if not rings or not rings[0]:
            return 0.0

        if self.has_shapely:
            try:
                poly = shape({"type": "Polygon", "coordinates": rings})
                return float(poly.area)
            except Exception:
                pass

        ext_ring = [(float(pt[0]), float(pt[1])) for pt in rings[0]]
        int_rings = []
        if len(rings) > 1:
            for hole in rings[1:]:
                int_rings.append([(float(pt[0]), float(pt[1])) for pt in hole])

        return calculate_polygon_with_holes_area(ext_ring, int_rings)

    def _calculate_multipolygon_area(self, polygons: List[List[List[List[float]]]]) -> Tuple[float, List[Dict[str, Any]]]:
        """Calculate total and individual areas for a MultiPolygon."""
        total_m2 = 0.0
        individual = []

        for idx, poly_rings in enumerate(polygons):
            poly_area_m2 = self._calculate_polygon_area(poly_rings)
            total_m2 += poly_area_m2
            individual.append({
                "part_index": idx,
                "area_m2": round(poly_area_m2, 2),
                **convert_area_units(poly_area_m2)
            })

        return total_m2, individual

    def _calculate_linestring_length(self, coords: List[List[float]]) -> float:
        """Calculate length for a LineString."""
        if not coords or len(coords) < 2:
            return 0.0

        if self.has_shapely:
            try:
                line = shape({"type": "LineString", "coordinates": coords})
                return float(line.length)
            except Exception:
                pass

        pts = [(float(pt[0]), float(pt[1])) for pt in coords]
        return planar_linestring_length(pts)

    def _calculate_multilinestring_length(self, lines: List[List[List[float]]]) -> Tuple[float, List[Dict[str, Any]]]:
        """Calculate total and individual lengths for a MultiLineString."""
        total_len_m = 0.0
        individual = []

        for idx, line_coords in enumerate(lines):
            line_len_m = self._calculate_linestring_length(line_coords)
            total_len_m += line_len_m
            individual.append({
                "part_index": idx,
                "length_m": round(line_len_m, 2),
                **convert_length_units(line_len_m)
            })

        return total_len_m, individual
