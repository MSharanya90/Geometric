"""
Repository for Feature database operations, filtering, aggregations, and GeoJSON queries.
"""
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from app.models.feature import Feature
from app.models.file import UploadedFile


class FeatureRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def bulk_create(self, features: List[Feature]) -> None:
        """Bulk insert feature records."""
        self.db.add_all(features)
        self.db.commit()

    def get_by_file_id(
        self,
        file_id: str,
        page: int = 1,
        page_size: int = 50,
        geometry_type: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        min_length: Optional[float] = None,
        max_length: Optional[float] = None,
        search_query: Optional[str] = None,
    ) -> Tuple[List[Feature], int]:
        """
        Query features with filtering, pagination, and sorting.
        Returns (features_list, total_count).
        """
        query = self.db.query(Feature).filter(Feature.uploaded_file_id == file_id)

        if geometry_type:
            query = query.filter(Feature.geometry_type.ilike(f"%{geometry_type}%"))

        if min_area is not None:
            query = query.filter(Feature.area_m2 >= min_area)
        if max_area is not None:
            query = query.filter(Feature.area_m2 <= max_area)

        if min_length is not None:
            query = query.filter(Feature.length_m >= min_length)
        if max_length is not None:
            query = query.filter(Feature.length_m <= max_length)

        total_count = query.count()

        # Sorting
        order_fn = desc if order.lower() == "desc" else asc
        if sort_by == "area":
            query = query.order_by(order_fn(Feature.area_m2))
        elif sort_by == "length":
            query = query.order_by(order_fn(Feature.length_m))
        elif sort_by == "geometry_type":
            query = query.order_by(order_fn(Feature.geometry_type))
        else:
            query = query.order_by(order_fn(Feature.feature_index))

        offset = (page - 1) * page_size
        results = query.offset(offset).limit(page_size).all()
        return results, total_count

    def get_all_by_file_id(self, file_id: str) -> List[Feature]:
        """Get all features for a file in index order."""
        return (
            self.db.query(Feature)
            .filter(Feature.uploaded_file_id == file_id)
            .order_by(Feature.feature_index.asc())
            .all()
        )

    def get_summary_stats(self, file_id: str) -> Dict[str, Any]:
        """
        Compute aggregate summary statistics for a file:
        - total features
        - polygon count & total area
        - line count & total length
        - point count
        - min/max/avg area
        - min/max/avg line length
        - valid/invalid/repaired counts
        """
        features = self.get_all_by_file_id(file_id)
        total_features = len(features)

        number_of_polygons = 0
        number_of_lines = 0
        number_of_points = 0
        other_geometries = 0

        polygon_areas = []
        line_lengths = []

        invalid_count = 0
        repaired_count = 0
        valid_count = 0

        for f in features:
            g_type = f.geometry_type.lower()

            if not f.is_valid:
                invalid_count += 1
            else:
                valid_count += 1

            if f.was_repaired:
                repaired_count += 1

            if "polygon" in g_type:
                number_of_polygons += 1
                if f.area_m2 is not None:
                    polygon_areas.append(f.area_m2)
            elif "line" in g_type:
                number_of_lines += 1
                if f.length_m is not None:
                    line_lengths.append(f.length_m)
            elif "point" in g_type:
                number_of_points += 1
            else:
                other_geometries += 1

        total_area = sum(polygon_areas)
        total_length = sum(line_lengths)

        min_area = min(polygon_areas) if polygon_areas else None
        max_area = max(polygon_areas) if polygon_areas else None
        avg_area = (total_area / len(polygon_areas)) if polygon_areas else None

        min_len = min(line_lengths) if line_lengths else None
        max_len = max(line_lengths) if line_lengths else None
        avg_len = (total_length / len(line_lengths)) if line_lengths else None

        return {
            "total_features": total_features,
            "number_of_polygons": number_of_polygons,
            "number_of_lines": number_of_lines,
            "number_of_points": number_of_points,
            "other_geometries": other_geometries,
            "total_polygon_area_m2": total_area,
            "total_line_length_m": total_length,
            "min_area_m2": min_area,
            "max_area_m2": max_area,
            "avg_area_m2": avg_area,
            "min_line_length_m": min_len,
            "max_line_length_m": max_len,
            "avg_line_length_m": avg_len,
            "invalid_geometry_count": invalid_count,
            "repaired_geometry_count": repaired_count,
            "valid_geometry_count": valid_count,
        }
