"""
Geometry manipulation, validation, repair, and bounding box calculation service.
"""
from typing import Dict, Any, List, Tuple, Optional
from app.core.logging import logger

try:
    import shapely
    from shapely.geometry import shape, mapping
    from shapely.validation import make_valid
    HAS_SHAPELY = True
except Exception:
    HAS_SHAPELY = False


class GeometryService:
    """Service for geometry inspection, bounding box calculation, and safe repair."""

    def __init__(self) -> None:
        self.has_shapely = HAS_SHAPELY

    def compute_bbox(self, coordinates: Any) -> Optional[List[float]]:
        """
        Recursively compute [min_lon, min_lat, max_lon, max_lat] for arbitrary GeoJSON coordinates.
        """
        points = []
        self._extract_all_points(coordinates, points)
        if not points:
            return None

        min_x = min(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_x = max(p[0] for p in points)
        max_y = max(p[1] for p in points)
        return [round(min_x, 6), round(min_y, 6), round(max_x, 6), round(max_y, 6)]

    def _extract_all_points(self, coords: Any, out_list: List[Tuple[float, float]]) -> None:
        """Helper to collect all 2D points from nested coordinate lists."""
        if not coords:
            return
        if isinstance(coords[0], (int, float)):
            out_list.append((float(coords[0]), float(coords[1])))
        else:
            for item in coords:
                self._extract_all_points(item, out_list)

    def validate_and_repair(
        self,
        geom_type: str,
        coordinates: Any
    ) -> Tuple[bool, bool, Any, List[str]]:
        """
        Validate geometry, detect defects (unclosed rings, duplicate vertices, self-intersections),
        and safely repair.
        Returns:
            (is_valid, was_repaired, repaired_or_original_coords, warnings)
        """
        warnings: List[str] = []
        is_valid = True
        was_repaired = False
        repaired_coords = coordinates

        if not coordinates:
            return False, False, coordinates, ["Geometry is empty or null."]

        # 1. Structural topological checks (unclosed rings, duplicate vertices)
        if geom_type in ("Polygon", "MultiPolygon"):
            repaired_coords, repair_warnings, had_repairs = self._repair_polygon_coordinates(
                geom_type, coordinates
            )
            if had_repairs:
                is_valid = False
                was_repaired = True
                warnings.extend(repair_warnings)

        elif geom_type in ("LineString", "MultiLineString"):
            repaired_coords, repair_warnings, had_repairs = self._repair_linestring_coordinates(
                geom_type, coordinates
            )
            if had_repairs:
                is_valid = False
                was_repaired = True
                warnings.extend(repair_warnings)

        # 2. Advanced topology & self-intersection validation via Shapely if available
        if self.has_shapely:
            try:
                geom_dict = {"type": geom_type, "coordinates": repaired_coords}
                geom_obj = shape(geom_dict)

                if not geom_obj.is_valid:
                    is_valid = False
                    fixed = make_valid(geom_obj)
                    if not fixed.is_empty:
                        fixed_mapping = mapping(fixed)
                        repaired_coords = fixed_mapping["coordinates"]
                        was_repaired = True
                        warnings.append("Geometry was invalid and was repaired before measurement.")
                    else:
                        warnings.append("Geometry is corrupted and could not be repaired.")
            except Exception as e:
                logger.debug("Shapely advanced validation encountered exception: %s", e)

        return is_valid, was_repaired, repaired_coords, warnings

    def _repair_polygon_coordinates(
        self,
        geom_type: str,
        coordinates: Any
    ) -> Tuple[Any, List[str], bool]:
        """Validate rings are closed, remove duplicate vertices, ensure minimum 4 coordinates."""
        warnings: List[str] = []
        had_repairs = False

        def _clean_ring(ring: List[Any]) -> List[List[float]]:
            nonlocal had_repairs
            if not ring:
                return []
            # Deduplicate consecutive identical vertices
            cleaned: List[List[float]] = [[float(ring[0][0]), float(ring[0][1])]]
            for pt in ring[1:]:
                p_x, p_y = float(pt[0]), float(pt[1])
                if p_x != cleaned[-1][0] or p_y != cleaned[-1][1]:
                    cleaned.append([p_x, p_y])

            if len(cleaned) < len(ring):
                had_repairs = True
                warnings.append("Removed redundant duplicate adjacent vertices.")

            # Ensure ring closure (first coordinate == last coordinate)
            if cleaned and (cleaned[0][0] != cleaned[-1][0] or cleaned[0][1] != cleaned[-1][1]):
                cleaned.append([cleaned[0][0], cleaned[0][1]])
                had_repairs = True
                warnings.append("Unclosed polygon ring was automatically closed.")

            # Minimum 4 coordinates for closed linear ring
            if len(cleaned) < 4:
                had_repairs = True
                warnings.append("Linear ring had insufficient vertices (<4).")

            return cleaned

        if geom_type == "Polygon":
            new_rings = []
            for ring in coordinates:
                new_rings.append(_clean_ring(ring))
            return new_rings, warnings, had_repairs

        elif geom_type == "MultiPolygon":
            new_polys = []
            for poly in coordinates:
                poly_rings = []
                for ring in poly:
                    poly_rings.append(_clean_ring(ring))
                new_polys.append(poly_rings)
            return new_polys, warnings, had_repairs

        return coordinates, warnings, had_repairs

    def _repair_linestring_coordinates(
        self,
        geom_type: str,
        coordinates: Any
    ) -> Tuple[Any, List[str], bool]:
        """Validate linestrings have at least 2 points and deduplicate adjacent identical coordinates."""
        warnings: List[str] = []
        had_repairs = False

        def _clean_line(line: List[Any]) -> List[List[float]]:
            nonlocal had_repairs
            if not line:
                return []
            cleaned: List[List[float]] = [[float(line[0][0]), float(line[0][1])]]
            for pt in line[1:]:
                p_x, p_y = float(pt[0]), float(pt[1])
                if p_x != cleaned[-1][0] or p_y != cleaned[-1][1]:
                    cleaned.append([p_x, p_y])
            if len(cleaned) < len(line):
                had_repairs = True
                warnings.append("Removed duplicate consecutive line vertices.")
            if len(cleaned) < 2:
                had_repairs = True
                warnings.append("LineString has fewer than 2 distinct points.")
            return cleaned

        if geom_type == "LineString":
            cleaned = _clean_line(coordinates)
            return cleaned, warnings, had_repairs
        elif geom_type == "MultiLineString":
            cleaned_lines = [_clean_line(line) for line in coordinates]
            return cleaned_lines, warnings, had_repairs

        return coordinates, warnings, had_repairs
