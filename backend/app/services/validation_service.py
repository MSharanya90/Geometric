"""
Dataset and Feature Validation Service.
Applies quality rules and sanity checks before and after spatial transformations.
"""
from typing import Dict, Any, List, Tuple
from app.core.logging import logger


class ValidationService:
    """Service to evaluate dataset completeness, geometry consistency, and error tolerance."""

    SUPPORTED_GEOMETRIES = {
        "Point",
        "MultiPoint",
        "LineString",
        "MultiLineString",
        "Polygon",
        "MultiPolygon",
        "GeometryCollection"
    }

    def validate_feature_structure(self, raw_feature: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check feature structure and geometry support.
        Returns (is_acceptable, warnings)
        """
        warnings = []
        geom_type = raw_feature.get("geometry_type")
        coords = raw_feature.get("coordinates")

        if not geom_type:
            return False, ["Missing geometry type."]

        if geom_type not in self.SUPPORTED_GEOMETRIES:
            return False, [f"Geometry type '{geom_type}' is not supported."]

        if coords is None:
            return False, ["Geometry coordinates are null."]

        return True, warnings
