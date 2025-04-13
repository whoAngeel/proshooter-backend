from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Integer, Float, String
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from uuid import uuid4

class PracticeExerciseModel(Base):
    __tablename__ = "practice_exercises"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("individual_practice_sessions.id"), nullable=False)

    exercise_type_id = Column(UUID(as_uuid=True), ForeignKey("exercise_types.id"), nullable=False)
    target_id = Column(UUID(as_uuid=True), ForeignKey("targets.id"), nullable=False)
    weapon_id = Column(UUID(as_uuid=True), ForeignKey("weapons.id"), nullable=False)
    ammunition_id = Column(UUID(as_uuid=True), ForeignKey("ammunition.id"), nullable=False)

    distance = Column(String, nullable=False) # metros
    firing_cadence = Column(String, nullable=True)
    time_limit = Column(String, nullable=True)
    ammunition_allocated = Column(Integer, default=0)
    ammunition_used = Column(Integer, default=0)
    hits = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    reaction_time = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session = relationship("IndividualPracticeSessionModel", back_populates="exercises")
    exercise_type = relationship("ExerciseTypeModel", back_populates="exercises")
    target = relationship("TargetModel", back_populates="exercises")
    weapon = relationship("WeaponModel", back_populates="exercises")
    ammunition = relationship("AmmunitionModel", back_populates="exercises")
    target_images = relationship("TargetImageModel", back_populates="exercise", cascade="all, delete-orphan")

from ..models.exercise_type_model import ExerciseTypeModel
from ..models.practice_session_model import IndividualPracticeSessionModel
from .target_model import TargetModel
from .weapon_model import WeaponModel
from .ammunition_model import AmmunitionModel
