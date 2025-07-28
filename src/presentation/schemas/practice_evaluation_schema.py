from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class EvaluationCreateRequest(BaseModel):
    """
    Request para crear evaluación - Solo campos manuales del instructor
    """

    strengths: Optional[str] = Field(
        None, max_length=1000, description="Fortalezas observadas"
    )
    weaknesses: Optional[str] = Field(
        None, max_length=1000, description="Debilidades detectadas"
    )
    recomendations: Optional[str] = Field(
        None, max_length=1000, description="Recomendaciones de mejora"
    )

    overall_technique_rating: Optional[float] = Field(
        None, ge=0.0, le=10.0, description="Calificación técnica general (0-10)"
    )
    instructor_notes: Optional[str] = Field(
        None, max_length=2000, description="Notas adicionales del instructor"
    )

    # Zonas de problema (sugeridas automáticamente, editables por instructor)
    primary_issue_zone: Optional[str] = Field(
        None, max_length=100, description="Zona principal de problema"
    )
    secondary_issue_zone: Optional[str] = Field(
        None, max_length=100, description="Zona secundaria de problema"
    )

    @field_validator("overall_technique_rating")
    def validate_rating(cls, v):
        if v is not None and (v < 0.0 or v > 10.0):
            raise ValueError("Rating debe estar entre 0.0 y 10.0")
        return v


class EvaluationAutoCalculated(BaseModel):
    """
    Campos calculados automáticamente
    """

    final_score: float = Field(description="Puntuación final calculada")
    avg_reaction_time: Optional[float] = Field(
        None, description="Tiempo promedio de reacción"
    )
    avg_draw_time: Optional[float] = Field(
        None, description="Tiempo promedio de desenfunde"
    )
    hit_factor: Optional[float] = Field(
        None, description="Factor de impacto (hits/tiempo)"
    )


class EvaluationSuggestedZones(BaseModel):
    """
    Zonas de problema sugeridas por IA
    """

    primary: Optional[str] = Field(None, description="Zona principal sugerida")
    secondary: Optional[str] = Field(None, description="Zona secundaria sugerida")


class EvaluationFormData(BaseModel):
    """
    Datos completos para pre-llenar formulario de evaluación
    """

    session_id: UUID
    auto_calculated: EvaluationAutoCalculated
    suggested_zones: EvaluationSuggestedZones
    shooter_context: Dict[str, Any]
    classification_suggestion: str = Field(
        description="Clasificación sugerida (TR/TM/TC/TE)"
    )


class EvaluationResponse(BaseModel):
    """
    Respuesta completa de evaluación
    """

    id: UUID
    session_id: UUID
    evaluator_id: Optional[UUID]

    # Campos calculados
    final_score: float
    classification: str
    avg_reaction_time: Optional[float]
    avg_draw_time: Optional[float]
    hit_factor: Optional[float]

    # Campos del instructor
    strengths: Optional[str]
    weaknesses: Optional[str]
    recomendations: Optional[str]

    overall_technique_rating: Optional[float]
    instructor_notes: Optional[str]

    # Zonas de problema
    primary_issue_zone: Optional[str]
    secondary_issue_zone: Optional[str]

    date: datetime

    class Config:
        from_attributes = True


class EvaluationCreateResponse(BaseModel):
    """
    Respuesta al crear evaluación
    """

    success: bool
    evaluation_id: Optional[UUID] = None
    final_score: Optional[float] = None
    classification: Optional[str] = None
    message: str
    error: Optional[str] = None


class EvaluationFormResponse(BaseModel):
    """
    Respuesta para datos del formulario
    """

    success: bool
    form_data: Optional[EvaluationFormData] = None
    error: Optional[str] = None


# Esquemas para listados y consultas


class EvaluationSummary(BaseModel):
    """
    Resumen de evaluación para listados
    """

    id: UUID
    session_id: UUID
    shooter_name: str
    final_score: float
    classification: str
    date: datetime
    evaluator_name: Optional[str] = None


class ShooterEvaluationHistory(BaseModel):
    """
    Historial de evaluaciones de un tirador
    """

    shooter_id: UUID
    shooter_name: str
    evaluations: list[EvaluationSummary]
    total_evaluations: int
    latest_classification: Optional[str] = None
    average_score: Optional[float] = None


# Esquemas para análisis y estadísticas


class EvaluationTrend(BaseModel):
    """
    Tendencia de evaluaciones
    """

    trend: str = Field(description="improving, declining, stable, insufficient_data")
    scores: list[float]
    improving: Optional[bool] = None
    trend_value: Optional[float] = None


class ClassificationDistribution(BaseModel):
    """
    Distribución de clasificaciones
    """

    distributions: Dict[str, int] = Field(description="Conteo por clasificación")
    total_evaluations: int
    most_common: Optional[str] = None


class IssueZonesAnalysis(BaseModel):
    """
    Análisis de zonas problemáticas
    """

    zones_frequency: Dict[str, float] = Field(
        description="Frecuencia de zonas problema"
    )
    most_common_zones: list[str] = Field(description="Zonas más comunes")
    improvement_suggestions: list[str] = Field(
        description="Sugerencias basadas en patrones"
    )


# Esquemas de validación


class EvaluationEditRequest(BaseModel):
    """
    Request para editar evaluación existente
    """

    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recomendations: Optional[str] = None

    overall_technique_rating: Optional[float] = Field(None, ge=1.0, le=10.0)
    instructor_notes: Optional[str] = None
    primary_issue_zone: Optional[str] = None
    secondary_issue_zone: Optional[str] = None


class BulkEvaluationRequest(BaseModel):
    """
    Request para operaciones en lote (futuro)
    """

    session_ids: list[UUID]
    action: str = Field(description="export, delete, etc.")
    format: Optional[str] = Field("json", description="json, pdf, excel")
