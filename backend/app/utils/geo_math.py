"""
Geodesic and spatial mathematical utilities.
Provides:
- WGS84 Ellipsoidal Vincenty & Haversine geodesic distance calculation
- Transverse Mercator / Universal Transverse Mercator (UTM) forward and inverse projection
- Planar Shoelace polygon area calculation
- Planar line string length calculation
- Canonical measurement unit conversions (Area: m2, km2, ha, acres; Length: m, km, mi, ft)
"""
import math
from typing import List, Tuple, Dict, Any, Optional

# WGS84 Ellipsoid constants
WGS84_A = 6378137.0          # Semi-major axis (meters)
WGS84_F = 1.0 / 298.257223563  # Flattening
WGS84_B = WGS84_A * (1.0 - WGS84_F)  # Semi-minor axis (meters)
WGS84_E2 = 2.0 * WGS84_F - WGS84_F ** 2  # First eccentricity squared
WGS84_E_PRIME2 = (WGS84_A ** 2 - WGS84_B ** 2) / (WGS84_B ** 2)  # Second eccentricity squared


def get_utm_epsg_for_centroid(lon: float, lat: float) -> Tuple[int, str]:
    """
    Determine the optimal UTM EPSG code for a dataset centroid.
    UTM zones range from 1 to 60.
    Northern hemisphere: EPSG:32601 - 32660
    Southern hemisphere: EPSG:32701 - 32760
    """
    # Normalize longitude to [-180, 180)
    lon_norm = ((lon + 180.0) % 360.0) - 180.0
    zone = int((lon_norm + 180.0) / 6.0) + 1
    if zone > 60:
        zone = 60
    elif zone < 1:
        zone = 1

    is_north = lat >= 0.0
    epsg_code = 32600 + zone if is_north else 32700 + zone
    strategy_desc = f"UTM Zone {zone}{'N' if is_north else 'S'} (EPSG:{epsg_code}) selected from dataset centroid ({lat:.4f}, {lon:.4f})"
    return epsg_code, strategy_desc


def latlon_to_utm(lon: float, lat: float, zone: Optional[int] = None) -> Tuple[float, float, int, bool]:
    """
    Project (longitude, latitude) in degrees into UTM (easting, northing) in meters.
    Uses Karney-accurate Transverse Mercator formulation for high fidelity.
    """
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    if zone is None:
        lon_norm = ((lon + 180.0) % 360.0) - 180.0
        zone = int((lon_norm + 180.0) / 6.0) + 1
        if zone > 60:
            zone = 60
        elif zone < 1:
            zone = 1

    is_north = lat >= 0.0

    # Central meridian of zone
    lon0 = math.radians((zone - 1) * 6 - 180 + 3)
    k0 = 0.9996  # UTM scale factor
    false_easting = 500000.0
    false_northing = 0.0 if is_north else 10000000.0

    delta_lon = lon_rad - lon0

    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    tan_lat = math.tan(lat_rad)

    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_lat ** 2)
    t = tan_lat ** 2
    c = WGS84_E_PRIME2 * (cos_lat ** 2)
    a = cos_lat * delta_lon

    # Meridional arc calculation M
    m = WGS84_A * (
        (1.0 - WGS84_E2 / 4.0 - 3.0 * (WGS84_E2 ** 2) / 64.0 - 5.0 * (WGS84_E2 ** 3) / 256.0) * lat_rad
        - (3.0 * WGS84_E2 / 8.0 + 3.0 * (WGS84_E2 ** 2) / 32.0 + 45.0 * (WGS84_E2 ** 3) / 1024.0) * math.sin(2.0 * lat_rad)
        + (15.0 * (WGS84_E2 ** 2) / 256.0 + 45.0 * (WGS84_E2 ** 3) / 1024.0) * math.sin(4.0 * lat_rad)
        - (35.0 * (WGS84_E2 ** 3) / 3072.0) * math.sin(6.0 * lat_rad)
    )

    # Easting
    easting = false_easting + k0 * n * (
        a
        + (1.0 - t + c) * (a ** 3) / 6.0
        + (5.0 - 18.0 * t + t ** 2 + 72.0 * c - 58.0 * WGS84_E_PRIME2) * (a ** 5) / 120.0
    )

    # Northing
    northing = false_northing + k0 * (
        m
        + n * tan_lat * (
            (a ** 2) / 2.0
            + (5.0 - t + 9.0 * c + 4.0 * (c ** 2)) * (a ** 4) / 24.0
            + (61.0 - 58.0 * t + t ** 2 + 600.0 * c - 330.0 * WGS84_E_PRIME2) * (a ** 6) / 720.0
        )
    )

    return easting, northing, zone, is_north


def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate geodesic distance in meters between two (lon, lat) points using Haversine formula.
    """
    lon1, lat1 = coord1[0], coord1[1]
    lon2, lat2 = coord2[0], coord2[1]

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return WGS84_A * c


def planar_linestring_length(coords: List[Tuple[float, float]]) -> float:
    """Calculate Euclidean length of a sequence of 2D projected coordinates in meters."""
    if len(coords) < 2:
        return 0.0
    length = 0.0
    for i in range(len(coords) - 1):
        dx = coords[i + 1][0] - coords[i][0]
        dy = coords[i + 1][1] - coords[i][1]
        length += math.hypot(dx, dy)
    return length


def planar_polygon_area(ring: List[Tuple[float, float]]) -> float:
    """
    Calculate the planar area of a closed ring using the Shoelace formula (surveyor's formula).
    Returns absolute area in square units (m^2 when projected).
    """
    n = len(ring)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += ring[i][0] * ring[j][1]
        area -= ring[j][0] * ring[i][1]
    return abs(area) / 2.0


def calculate_polygon_with_holes_area(exterior_ring: List[Tuple[float, float]], interior_rings: Optional[List[List[Tuple[float, float]]]] = None) -> float:
    """Calculate total polygon area: exterior area minus interior hole areas."""
    ext_area = planar_polygon_area(exterior_ring)
    hole_area = 0.0
    if interior_rings:
        for hole in interior_rings:
            hole_area += planar_polygon_area(hole)
    return max(0.0, ext_area - hole_area)


def convert_area_units(area_m2: float) -> Dict[str, float]:
    """
    Convert canonical area in square meters into all required presentation units:
    - m2: square meters
    - km2: square kilometers
    - ha: hectares (1 ha = 10,000 m2)
    - acres: acres (1 acre = 4046.8564224 m2)
    """
    m2 = round(area_m2, 2)
    km2 = round(area_m2 / 1_000_000.0, 6)
    ha = round(area_m2 / 10_000.0, 4)
    acres = round(area_m2 * 0.00024710538146717, 4)
    return {
        "area_m2": m2,
        "area_km2": km2,
        "area_ha": ha,
        "area_acres": acres,
    }


def convert_length_units(length_m: float) -> Dict[str, float]:
    """
    Convert canonical length in meters into all required presentation units:
    - m: meters
    - km: kilometers
    - mi: miles (1 mi = 1609.344 m)
    - ft: feet (1 ft = 0.3048 m)
    """
    m = round(length_m, 2)
    km = round(length_m / 1000.0, 4)
    miles = round(length_m * 0.00062137119223733, 4)
    feet = round(length_m * 3.2808398950131, 2)
    return {
        "length_m": m,
        "length_km": km,
        "length_miles": miles,
        "length_feet": feet,
    }
