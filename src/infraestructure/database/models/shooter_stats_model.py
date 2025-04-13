from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Integer, Float, String, UniqueConstraint
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base

class ShooterStatsModel(Base):
    __tablename__ = "shooter_stats"
    shooter_id = Column(UUID(as_uuid=True), ForeignKey('shooters.user_id', ondelete="CASCADE"), primary_key=True)

    total_shots = Column(Integer, default=0, nullable=False)
    accuracy = Column(Integer, default=0, nullable=False) # Porcentaje de precision
    # average_score = Column(Integer, default=0, nullable=False)
    reaction_shots = Column(Integer, default=0, nullable=False)
    presicion_shots = Column(Integer, default=0, nullable=False)
    draw_time_avg = Column(Float, default=0, nullable=False)
    reload_time_avg = Column(Float, default=0, nullable=False)

    average_hit_factor = Column(Float, default=0, nullable=False)
    effectiveness = Column(Float, default=0, nullable=False)

    common_error_zones = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shooter = relationship("ShooterModel", back_populates="stats")


    def __repr__(self):
        return f"ShooterStats(shooter_id={self.shooter_id})"

from src.infraestructure.database.models.shooter_model import ShooterModel
