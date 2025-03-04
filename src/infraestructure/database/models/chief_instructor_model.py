from sqlalchemy import Column, UUID, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base

class HeadInstructorModel(Base):
    __tablename__ = "head_instructors"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("UserModel", back_populates="head_instructor")
    # club = relationship("ClubModel", back_populates="head_instructor", uselist=False)  # Un jefe tiene un solo club
