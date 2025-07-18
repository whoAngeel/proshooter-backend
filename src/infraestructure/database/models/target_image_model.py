import uuid
from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Integer, Float, String
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infraestructure.database.session import Base


class TargetImageModel(Base):
    __tablename__ = "target_images"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación uno a uno con PracticeExerciseModel
    exercise = relationship(
        "PracticeExerciseModel", back_populates="target_image", uselist=False
    )
    analyses = relationship(
        "TargetAnalysisModel",
        back_populates="target_image",
        cascade="all, delete-orphan",
    )


from .practice_exercise_model import PracticeExerciseModel
from .target_analysis_model import TargetAnalysisModel
