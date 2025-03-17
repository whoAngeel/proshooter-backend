# src/presentation/schemas/ammunition_schema.py
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime

from src.domain.enums.ammo_enum import AmmoType

class AmmunitionBase(BaseModel):
    name: str = Field(..., description="Nombre de la munición")
    brand: str = Field(..., description="Marca de la munición")
    caliber: str = Field(..., description="Calibre de la munición")
    ammo_type: AmmoType = Field(..., description="Tipo de munición")
    grain_weight: Optional[float] = Field(None, description="Peso en granos")
    velocity: Optional[float] = Field(None, description="Velocidad en pies por segundo")
    description: Optional[str] = Field(None, description="Descripción de la munición")
    price_per_round: Optional[float] = Field(None, description="Precio por unidad")

class AmmunitionCreate(AmmunitionBase):
    pass

class AmmunitionUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    caliber: Optional[str] = None
    ammo_type: Optional[AmmoType] = None
    grain_weight: Optional[float] = None
    velocity: Optional[float] = None
    description: Optional[str] = None
    price_per_round: Optional[float] = None
    is_active: Optional[bool] = None

class AmmunitionRead(AmmunitionBase):
    id: UUID4
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class AmmunitionDetail(AmmunitionRead):
    compatible_weapons: Optional[List["WeaponRead"]] = None

    model_config = {
        "from_attributes": True
    }

# Ahora hay que resolver la referencia circular
from src.presentation.schemas.weapon_schema import WeaponRead
AmmunitionDetail.model_rebuild()
