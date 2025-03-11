# src/domain/models/weapon_ammunition_compatibility_model.py
from sqlalchemy import Column, UUID, ForeignKey, DateTime, func
from src.infraestructure.database.session import Base
from uuid import uuid4

class WeaponAmmunitionCompatibilityModel(Base):
    """
    Modelo que representa la compatibilidad entre armas y municiones.

    Esta tabla de relación permite establecer qué municiones son
    compatibles con qué armas, facilitando la validación al crear prácticas.
    """
    __tablename__ = "weapon_ammunition_compatibility"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    weapon_id = Column(UUID(as_uuid=True), ForeignKey("weapons.id", ondelete="CASCADE"), nullable=False)
    ammunition_id = Column(UUID(as_uuid=True), ForeignKey("ammunition.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"WeaponAmmunitionCompatibility(weapon_id={self.weapon_id}, ammunition_id={self.ammunition_id})"
