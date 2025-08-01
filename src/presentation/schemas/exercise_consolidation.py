from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime


class AmmunitionValidationResult(BaseModel):
    """
    Resultado de la validación de consistencia de munición
    """

    allocated: int = Field(description="Munición asignada originalmente")
    currently_used: int = Field(description="Munición marcada como usada actualmente")
    detected_impacts: int = Field(description="Impactos detectados por IA")
    recommended_used: int = Field(description="Munición recomendada a usar")
    status: str = Field(description="Estado de la validación")
    warning: Optional[str] = Field(
        None, description="Advertencia si hay inconsistencias"
    )
    needs_manual_review: bool = Field(False, description="Requiere revisión manual")


class ExerciseMetricsUpdate(BaseModel):
    """
    Métricas actualizadas para un ejercicio
    """

    ammunition_used: int = Field(description="Munición efectivamente usada")
    hits: int = Field(description="Aciertos dentro del blanco")
    accuracy_percentage: float = Field(description="Porcentaje de precisión")
    reaction_time: Optional[float] = Field(None, description="Tiempo de reacción")
    total_impacts_detected: Optional[int] = Field(
        None, description="Total de impactos detectados"
    )
    impacts_outside_target: Optional[int] = Field(
        None, description="Impactos fuera del blanco"
    )
    total_score: int = 0
    average_score_per_shot: float = 0.0
    max_score_achieved: int = 0
    score_distribution: Optional[Dict[str, int]] = None
    group_diameter: Optional[float] = None


class ExerciseConsolidationResult(BaseModel):
    """Resultado actualizado de consolidación con puntuación"""

    # Campos existentes
    exercise_id: UUID
    updated_successfully: bool
    ammunition_used: int
    hits: int
    accuracy_percentage: float
    ammunition_validation: AmmunitionValidationResult
    total_impacts_detected: int
    message: str

    total_score: int = 0
    average_score_per_shot: float = 0.0
    max_score_achieved: int = 0
    score_efficiency: Optional[float] = None


class ExerciseConsolidationStatus(BaseModel):
    """
    Estado actual de consolidación de un ejercicio
    """

    exercise_id: UUID
    has_image: bool = Field(description="Si tiene imagen de blanco")
    has_analysis: bool = Field(description="Si tiene análisis de IA")
    ammunition_allocated: Optional[int] = Field(description="Munición asignada")
    ammunition_used: Optional[int] = Field(description="Munición usada registrada")
    hits: Optional[int] = Field(description="Aciertos registrados")
    accuracy_percentage: Optional[float] = Field(description="Precisión registrada")
    analysis_detected_impacts: Optional[int] = Field(
        description="Impactos detectados por IA"
    )
    needs_consolidation: bool = Field(description="Si necesita consolidación")
    last_analysis_date: Optional[datetime] = Field(
        description="Fecha del último análisis"
    )


class SessionConsolidationResult(BaseModel):
    """
    Resultado de consolidar todos los ejercicios de una sesión
    """

    session_id: UUID
    total_exercises: int = Field(description="Total de ejercicios en la sesión")
    consolidated_count: int = Field(description="Ejercicios consolidados exitosamente")
    failed_count: int = Field(description="Ejercicios que fallaron al consolidar")
    exercise_results: List[Dict] = Field(
        description="Resultados detallados por ejercicio"
    )
    session_totals: Optional[Dict] = Field(
        None, description="Totales actualizados de la sesión"
    )


# Esquemas para respuestas de endpoints


class ConsolidateExerciseRequest(BaseModel):
    """
    Request para consolidar un ejercicio específico
    """

    force_update: bool = Field(
        False, description="Forzar actualización aunque parezca actualizado"
    )


class ConsolidateExerciseResponse(BaseModel):
    """
    Respuesta al consolidar un ejercicio
    """

    success: bool
    data: Optional[ExerciseConsolidationResult] = None
    error: Optional[str] = None


class GetConsolidationStatusResponse(BaseModel):
    """
    Respuesta al consultar estado de consolidación
    """

    success: bool
    data: Optional[ExerciseConsolidationStatus] = None
    error: Optional[str] = None


class ConsolidateSessionRequest(BaseModel):
    """
    Request para consolidar toda una sesión
    """

    force_update_all: bool = Field(
        False, description="Forzar actualización de todos los ejercicios"
    )


class ConsolidateSessionResponse(BaseModel):
    """
    Respuesta al consolidar una sesión completa
    """

    success: bool
    data: Optional[SessionConsolidationResult] = None
    error: Optional[str] = None


# Esquemas para configuración


class ConsolidationConfig(BaseModel):
    """
    Configuración para el proceso de consolidación
    """

    max_ammunition_difference: int = Field(
        2, description="Diferencia máxima aceptable entre asignado/detectado"
    )
    auto_resolve_misses: bool = Field(
        True, description="Resolver automáticamente fallos aparentes"
    )
    require_manual_review_threshold: int = Field(
        3, description="Umbral para requerir revisión manual"
    )

    class Config:
        from_attributes = True


# Esquemas de validación adicionales


class AmmunitionConsistencyCheck(BaseModel):
    """
    Verificación de consistencia de munición
    """

    exercise_id: UUID
    allocated: int
    detected: int
    difference: int
    percentage_difference: float
    status: str  # CONSISTENT, MINOR_DIFFERENCE, MAJOR_DIFFERENCE
    recommended_action: str


class ConsolidationSummary(BaseModel):
    """
    Resumen de consolidación para dashboard
    """

    total_exercises_checked: int
    exercises_updated: int
    exercises_needing_review: int
    average_accuracy_change: float
    total_ammunition_adjusted: int
    common_issues: List[str]
