from sqlalchemy import Column, UUID, DateTime, Enum, String, Text, Boolean, func, Float, JSON
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from src.domain.enums.target_enum import TargetType
from uuid import uuid4

class TargetModel(Base):

    __tablename__ = "targets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    target_type = Column(Enum(TargetType), nullable=False)

    description = Column(Text, nullable=True)
    scoring_zones = Column(JSON, nullable=True) # Configuracion de zonas de puntuacion
    dimensions = Column(String, nullable=True) # Dimensiones fisicas (ancho x alto)
    distance_recommended = Column(Float, nullable=True) # Distancia recomendada en metros

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relaciones
    #practice_sessions

    def __repr__(self):
        return f"Target(name={self.name}, target_type={self.target_type})"
