"""
Shapefile Parsing and Feature Extraction Service.
Parses Shapefile components (.shp, .shx, .dbf, .prj) from extracted directory.
Supports both Fiona/GeoPandas and high-performance pure-Python pyshp.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from app.core.logging import logger
from app.core.exceptions import InvalidDatasetError

try:
    import fiona
    HAS_FIONA = True
except Exception:
    HAS_FIONA = False

try:
    import shapefile
    HAS_SHAPEFILE = True
except Exception:
    HAS_SHAPEFILE = False


class ShapefileService:
    """Service to parse Shapefile datasets (.shp/.dbf/.prj) and extract standardized features."""

    def parse_shapefile(self, shp_path: Path) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Parse Shapefile and return:
        (features_list, prj_content)
        """
        if not shp_path.exists():
            raise InvalidDatasetError(f"Primary Shapefile (.shp) does not exist: {shp_path.name}")

        # Check for companion files
        base_path = shp_path.with_suffix("")
        dbf_path = base_path.with_suffix(".dbf")
        shx_path = base_path.with_suffix(".shx")
        prj_path = base_path.with_suffix(".prj")

        prj_content: Optional[str] = None
        if prj_path.exists():
            try:
                with open(prj_path, "r", encoding="utf-8", errors="ignore") as f:
                    prj_content = f.read().strip()
            except Exception as e:
                logger.warning("Could not read .prj file: %s", str(e))

        features: List[Dict[str, Any]] = []

        # 1. Attempt using Fiona if available
        if HAS_FIONA:
            try:
                with fiona.open(str(shp_path)) as src:
                    crs_wkt = src.crs_wkt if hasattr(src, "crs_wkt") else prj_content
                    for idx, feat in enumerate(src):
                        geom = feat.get("geometry")
                        if not geom:
                            continue
                        features.append({
                            "feature_index": idx,
                            "geometry_type": geom["type"],
                            "coordinates": geom["coordinates"],
                            "properties": dict(feat.get("properties", {}))
                        })
                return features, (crs_wkt or prj_content)
            except Exception as e:
                logger.debug("Fiona parsing encountered exception: %s. Using shapefile reader.", e)

        # 2. Pure-Python shapefile (pyshp) reader
        if HAS_SHAPEFILE:
            try:
                with shapefile.Reader(str(shp_path)) as sf:
                    fields = [f[0] for f in sf.fields[1:]]  # exclude DeletionFlag

                    for idx, shape_record in enumerate(sf.shapeRecords()):
                        geom_interface = shape_record.shape.__geo_interface__
                        g_type = geom_interface.get("type", "Unknown")
                        coords = geom_interface.get("coordinates", [])

                        # Properties from DBF record
                        raw_record = shape_record.record
                        props = {}
                        for f_idx, f_name in enumerate(fields):
                            val = raw_record[f_idx]
                            # Clean up dates, bytes or trailing spaces
                            if isinstance(val, bytes):
                                val = val.decode("utf-8", errors="ignore")
                            elif isinstance(val, str):
                                val = val.strip()
                            props[f_name] = val

                        features.append({
                            "feature_index": idx,
                            "geometry_type": g_type,
                            "coordinates": coords,
                            "properties": props
                        })

                return features, prj_content
            except Exception as e:
                logger.error("Error reading Shapefile with pyshp: %s", str(e))
                raise InvalidDatasetError(f"Failed to read Shapefile: {str(e)}")

        raise InvalidDatasetError("No Shapefile parsing driver available (Fiona or pyshp required).")
