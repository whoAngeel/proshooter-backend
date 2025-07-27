# schemas/instructor_dashboard_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class AssignedSessionSummary(BaseModel):
    """
    Resumen de sesión asignada para listado en dashboard
    """

    session_id: UUID
    shooter_id: UUID
    shooter_name: str
    date: datetime
    location: str
    total_shots: int
    total_hits: int
    accuracy_percentage: float
    exercises_count: int
    evaluation_pending: bool
    days_pending: int = Field(description="Días desde la sesión")
    evaluation_id: Optional[str]
    evaluation_score: Optional[float]
    evaluation_date: Optional[datetime]


class ExerciseForEvaluation(BaseModel):
    """
    Detalles de ejercicio para evaluación
    """

    exercise_id: UUID
    exercise_type: str
    distance: str
    ammunition_allocated: int
    ammunition_used: int
    hits: int
    accuracy_percentage: float
    reaction_time: Optional[float] = None
    has_target_image: bool
    target_image_path: Optional[str] = None
    analysis_data: Optional[Dict] = None


class ShooterInfoForEvaluation(BaseModel):
    """
    Información del tirador para contexto de evaluación
    """

    name: str
    email: str
    level: str
    nickname: Optional[str] = None
    recent_average_accuracy: float = Field(description="Promedio reciente de precisión")
    total_sessions_finished: int = Field(description="Total de sesiones finalizadas")


class SessionForEvaluationDetails(BaseModel):
    """
    Detalles completos de sesión para evaluación
    """

    session_id: UUID
    shooter_info: Dict
    date: datetime
    location: str
    total_shots_fired: int
    total_hits: int
    accuracy_percentage: float
    exercises: List[Dict]
    evaluation_pending: bool
    can_evaluate: bool


class InstructorDashboardStats(BaseModel):
    """
    Estadísticas para dashboard del instructor
    """

    pending_evaluations: int = Field(description="Evaluaciones pendientes")
    evaluated_this_month: int = Field(description="Evaluadas este mes")
    urgent_evaluations: int = Field(description="Evaluaciones urgentes (>7 días)")
    average_session_accuracy: float = Field(
        description="Precisión promedio de sesiones"
    )
    total_assigned_sessions: int = Field(description="Total de sesiones asignadas")


# Esquemas para requests/responses de endpoints


class InstructorDashboardResponse(BaseModel):
    """
    Respuesta completa del dashboard
    """

    success: bool
    stats: Optional[InstructorDashboardStats] = None
    recent_sessions: List[AssignedSessionSummary] = Field(default=[])
    urgent_sessions: List[AssignedSessionSummary] = Field(default=[])
    error: Optional[str] = None


class AssignedSessionsResponse(BaseModel):
    """
    Respuesta para lista de sesiones asignadas
    """

    success: bool
    sessions: List[AssignedSessionSummary] = Field(default=[])
    total_count: int = Field(default=0)
    pending_count: int = Field(default=0)
    evaluated_count: int = Field(default=0)

    error: Optional[str] = None


class SessionDetailsResponse(BaseModel):
    """
    Respuesta para detalles de sesión
    """

    success: bool
    session_details: Optional[SessionForEvaluationDetails] = None
    error: Optional[str] = None


# Esquemas para filtros y búsquedas


class SessionSearchFilters(BaseModel):
    """
    Filtros para búsqueda de sesiones
    """

    evaluation_status: Optional[str] = Field(
        None, description="pending, evaluated, all"
    )
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    min_accuracy: Optional[float] = None
    shooter_name: Optional[str] = None


class SessionSearchRequest(BaseModel):
    """
    Request para búsqueda de sesiones
    """

    filters: SessionSearchFilters = Field(default=SessionSearchFilters())
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0)


# Esquemas para acciones rápidas


class QuickActionRequest(BaseModel):
    """
    Request para acciones rápidas desde dashboard
    """

    session_ids: List[UUID] = Field(description="IDs de sesiones")
    action: str = Field(description="mark_urgent, add_note, etc.")
    params: Dict[str, Any] = Field(default={})


class BulkActionResponse(BaseModel):
    """
    Respuesta a acciones en lote
    """

    success: bool
    processed_count: int
    failed_count: int
    failed_sessions: List[UUID] = Field(default=[])
    message: str
