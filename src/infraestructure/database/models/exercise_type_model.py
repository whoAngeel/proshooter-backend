from sqlalchemy import Column, UUID, DateTime, func, Integer, String, Boolean
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from uuid import uuid4

class ExerciseTypeModel(Base):
    __tablename__ = "exercise_types"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    difficulty = Column(Integer, nullable=False)
    objective = Column(String, nullable=True)
    development = Column(String, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # practice_exercise = relationship("PracticeExerciseModel", back_populates="exercise_type", cascade="all, delete-orphan")
    exercises = relationship("PracticeExerciseModel", back_populates="exercise_type", cascade="all, delete-orphan")


    def __repr__(self):
        return f"ExerciseType(id={self.id}, name={self.name}, description={self.description})"

from ..models.practice_exercise_model import PracticeExerciseModel
