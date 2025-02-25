from sqlalchemy import Column, String, UUID, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from uuid import uuid4

class ShooterModel(Base):
    __tablename__ = "shooters"

    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("UserModel", back_populates="shooter")
