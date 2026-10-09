"""
SQLAlchemy model for individual extracted geospatial features.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    uploaded_file_id = Column(String(36), ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_index = Column(Integer, nullable=False, index=True)
    geometry_type = Column(String(64), nullable=False, index=True)
    geometry = Column(JSON, nullable=False)  # GeoJSON geometry dict {type: ..., coordinates: ...}
    bbox = Column(JSON, nullable=True)  # [min_x, min_y, max_x, max_y]
    properties = Column(JSON, nullable=True, default=dict)
    is_valid = Column(Boolean, default=True)
    was_repaired = Column(Boolean, default=False)
    measurement_status = Column(String(32), default="SUCCESS")  # SUCCESS, WARNING, SKIPPED, FAILED
    area_m2 = Column(Float, nullable=True, index=True)
    length_m = Column(Float, nullable=True, index=True)
    sub_measurements = Column(JSON, nullable=True)  # e.g. individual polygon areas or line lengths
    warnings = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    uploaded_file = relationship("UploadedFile", back_populates="features")

    def __repr__(self) -> str:
        return f"<Feature(id={self.id}, file_id='{self.uploaded_file_id}', index={self.feature_index}, type='{self.geometry_type}')>"
