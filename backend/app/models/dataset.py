"""
Dataset model
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    columns = Column(JSON, nullable=False)  # List of column names
    row_count = Column(Integer, nullable=False)
    file_path = Column(String, nullable=True)  # Path to stored file
    meta_data = Column(JSON, nullable=True)  # Additional metadata (renamed from 'metadata' - reserved by SQLAlchemy)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

