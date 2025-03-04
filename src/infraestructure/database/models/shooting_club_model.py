from sqlalchemy import Column, String, UUID, DateTime, func, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import uuid
from src.infraestructure.database.session import Base

class ShootingClubModel(Base):
    __tablename__ = "shooting_clubs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    chief_instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    #relationships
    chief_instructor = relationship("UserModel", foreign_keys=[
        chief_instructor_id
    ])

    members = relationship("ShooterModel", back_populates="club")
    # groups = relationship("ShootingGroupModel")

    def __repr__(self):
        """
        Return a string representation of the ShootingClub object, showing the id, name and chief instructor id.
        """
        return f"<ShootingClub(id={self.id}, name={self.name}, chief_instructor_id={self.chief_instructor_id})>"
