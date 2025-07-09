import uuid
from datetime import datetime
from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Integer, Float, Enum, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from src.infraestructure.database.session import Base
from src.domain.enums.classification_enum import ShooterLevelEnum

classification_enum = ENUM(
    ShooterLevelEnum,
    name= 'shooterlevelenum',
    create_type=False,
)
class PracticeEvaluationModel(Base):
    __tablename__ = "practice_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("individual_practice_sessions.id"), nullable=False)
    evaluator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # calificacion general
    final_score = Column(Float, nullable=False)
    classification = Column(classification_enum, nullable=False)

    # retroalimentacion cualitativa
    strengths = Column(String, nullable=True)
    weaknesses = Column(String, nullable=True)
    recomendations = Column(String, nullable=True)

    # calificaciones especificas (1-10)

    posture_rating = Column(Integer, nullable=True)
    grip_rating = Column(Integer, nullable=True)
    sight_alignment_rating = Column(Integer, nullable=True)
    trigger_control_rating = Column(Integer, nullable=True)
    breathing_rating = Column(Integer, nullable=True)

    # para analisis de errores
    primary_issue_zone = Column(String, nullable=True)
    secondary_issue_zone = Column(String, nullable=True)

    avg_reaction_time = Column(Float, nullable=True)
    avg_draw_time = Column(Float, nullable=True)
    avg_reload_time = Column(Float, nullable=True)

    # metricas avanzadas
    hit_factor = Column(Float, nullable=True) # puntos/tiempo (metrica usada en IPSC)

    date = Column(DateTime, nullable=False, default=datetime.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    session = relationship("IndividualPracticeSessionModel", back_populates="evaluation")
    evaluator = relationship("UserModel", foreign_keys=[evaluator_id])

    def __repr__(self):
        return f"Evaluation(id={self.id}, session_id={self.session_id}, evaluator_id={self.evaluator_id})"

from .practice_session_model import IndividualPracticeSessionModel
from .user_model import UserModel
