from pydantic import BaseModel
from typing import Optional
from uuid import UUID
# from .user_schemas import UserRead
# from src.infraestructure.database.models.shooter_model import ShooterClassification, ShooterLevelEnum
from src.domain.enums.classification_enum import ShooterLevelEnum

class ShooterBase(BaseModel):
    level: ShooterLevelEnum = ShooterLevelEnum.REGULAR

class ShooterRead(ShooterBase):
    user_id: UUID
    user: Optional["UserReadLiteNoPersonalData"] = None  # 🔥 Relación con usuario
    stats: Optional["ShooterStatsRead"] = None

    class Config:
        from_attributes = True
class ShooterReadLite(ShooterBase):
    user_id: UUID

    user: Optional["UserReadLite"] = None
    stats: Optional["ShooterStatsRead"] = None



class ShooterCreate(ShooterBase):
    pass

class ShooterUpdate(ShooterBase):
    pass

from src.presentation.schemas.user_schemas import UserReadLite, UserReadLiteNoPersonalData
from src.presentation.schemas.user_stats_schema import ShooterStatsRead
ShooterRead.model_rebuild()
