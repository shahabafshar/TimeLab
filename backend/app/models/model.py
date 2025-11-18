"""
Model and ModelMetrics models
"""
from sqlalchemy import Column, String, DateTime, Float, JSON, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class Model(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., "SARIMAX"
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    parameters = Column(JSON, nullable=False)  # Model parameters (p, d, q, etc.)
    model_data = Column(Text, nullable=True)  # Serialized model (pickle as base64)
    summary = Column(Text, nullable=True)  # Model summary text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", backref="models")
    metrics = relationship("ModelMetrics", back_populates="model", uselist=False)


class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    rmse = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    aic = Column(Float, nullable=True)
    bic = Column(Float, nullable=True)
    hqic = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    model = relationship("Model", back_populates="metrics")

