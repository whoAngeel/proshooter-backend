import uuid
from datetime import datetime
from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base

class ShootingRecommendationModel(Base):
    __tablename__ = "shooting_recommendations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("target_analyses.id"), nullable=False)
    primary_issue_zone = Column(String, nullable=False)
    primary_issue_zone_description = Column(String, nullable=False)
    secondary_issue_zone = Column(String, nullable=True)
    secondary_issue_zone_description = Column(String, nullable=True)

    # posture_recommendation = Column(String, nullable=True)
    # grip_recommendation = Column(String, nullable=True)
    # sight_alignment_recommendation = Column(String, nullable=True)
    # trigger_control_recommendation = Column(String, nullable=True)
    # breathing_recommendation = Column(String, nullable=True)
    # follow_through_recommendation = Column(String, nullable=True)
    recommended_exercises = Column(JSON, nullable=True)
    recommendation_description = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    analysis = relationship("TargetAnalysisModel", back_populates="recommendation")

from .target_analysis_model import TargetAnalysisModel
