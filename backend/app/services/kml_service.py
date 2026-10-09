"""
KML File Parsing and Feature Extraction Service.
Parses OGC KML 2.0 / 2.2 files safely using lxml / ElementTree.
Extracts Placemarks into standard GeoJSON-compatible feature representations.
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from app.core.logging import logger
from app.core.exceptions import InvalidDatasetError

try:
    from lxml import etree
    HAS_LXML = True
except Exception:
    import xml.etree.ElementTree as etree
    HAS_LXML = False


def _get_tag_name(elem: Any) -> str:
    """Safely extract local tag name in lowercase, ignoring Cython comments or PIs."""
    if not hasattr(elem, "tag") or not isinstance(elem.tag, str):
        return ""
    return elem.tag.split("}")[-1].lower() if "}" in elem.tag else elem.tag.lower()


class KMLService:
    """Service to parse KML files and extract standardized features."""

    def parse_kml_file(self, kml_path: Path) -> List[Dict[str, Any]]:
        """
        Parse KML file and extract list of standardized features:
        [
            {
                "feature_index": 0,
                "geometry_type": "Polygon",
                "coordinates": [...],
                "properties": {"name": "...", ...}
            },
            ...
        ]
        """
        try:
            with open(kml_path, "rb") as f:
                content = f.read()

            if not content.strip():
                raise InvalidDatasetError("KML file is empty.")

            if HAS_LXML:
                parser = etree.XMLParser(recover=True, resolve_entities=False, no_network=True)
                root = etree.fromstring(content, parser=parser)
            else:
                root = etree.fromstring(content)

            if root is None:
                raise InvalidDatasetError("Could not parse KML content.")

            features: List[Dict[str, Any]] = []
            feature_index = 0

            # Iterate all Placemark elements regardless of XML namespace
            for elem in root.iter():
                tag_name = _get_tag_name(elem)
                if tag_name == "placemark":
                    parsed_features = self._parse_placemark(elem, feature_index)
                    for pf in parsed_features:
                        features.append(pf)
                        feature_index += 1

            if not features:
                logger.warning("No Placemark features found in KML file: %s", kml_path.name)

            return features

        except InvalidDatasetError:
            raise
        except Exception as e:
            logger.error("Error parsing KML %s: %s", kml_path.name, str(e))
            raise InvalidDatasetError(f"Failed to parse KML dataset: {str(e)}")

    def _parse_placemark(self, placemark_elem: Any, start_index: int) -> List[Dict[str, Any]]:
        """Extract properties and geometries from a Placemark element."""
        properties: Dict[str, Any] = {}
        geometries: List[Tuple[str, Any]] = []

        for child in placemark_elem:
            tag_lower = _get_tag_name(child)
            if not tag_lower:
                continue

            if tag_lower == "name" and child.text:
                properties["name"] = child.text.strip()
            elif tag_lower == "description" and child.text:
                properties["description"] = child.text.strip()
            elif tag_lower == "extendeddata":
                self._extract_extended_data(child, properties)
            elif tag_lower == "point":
                geom = self._parse_point(child)
                if geom:
                    geometries.append(geom)
            elif tag_lower == "linestring":
                geom = self._parse_linestring(child)
                if geom:
                    geometries.append(geom)
            elif tag_lower == "polygon":
                geom = self._parse_polygon(child)
                if geom:
                    geometries.append(geom)
            elif tag_lower == "multigeometry":
                multi_geoms = self._parse_multigeometry(child)
                geometries.extend(multi_geoms)

        results = []
        for i, (g_type, coords) in enumerate(geometries):
            results.append({
                "feature_index": start_index + i,
                "geometry_type": g_type,
                "coordinates": coords,
                "properties": properties.copy()
            })

        return results

    def _extract_extended_data(self, elem: Any, props: Dict[str, Any]) -> None:
        """Extract ExtendedData key-value pairs."""
        for child in elem:
            tag = _get_tag_name(child)
            if tag == "data":
                key = child.attrib.get("name")
                val_node = child.find("{*}value") if HAS_LXML else child.find("value")
                if val_node is None:
                    # search without namespace
                    for c in child:
                        if _get_tag_name(c) == "value":
                            val_node = c
                            break
                val = val_node.text.strip() if (val_node is not None and val_node.text) else ""
                if key:
                    props[key] = val

    def _parse_coords_string(self, text: Optional[str]) -> List[List[float]]:
        """Parse 'lon,lat,alt lon,lat,alt' coordinate string into [[lon, lat], ...]."""
        if not text:
            return []
        coords = []
        raw_tuples = re.split(r"[\s\n\r]+", text.strip())
        for raw in raw_tuples:
            if not raw:
                continue
            parts = raw.split(",")
            if len(parts) >= 2:
                try:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    coords.append([lon, lat])
                except ValueError:
                    continue
        return coords

    def _parse_point(self, elem: Any) -> Optional[Tuple[str, List[float]]]:
        for child in elem.iter():
            tag = _get_tag_name(child)
            if tag == "coordinates":
                pts = self._parse_coords_string(child.text)
                if pts:
                    return "Point", pts[0]
        return None

    def _parse_linestring(self, elem: Any) -> Optional[Tuple[str, List[List[float]]]]:
        for child in elem.iter():
            tag = _get_tag_name(child)
            if tag == "coordinates":
                pts = self._parse_coords_string(child.text)
                if pts:
                    return "LineString", pts
        return None

    def _parse_polygon(self, elem: Any) -> Optional[Tuple[str, List[List[List[float]]]]]:
        exterior_ring = []
        interior_rings = []

        for child in elem:
            tag = _get_tag_name(child)
            if tag == "outerboundaryis":
                for ring_child in child.iter():
                    if _get_tag_name(ring_child) == "coordinates":
                        exterior_ring = self._parse_coords_string(ring_child.text)
            elif tag == "innerboundaryis":
                for ring_child in child.iter():
                    if _get_tag_name(ring_child) == "coordinates":
                        hole = self._parse_coords_string(ring_child.text)
                        if hole:
                            interior_rings.append(hole)

        if not exterior_ring:
            # Check if coordinates tag exists directly inside
            for child in elem.iter():
                if _get_tag_name(child) == "coordinates":
                    exterior_ring = self._parse_coords_string(child.text)
                    break

        if exterior_ring:
            rings = [exterior_ring] + interior_rings
            return "Polygon", rings
        return None

    def _parse_multigeometry(self, elem: Any) -> List[Tuple[str, Any]]:
        geoms = []
        for child in elem:
            tag = _get_tag_name(child)
            if tag == "point":
                g = self._parse_point(child)
                if g:
                    geoms.append(g)
            elif tag == "linestring":
                g = self._parse_linestring(child)
                if g:
                    geoms.append(g)
            elif tag == "polygon":
                g = self._parse_polygon(child)
                if g:
                    geoms.append(g)
        return geoms
