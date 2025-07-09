from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Integer, String, JSON, Float
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base

class TargetAnalysisModel(Base):
    __tablename__ = "target_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    target_image_id = Column(UUID(as_uuid=True), ForeignKey("target_images.id"), nullable=False)
    analysis_timestamp = Column(DateTime, default=datetime.now())
    total_impacts_detected = Column(Integer, default=0)
    zone_distribution = Column(JSON, nullable=True)
    impact_coordinates = Column(JSON, nullable=True)
    analysis_confidence = Column(Float, default=0.0)
    analysis_method = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # Relationships
    target_image = relationship("TargetImageModel", back_populates="analyses")
    recommendation = relationship("ShootingRecommendationModel", back_populates="analysis", cascade="all, delete-orphan")

from .target_image_model import TargetImageModel
from .shooting_recommendation_model import ShootingRecommendationModel
