from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class ShooterStatsBase(BaseModel):
    total_shots: int = 0
    accuracy: int = 0
    reaction_shots: int = 0
    presicion_shots: int = 0
    draw_time_avg: float = 0
    reload_time_avg: float = 0
    average_hit_factor: float = 0
    effectiveness: float = 0
    common_error_zones: Optional[str]




class ShooterStatsCreate(ShooterStatsBase):
    pass

class ShooterStatsUpdate(ShooterStatsBase):
    shooter_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ShooterStatsRead(ShooterStatsBase):

    class Config:
        from_attributes = True
