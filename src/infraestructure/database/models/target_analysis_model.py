from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column,
    UUID,
    DateTime,
    func,
    ForeignKey,
    Integer,
    String,
    JSON,
    Float,
)
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base


class TargetAnalysisModel(Base):
    __tablename__ = "target_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    target_image_id = Column(
        UUID(as_uuid=True), ForeignKey("target_images.id"), nullable=False
    )
    analysis_timestamp = Column(DateTime, default=datetime.now)

    # Estadísticas de impactos detectados (AGREGAR ESTAS COLUMNAS)
    total_impacts_detected = Column(Integer, default=0)
    fresh_impacts_inside = Column(Integer, default=0)
    fresh_impacts_outside = Column(Integer, default=0)
    covered_impacts_inside = Column(Integer, default=0)
    covered_impacts_outside = Column(Integer, default=0)

    # Métricas calculadas (AGREGAR ESTAS COLUMNAS)
    accuracy_percentage = Column(Float, default=0.0)
    average_confidence = Column(Float, default=0.0)

    # Datos detallados en JSON
    impact_coordinates = Column(JSON, nullable=True)
    zone_distribution = Column(JSON, nullable=True)  # Si lo usas
    confidence_stats = Column(JSON, nullable=True)

    # Metadata del análisis (AGREGAR ESTAS COLUMNAS)
    analysis_method = Column(String, nullable=False, default="YOLO_v8")
    model_version = Column(String, nullable=True, default="1.0")
    confidence_threshold = Column(Float, default=0.25)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    target_image = relationship("TargetImageModel", back_populates="analyses")
    recommendation = relationship(
        "ShootingRecommendationModel",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


from .target_image_model import TargetImageModel
from .shooting_recommendation_model import ShootingRecommendationModel
