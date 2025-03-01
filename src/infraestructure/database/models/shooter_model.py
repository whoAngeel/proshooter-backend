from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Enum, String
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from src.domain.enums.classification_enum import ShooterClassification

class ShooterModel(Base):
    __tablename__ = "shooters"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    classification = Column(String, nullable=False, default="TR")
    range = Column(String)


    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("UserModel", back_populates="shooter")
    stats = relationship("ShooterStatsModel", back_populates="shooter", uselist=False, cascade="all, delete-orphan")

from src.infraestructure.database.models.user_model import UserModel
from src.infraestructure.database.models.shooter_stats_model import ShooterStatsModel
