from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
import uuid

class IndividualPracticeSessionModel(Base):
    __tablename__ = "individual_practice_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    shooter_id = Column()
