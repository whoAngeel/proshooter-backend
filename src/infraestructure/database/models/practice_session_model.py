from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
import uuid
from datetime import datetime

class IndividualPracticeSessionModel(Base):
    __tablename__ = "individual_practice_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shooter_id = Column(UUID(as_uuid=True), ForeignKey("shooters.user_id"), nullable=False)
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.now())
    location = Column(String, nullable=False, default="Sin especificar")
    total_shots_fired = Column(Integer, default=0)
    total_hits = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shooter = relationship("ShooterModel", back_populates="practice_sessions")
    instructor = relationship("UserModel", foreign_keys=[instructor_id])

    def __repr__(self):
        return f"<IndividualPracticeSession(id={self.id}, shooter_id={self.shooter_id}, instructor_id={self.instructor_id}, date={self.date}, location={self.location}, total_shots_fired={self.total_shots_fired}, total_hits={self.total_hits}, accuracy_percentage={self.accuracy_percentage})>"


from ..models.user_model import UserModel
from ..models.shooter_model import ShooterModel
