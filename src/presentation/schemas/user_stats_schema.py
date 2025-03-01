from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class ShooterStatsBase(BaseModel):
    total_shots: int = 0
    acuracy: int = 0
    average_hit_factor: float = 0
    accuracy: float = 0

class ShooterStatsCreate(ShooterStatsBase):
    pass

class ShooterStatsUpdate(ShooterStatsBase):
    shooter_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ShooterStatsRead(ShooterStatsBase):
    pass
