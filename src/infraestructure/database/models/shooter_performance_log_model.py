from sqlalchemy import Column, UUID, DateTime, String, Text, Boolean, func, ForeignKey
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from uuid import uuid4

class ShooterPerformanceLogModel(Base):
    __tablename__ = "shooter_performance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    shooter_id = Column(UUID(as_uuid=True), ForeignKey('shooters.user_id', ondelete="CASCADE"), nullable=False)

    metric_type = Column(String, nullable=True)
    metric_value = Column(String, nullable=True)
    context = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relacion con el tirador
    shooter = relationship("ShooterModel", back_populates="performance_logs")

    def __repr__(self):
        return f"Shooter Performance Record = {self.id}, shooter_id={self.shooter_id}"

from src.infraestructure.database.models.shooter_model import ShooterModel
