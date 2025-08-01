from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class SessionValidationResult(BaseModel):
    """
    Resultado de validar si una sesión puede finalizarse
    """

    can_finish: bool = Field(description="Si la sesión puede finalizarse")
    reason: str = Field(description="Razón por la cual puede o no finalizarse")
    missing_requirements: List[str] = Field(
        default=[], description="Requerimientos faltantes"
    )
    exercises_count: Optional[int] = Field(
        None, description="Número total de ejercicios"
    )
    exercises_with_images: Optional[int] = Field(
        None, description="Ejercicios con imágenes"
    )
    exercises_needing_analysis: Optional[List[str]] = Field(
        None, description="IDs de ejercicios que necesitan análisis"
    )


class SessionFinalizationResult(BaseModel):
    """✅ ACTUALIZADO: Resultado de finalización con puntuación"""

    # Campos existentes
    session_id: UUID
    finalized_successfully: bool
    total_exercises: int
    consolidated_exercises: int
    failed_exercises: int
    final_stats: Dict[str, Any]
    consolidation_warnings: List[str]
    finalization_timestamp: datetime
    evaluation_pending: bool
    has_assigned_instructor: bool
    message: str

    # ✅ NUEVOS campos de puntuación
    total_session_score: int = 0
    average_score_per_exercise: float = 0.0
    best_shot_score: int = 0
    score_efficiency: Optional[float] = None


# Esquemas para requests/responses de endpoints


class FinishSessionRequest(BaseModel):
    """
    Request para finalizar sesión (puede estar vacío si no necesitas parámetros adicionales)
    """

    force_finish: bool = Field(
        False, description="Forzar finalización aunque haya warnings menores"
    )


class FinishSessionResponse(BaseModel):
    """
    Respuesta al finalizar sesión
    """

    success: bool
    data: Optional[SessionFinalizationResult] = None
    error: Optional[str] = None


class SessionStatusResponse(BaseModel):
    """
    Respuesta del estado de una sesión
    """

    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None


class ReopenSessionRequest(BaseModel):
    """
    Request para reabrir una sesión finalizada
    """

    confirmation: bool = Field(description="Confirmación de que quiere reabrir")
    reason: Optional[str] = Field(None, description="Razón para reabrir")


class ReopenSessionResponse(BaseModel):
    """
    Respuesta al reabrir sesión
    """

    success: bool
    message: str
    session_id: UUID
    can_modify: bool


# Esquemas para validación de modificaciones


class SessionModificationCheck(BaseModel):
    """
    Verificación de si se puede modificar una sesión
    """

    session_id: UUID
    can_modify: bool = Field(description="Si la sesión puede modificarse")
    is_finished: bool = Field(description="Si la sesión está finalizada")
    reason: Optional[str] = Field(None, description="Razón si no se puede modificar")


# Esquemas para estadísticas de finalización


class FinalizationSummary(BaseModel):
    """
    Resumen de finalización para dashboards
    """

    sessions_finished_today: int
    average_exercises_per_session: float
    average_accuracy: float
    common_finalization_issues: List[str]
    total_shots_today: int
