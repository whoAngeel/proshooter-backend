# src/presentation/schemas/shooter_schema.py
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from src.domain.enums.classification_enum import ShooterLevelEnum
from src.presentation.schemas.user_schemas import (
    UserReadLite,
    UserReadLiteNoPersonalData,
)
from src.presentation.schemas.user_stats_schema import ShooterStatsRead


class ShooterBase(BaseModel):
    """Esquema base para los tiradores."""

    level: ShooterLevelEnum = ShooterLevelEnum.REGULAR
    range: Optional[str] = None
    club_id: Optional[UUID] = None


class ShooterCreate(ShooterBase):
    """Esquema para crear un nuevo tirador."""

    user_id: UUID


class ShooterUpdate(BaseModel):
    """Esquema para actualizar un tirador existente."""

    level: Optional[ShooterLevelEnum] = None
    range: Optional[str] = None
    club_id: Optional[UUID] = None


class ShooterRead(ShooterBase):
    """Esquema para leer información de un tirador."""

    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserReadLiteNoPersonalData] = None
    stats: Optional[ShooterStatsRead] = None

    model_config = {"from_attributes": True}


class ShooterReadLite(ShooterBase):
    """Esquema para leer información básica de un tirador."""

    user_id: UUID
    user: Optional[UserReadLite] = None

    model_config = {"from_attributes": True}


class ShooterDetail(ShooterRead):
    """Esquema detallado de un tirador con información adicional."""

    # Se incluye información completa de stats
    stats: Optional[ShooterStatsRead] = None
    # Se podría añadir información sobre sesiones recientes, evaluaciones, etc.
    session_count: Optional[int] = None
    evaluation_count: Optional[int] = None
    recent_progress: Optional[str] = None  # Improving, Stable, Declining
    club_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ShooterList(BaseModel):
    """Esquema para listar tiradores con paginación."""

    items: List[ShooterRead]
    total: int
    page: int
    size: int
    pages: int


class ShooterFilter(BaseModel):
    """Esquema para filtrar tiradores en consultas."""

    level: Optional[ShooterLevelEnum] = None
    club_id: Optional[UUID] = None
    search: Optional[str] = None
    min_accuracy: Optional[float] = None
    max_accuracy: Optional[float] = None
    skip: int = 0
    limit: int = 100


class ShooterClassificationHistory(BaseModel):
    """Esquema para el historial de clasificaciones de un tirador."""

    shooter_id: UUID
    classifications: List[
        Dict[str, Any]
    ]  # Lista de cambios de clasificación con fechas
    current_level: ShooterLevelEnum
    days_at_current_level: int
    progression_trend: str  # "ascending", "stable", "descending"


class ShooterPerformanceSummary(BaseModel):
    """Esquema para el resumen de rendimiento de un tirador."""

    shooter_id: UUID
    user_name: str
    level: ShooterLevelEnum
    total_sessions: int
    total_shots: int
    accuracy: float
    recent_trend: str  # "improving", "stable", "declining"
    strengths: List[str]
    weaknesses: List[str]
    recommended_exercises: List[str]
    recent_evaluations: List[Dict[str, Any]]


class ShooterComparisonResult(BaseModel):
    """Esquema para comparar el rendimiento de dos tiradores."""

    shooter1_id: UUID
    shooter1_name: str
    shooter1_level: ShooterLevelEnum
    shooter2_id: UUID
    shooter2_name: str
    shooter2_level: ShooterLevelEnum
    accuracy_difference: float
    reaction_time_difference: float
    strengths_comparison: Dict[str, Any]
    recommendation: str
