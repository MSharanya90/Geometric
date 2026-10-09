"""
CRS (Coordinate Reference System) Service.
Responsible for:
- Detecting dataset source CRS
- Identifying geographic vs projected CRS
- Intelligent projected CRS selection for accurate metric measurements
- Transforming geometries between coordinate systems
"""
from typing import Tuple, List, Dict, Any, Optional
from app.core.logging import logger
from app.utils.geo_math import get_utm_epsg_for_centroid, latlon_to_utm

# Optional PyProj import for environments with compiled binaries
try:
    import pyproj
    HAS_PYPROJ = True
except Exception:
    HAS_PYPROJ = False


class CRSService:
    """Service for CRS detection, strategy selection, and coordinate transformation."""

    def __init__(self) -> None:
        self.has_pyproj = HAS_PYPROJ

    def detect_source_crs_from_prj(self, prj_content: Optional[str]) -> str:
        """
        Detect EPSG or CRS string from ESRI .prj content.
        Defaults to EPSG:4326 if .prj is missing or empty.
        """
        if not prj_content or not prj_content.strip():
            logger.info("No .prj file found; defaulting source CRS to EPSG:4326 (WGS84)")
            return "EPSG:4326"

        prj_clean = prj_content.strip()

        if self.has_pyproj:
            try:
                crs = pyproj.CRS.from_user_input(prj_clean)
                epsg = crs.to_epsg()
                if epsg:
                    return f"EPSG:{epsg}"
                return crs.name or "CUSTOM_PROJECTED"
            except Exception as e:
                logger.warning("PyProj could not parse PRJ: %s. Analyzing WKT tokens.", e)

        # Fallback heuristic parser for standard WKT
        upper = prj_clean.upper()
        if "UTM_ZONE_" in upper:
            import re
            match = re.search(r"UTM_ZONE_(\d+)([NS]?)", upper)
            if match:
                zone = int(match.group(1))
                hemi = match.group(2)
                epsg = (32600 + zone) if hemi != "S" else (32700 + zone)
                return f"EPSG:{epsg}"
        elif "WGS_1984" in upper or "WGS 84" in upper or "GEOGCS[\"GCS_WGS_1984\"" in upper:
            return "EPSG:4326"
        elif "NAD_1983" in upper or "NAD83" in upper:
            return "EPSG:4269"

        return "EPSG:4326"

    def select_measurement_crs(
        self,
        source_crs: str,
        bbox: Optional[List[float]] = None
    ) -> Tuple[str, str]:
        """
        Select an optimal projected CRS (in meters) for calculating area and length.
        Never measure directly in geographic degrees (EPSG:4326).
        """
        # If source is already a recognized projected CRS (e.g., UTM or State Plane)
        if source_crs.startswith("EPSG:") and source_crs != "EPSG:4326":
            epsg_num = int(source_crs.replace("EPSG:", ""))
            # If UTM zone (32601-32660 or 32701-32760)
            if (32601 <= epsg_num <= 32660) or (32701 <= epsg_num <= 32760):
                return source_crs, f"Source CRS ({source_crs}) is already an optimal UTM projected CRS"

        # If bounding box is provided: [min_lon, min_lat, max_lon, max_lat]
        if bbox and len(bbox) >= 4:
            centroid_lon = (bbox[0] + bbox[2]) / 2.0
            centroid_lat = (bbox[1] + bbox[3]) / 2.0

            # Check if dataset spans more than 60 degrees of longitude (continental or global)
            lon_span = abs(bbox[2] - bbox[0])
            if lon_span > 60.0:
                # Global dataset
                return (
                    "EPSG:6933",
                    f"Equal Earth / Global projection selected (dataset spans {lon_span:.1f}° longitude)"
                )

            epsg_code, strategy = get_utm_epsg_for_centroid(centroid_lon, centroid_lat)
            return f"EPSG:{epsg_code}", strategy

        # Default fallback: UTM Zone 32N (Central Europe/Global standard fallback)
        return "EPSG:32632", "Default UTM Zone 32N selected (no dataset bbox available)"

    def project_coordinates(
        self,
        coordinates: Any,
        source_crs: str,
        target_crs: str
    ) -> Any:
        """
        Recursively project coordinate lists/tuples from source_crs to target_crs.
        Accepts: [lon, lat], [[lon, lat], ...], [[[lon, lat], ...], ...], etc.
        """
        # Target UTM zone calculation
        target_epsg = 32632
        if target_crs.startswith("EPSG:"):
            try:
                target_epsg = int(target_crs.replace("EPSG:", ""))
            except ValueError:
                pass

        zone = target_epsg % 100 if (32601 <= target_epsg <= 32660 or 32701 <= target_epsg <= 32760) else None

        if self.has_pyproj:
            try:
                transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)
                def _transform_pt(pt: List[float]) -> List[float]:
                    x, y = transformer.transform(pt[0], pt[1])
                    return [x, y]
                return self._apply_recursive(coordinates, _transform_pt)
            except Exception as e:
                logger.debug("PyProj transform failed (%s), using high-precision UTM engine.", e)

        # Fallback to high-precision Karney Transverse Mercator formulation
        def _to_utm_pt(pt: List[float]) -> List[float]:
            lon, lat = float(pt[0]), float(pt[1])
            x, y, _, _ = latlon_to_utm(lon, lat, zone=zone)
            return [x, y]

        return self._apply_recursive(coordinates, _to_utm_pt)

    def _apply_recursive(self, coords: Any, fn: Any) -> Any:
        """Recursively apply projection function to coordinate arrays."""
        if not coords:
            return []
        if isinstance(coords[0], (int, float)):
            # Single point [x, y] or [x, y, z]
            res = fn(coords[:2])
            if len(coords) > 2:
                res.append(coords[2])  # preserve z if present
            return res
        return [self._apply_recursive(c, fn) for c in coords]
