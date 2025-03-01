from pydantic import BaseModel
from typing import Optional
from uuid import UUID
# from .user_schemas import UserRead
from src.infraestructure.database.models.shooter_model import ShooterClassification

class ShooterBase(BaseModel):
    classification: str = "TR"

class ShooterRead(ShooterBase):
    user_id: UUID
    user: Optional["UserReadLite"] = None  # 🔥 Relación con usuario
    stats: Optional["ShooterStatsRead"] = None

    class Config:
        from_attributes = True

class ShooterCreate(ShooterBase):
    pass

class ShooterUpdate(ShooterBase):
    pass

from src.presentation.schemas.user_schemas import UserReadLite
from src.presentation.schemas.user_stats_schema import ShooterStatsRead
ShooterRead.model_rebuild()
