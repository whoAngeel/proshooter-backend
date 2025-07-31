from sqlalchemy import (
    Column,
    UUID,
    DateTime,
    func,
    ForeignKey,
    Integer,
    String,
    Float,
    Boolean,
)
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
import uuid
from datetime import datetime


class IndividualPracticeSessionModel(Base):
    __tablename__ = "individual_practice_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shooter_id = Column(
        UUID(as_uuid=True), ForeignKey("shooters.user_id"), nullable=False
    )
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.now())
    location = Column(String, nullable=False, default="Not specified")
    total_shots_fired = Column(Integer, default=0)
    total_hits = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)

    evaluation_pending = Column(Boolean, default=True)
    is_finished = Column(Boolean, default=False)

    total_session_score = Column(Integer, default=0, nullable=False)
    average_score_per_exercise = Column(Float, default=0.0, nullable=False)
    average_score_per_shot = Column(Float, default=0.0, nullable=False)
    best_shot_score = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shooter = relationship("ShooterModel", back_populates="practice_sessions")
    instructor = relationship("UserModel", foreign_keys=[instructor_id])
    exercises = relationship(
        "PracticeExerciseModel", back_populates="session", cascade="all, delete-orphan"
    )
    evaluation = relationship(
        "PracticeEvaluationModel",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def has_scoring_data(self) -> bool:
        """Indica si esta sesión tiene datos de puntuación"""
        return self.total_session_score > 0

    @property
    def session_score_efficiency(self) -> float:
        """Eficiencia de puntuación de la sesión"""
        if self.total_shots_fired == 0:
            return 0.0
        max_possible = self.total_shots_fired * 10
        return (
            (self.total_session_score / max_possible) * 100 if max_possible > 0 else 0.0
        )

    def __repr__(self):
        return f"<IndividualPracticeSession(id={self.id}, shooter_id={self.shooter_id}, instructor_id={self.instructor_id}, date={self.date}, location={self.location}, total_shots_fired={self.total_shots_fired}, total_hits={self.total_hits}, accuracy_percentage={self.accuracy_percentage})>"


from ..models.user_model import UserModel
from ..models.shooter_model import ShooterModel
from ..models.practice_exercise_model import PracticeExerciseModel
from ..models.evaluation_model import PracticeEvaluationModel
