from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Integer, Float, String
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from uuid import uuid4

class PracticeExerciseModel(Base):
    __tablename__ = "practice_exercises"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    shooter_id = Column(UUID(as_uuid=True), ForeignKey("shooters.user_id"), nullable=False)
