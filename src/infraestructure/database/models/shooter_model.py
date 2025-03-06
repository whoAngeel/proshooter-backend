from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Enum, String
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from src.domain.enums.classification_enum import ShooterClassification

class ShooterModel(Base):
    __tablename__ = "shooters"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    club_id = Column(UUID(as_uuid=True), ForeignKey("shooting_clubs.id"), nullable=True)
    classification = Column(String, nullable=False, default="TR")
    range = Column(String)


    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("UserModel", back_populates="shooter")
    stats = relationship("ShooterStatsModel", back_populates="shooter", uselist=False, cascade="all, delete-orphan")
    club = relationship("ShootingClubModel", back_populates="members")

    def __repr__(self):
        return f"Shooter(user_id={self.user_id}, club_id={self.club_id}, classification={self.classification}, range={self.range}, created_at={self.created_at}, updated_at={self.updated_at})"

from src.infraestructure.database.models.user_model import UserModel
from src.infraestructure.database.models.shooter_stats_model import ShooterStatsModel
from src.infraestructure.database.models.shooting_club_model import ShootingClubModel
