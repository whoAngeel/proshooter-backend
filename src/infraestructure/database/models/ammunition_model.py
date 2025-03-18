from sqlalchemy import Column, UUID, DateTime, Enum, String, Text, Boolean, func, Float
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from src.domain.enums.ammo_enum import AmmoType
from uuid import uuid4

class AmmunitionModel(Base):
    '''
    Modelo que representa una munición en el sistema

    La municion es utilizaad en las sesiones de práctica de los tiradores
    y debe ser compatible con el arma seleccionada
    '''

    __tablename__ = "ammunition"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    caliber = Column(String, nullable=False)

    ammo_type = Column(Enum(AmmoType), nullable=False)
    grain_weight = Column(Float, nullable=True) # Peso en granos
    velocity = Column(Float, nullable=True) # Velocidad en pies por segundo

    description = Column(Text, nullable=True)
    price_per_round = Column(Float, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relaciones
    compatible_weapons = relationship(
        "WeaponModel",
        secondary="weapon_ammunition_compatibility",
        back_populates="compatible_ammunition"
    )

    # practice sessions


    def __repr__(self):
        return f"Ammunition(name={self.name}, brand={self.brand}, caliber={self.caliber})"

from src.infraestructure.database.models.weapon_model import WeaponModel
from src.infraestructure.database.models.weapon_ammunition_compatibility_model import WeaponAmmunitionCompatibilityModel
