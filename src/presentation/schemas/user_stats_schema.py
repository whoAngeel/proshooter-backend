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
    trend_accuracy: float = 0.0
    last_10_sessions_avg: float = 0.0
    precision_exercise_accuracy: float = 0.0
    reaction_exercise_accuracy: float = 0.0
    movement_exercise_accuracy: float = 0.0
    # --- Nuevos campos de puntuación ---
    average_score: float = 0.0
    best_score_session: int = 0
    best_shot_ever: int = 0
    score_trend: float = 0.0
    precision_exercise_avg_score: float = 0.0
    reaction_exercise_avg_score: float = 0.0
    movement_exercise_avg_score: float = 0.0


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
