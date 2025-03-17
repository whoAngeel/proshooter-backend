from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime

from src.domain.enums.weapon_type_enum import WeaponTypeEnum

class WeaponBase(BaseModel):
    name: str = Field(..., description="Nombre de la arma")
    brand: str = Field(..., description="Marca de la arma")
    model: str = Field(..., description="Modelo de la arma")
    serial_number: str = Field(..., description="Número de serie de la arma")
    weapon_type: WeaponTypeEnum = Field(..., description="Tipo de arma")
    caliber: str = Field(..., description="Calibre del arma")
    description: Optional[str] = Field(None, description="Descripción detallada de la arma")

class WeaponCreate(WeaponBase):
    pass

class WeaponUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nombre de la arma", min_length=1)
    brand: Optional[str] = Field(None, description="Marca de la arma", min_length=1)
    model: Optional[str] = Field(None, description="Modelo de la arma", min_length=1)
    serial_number: Optional[str] = Field(None, description="Número de serie de la arma", min_length=1)
    weapon_type: Optional[WeaponTypeEnum] = None
    caliber: Optional[str] = Field(None, description="Calibre del arma", min_length=1)
    description: Optional[str] = Field(None, description="Descripción detallada de la arma")
    is_active: Optional[bool] = None

class WeaponRead(WeaponBase):
    id: UUID4
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
        }

class WeaponDetail(WeaponRead):

    # compatible_ammunition: Optional[List['AmmunitionRead']] = None
    model_config = {
        "from_attributes": True
    }
