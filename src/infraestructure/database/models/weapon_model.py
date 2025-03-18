from sqlalchemy import Column, UUID, DateTime, Enum, String, Text, Boolean, func
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from src.domain.enums.weapon_type_enum import WeaponTypeEnum
from uuid import uuid4

class WeaponModel(Base):
    '''
    Modelo que representa un arma en el sistema

    Las armas son utilizadas por los tiradores en sus sesiones de práctica y pueden
    ser compatibles con diferentes tipos de municiones.
    '''
    __tablename__ = "weapons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    serial_number = Column(String, nullable=False, unique=True)

    weapon_type = Column(Enum(WeaponTypeEnum), nullable=False)
    caliber = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relaciones

    compatible_ammunition = relationship(
        "AmmunitionModel",
        secondary="weapon_ammunition_compatibility",
        back_populates="compatible_weapons"
    )
    # practice sessions

    def __repr__(self):
        return f"Weapon(name={self.name}, brand={self.brand}, model={self.model}, serial_number={self.serial_number})"

from src.infraestructure.database.models.ammunition_model import AmmunitionModel
