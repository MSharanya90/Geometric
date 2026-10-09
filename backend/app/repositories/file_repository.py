"""
Repository for UploadedFile database operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.file import UploadedFile


class FileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, uploaded_file: UploadedFile) -> UploadedFile:
        self.db.add(uploaded_file)
        self.db.commit()
        self.db.refresh(uploaded_file)
        return uploaded_file

    def get_by_id(self, file_id: str) -> Optional[UploadedFile]:
        return self.db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

    def list_all(self, limit: int = 100, offset: int = 0) -> List[UploadedFile]:
        return (
            self.db.query(UploadedFile)
            .order_by(UploadedFile.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update(self, uploaded_file: UploadedFile) -> UploadedFile:
        self.db.commit()
        self.db.refresh(uploaded_file)
        return uploaded_file

    def delete(self, file_id: str) -> bool:
        obj = self.get_by_id(file_id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
