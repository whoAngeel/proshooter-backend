from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from src.domain.enums.classification_enum import ShooterLevelEnum
from src.presentation.schemas.user_schemas import UserReadLite, UserReadLiteNoPersonalData
from src.presentation.schemas.user_stats_schema import ShooterStatsRead

class ShooterBase(BaseModel):
    level: ShooterLevelEnum = ShooterLevelEnum.REGULAR

class ShooterRead(ShooterBase):
    user_id: UUID
    user: Optional[UserReadLiteNoPersonalData] = None
    stats: Optional[ShooterStatsRead] = None

    model_config = {
        "from_attributes": True
    }

class ShooterReadLite(ShooterBase):
    user_id: UUID
    user: Optional[UserReadLite] = None
    stats: Optional[ShooterStatsRead] = None

    model_config = {
        "from_attributes": True
    }

class ShooterCreate(ShooterBase):
    pass

class ShooterUpdate(ShooterBase):
    pass

ShooterRead.model_rebuild()
