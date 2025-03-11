from pydantic import BaseModel, Field, UUID4, model_validator, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.domain.enums.target_enum import TargetType

class TargetBase(BaseModel):
    name: str = Field(..., title="Nombre del blanco", description="Nombre del blanco", min_length=3, max_length=100)
    target_type: TargetType = Field(..., description="Tipo de blanco (Concéntrico, IPSC, etc.)")
    description: Optional[str] = Field(None, description="Descripción detallada del blanco")
    scoring_zones: Optional[Dict[str, Any]] = Field(None, description="Configuración de zonas de puntuación")
    dimensions: Optional[str] = Field(None, description="Dimensiones físicas (ancho x alto)")
    distance_recommended: Optional[float] = Field(None, description="Distancia recomendada en metros")

class TargetCreate(TargetBase):
    @model_validator(mode="after")
    def validate_scoring_zones(self):
        if self.scoring_zones is None:
            return self

        if self.target_type == TargetType.CONCENTRIC:
            if "rings" not in self.scoring_zones:
                raise ValueError("MISSING_RINGS")
        elif self.target_type == TargetType.IPSC:
            if "zones" not in self.scoring_zones:
                raise ValueError("MISSING_ZONES")

        return self

class TargetUpdate(TargetBase):
    name: Optional[str] = None
    target_type: Optional[TargetType] = None
    description: Optional[str] = None
    scoring_zones: Optional[Dict[str, Any]] = None
    dimensions: Optional[str] = None
    distance_recommended: Optional[float] = None
    is_active: Optional[bool] = None

    @model_validator(mode='after')
    def validate_scoring_zones(self):
        if self.scoring_zones is None:
            return self

        if self.target_type is not None:
            if self.target_type == TargetType.CONCENTRIC:
                if "rings" not in self.scoring_zones:
                    raise ValueError("MISSING_RINGS")
            elif self.target_type == TargetType.IPSC:
                if "zones" not in self.scoring_zones:
                    raise ValueError("MISSING_ZONES")
        return self

class TargetRead(TargetBase):
    id: UUID4
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TargetDetail(TargetRead):
    pass

class TargetScoreInput(BaseModel):
    """Schema para el cálculo de puntuación en un blanco."""
    target_id: UUID4
    hit_coordinates: Dict[str, float] = Field(..., example={"x": 10.5, "y": 15.2})

    @field_validator('hit_coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if 'x' not in v or 'y' not in v:
            raise ValueError("Las coordenadas deben incluir 'x' y 'y'")
        return v

class TargetScoreOutput(BaseModel):
    """Schema para el resultado del cálculo de puntuación."""
    target_id: UUID4
    target_name: str
    target_type: TargetType
    score: float
    hit_coordinates: Dict[str, float]
    zone_hit: Optional[str] = None  # Nombre de la zona impactada (si aplica)
