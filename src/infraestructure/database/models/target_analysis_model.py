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
    analysis_timestamp = Column(DateTime, default=datetime.now())

    # estadisticas de impactos detectados
    total_impacts_detected = Column(Integer, default=0)
    total_impacts_inside = Column(Integer, default=0)
    total_impacts_outside = Column(Integer, default=0)
    covered_impacts_inside = Column(Integer, default=0)
    covered_impacts_outside = Column(Integer, default=0)

    # metricas calculadas
    accuracy_percentage = Column(Float, default=0.0)  # solo impactos frescos
    average_confidence = Column(Float, default=0.0)

    # datos detallados en JSOn
    impact_coordinates = Column(JSON, nullable=True)
    zone_distribution = Column(JSON, nullable=True)
    confidence_stats = Column(JSON, nullable=True)

    # metadatos del analisis
    analysis_method = Column(String, nullable=False, default="YOLO_V8")  #
    model_version = Column(
        String, nullable=True, default="1.0.0"
    )  # Version del modelo utilizado
    confidence_threshold = Column(
        Float, default=0.25
    )  # Umbral de confianza para considerar un impacto como válido

    # total_impacts_detected = Column(Integer, default=0)
    # zone_distribution = Column(JSON, nullable=True)
    # impact_coordinates = Column(JSON, nullable=True)
    # analysis_confidence = Column(Float, default=0.0)
    # analysis_method = Column(String, nullable=False)

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
