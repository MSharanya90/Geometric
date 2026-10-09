"""
SQLAlchemy model for uploaded geospatial files.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String(36), primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(32), nullable=False)  # KML or SHAPEFILE_ZIP
    file_size = Column(Integer, nullable=False)
    source_crs = Column(String(64), nullable=True, default="EPSG:4326")
    measurement_crs = Column(String(64), nullable=True)
    crs_strategy = Column(String(255), nullable=True)
    feature_count = Column(Integer, default=0)
    geometry_types = Column(JSON, nullable=True)  # {"Polygon": 10, "Point": 5}
    status = Column(String(32), default="UPLOADED", index=True)
    processing_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    features = relationship(
        "Feature",
        back_populates="uploaded_file",
        cascade="all, delete-orphan",
        order_by="Feature.feature_index"
    )

    def __repr__(self) -> str:
        return f"<UploadedFile(id='{self.id}', filename='{self.original_filename}', status='{self.status}')>"
