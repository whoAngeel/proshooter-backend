from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator

from src.domain.enums.classification_enum import ShooterLevelEnum


class SessionInfo(BaseModel):
    id: UUID
    date: datetime
    location: str
    total_shots_fired: int
    accuracy_percentage: float

    model_config = {"from_attributes": True}


class ShooterInfo(BaseModel):
    user_id: UUID
    range: Optional[str] = None

    model_config = {"from_attributes": True}


class EvaluatorInfo(BaseModel):
    id: UUID
    model_config = {"from_attributes": True}


class PracticeEvaulationBase(BaseModel):
    session_id: UUID
    evaluator_id: Optional[UUID] = None
    final_score: float = Field(ge=0, le=100)
    # classification: Optional[ShooterLevelEnum] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recomendations: Optional[str] = None

    overall_technique_rating: Optional[float] = None
    instructor_notes: Optional[str] = None

    # zonas problematicas
    primary_issue_zone: Optional[str] = None
    secondary_issue_zone: Optional[str] = None

    # metricas de tiempo
    avg_reaction_time: Optional[float] = None
    avg_draw_time: Optional[float] = None
    avg_reload_time: Optional[float] = None

    # Metricas avanzadas
    hit_factor: Optional[float] = None


class PracticeEvaluationCreate(PracticeEvaulationBase):
    # TODO: cambiar esto
    @model_validator(mode="after")
    def validate_classification_based_on_score(self) -> "PracticeEvaluationCreate":
        # validamos que la clasificacion sea coherente con la puntuacion
        score = self.final_score
        classification = self.classification

        # reglas de clasificacion segun el documento
        if score >= 90 and classification != ShooterLevelEnum.EXPERTO:
            self.classification = ShooterLevelEnum.EXPERTO
        elif 70 <= score < 90 and classification != ShooterLevelEnum.CONFIABLE:
            self.classification = ShooterLevelEnum.CONFIABLE
        elif 40 <= score < 70 and classification != ShooterLevelEnum.MEDIO:
            self.classification = ShooterLevelEnum.MEDIO
        elif 10 <= score < 40 and classification != ShooterLevelEnum.REGULAR:
            self.classification = ShooterLevelEnum.REGULAR

        return self


class PracticeEvaluationUpdate(BaseModel):
    evaluator_id: Optional[UUID] = None
    final_score: Optional[float] = Field(None, ge=0, le=100)
    # classification: Optional[ShooterLevelEnum] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recomendations: Optional[str] = None

    # Calificaciones específicas
    overall_technique_rating: Optional[float] = None
    instructor_notes: Optional[str] = None

    # Zonas problemáticas
    primary_issue_zone: Optional[str] = None
    secondary_issue_zone: Optional[str] = None

    # Métricas de tiempo
    avg_reaction_time: Optional[float] = None
    avg_draw_time: Optional[float] = None
    avg_reload_time: Optional[float] = None

    # Métricas avanzadas
    hit_factor: Optional[float] = None

    @model_validator(mode="after")
    def validate_classification_based_on_score(self) -> "PracticeEvaluationUpdate":
        # Solo validamos si ambos campos se proporcionan
        if self.final_score is not None and self.classification is not None:
            score = self.final_score

            # Reglas de clasificación según el documento
            if score >= 90 and self.classification != ShooterLevelEnum.EXPERT:
                self.classification = ShooterLevelEnum.EXPERT
            elif (
                70 <= score < 90 and self.classification != ShooterLevelEnum.TRUSTWORTHY
            ):
                self.classification = ShooterLevelEnum.TRUSTWORTHY
            elif 40 <= score < 70 and self.classification != ShooterLevelEnum.MEDIUM:
                self.classification = ShooterLevelEnum.MEDIUM
            elif 10 <= score < 40 and self.classification != ShooterLevelEnum.REGULAR:
                self.classification = ShooterLevelEnum.REGULAR

        return self


class PracticeEvaluationRead(PracticeEvaulationBase):
    id: UUID
    date: datetime
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PracticeEvaluationDetail(PracticeEvaluationRead):
    session: Optional[SessionInfo] = None
    evaluator: Optional[EvaluatorInfo] = None

    model_config = {"from_attributes": True}


class PracticeEvaluationList(BaseModel):
    items: List[PracticeEvaluationRead]
    total: int
    page: int
    size: int
    pages: int


class ShooterEvaluationStatistics(BaseModel):
    shooter_id: UUID
    total_evaluations: int
    average_score: float
    classification_distribution: Dict[str, int]
    recent_trend: str  # "improving", "declining", "stable", "insufficient_data"
    average_ratings: Dict[str, Optional[float]]
    common_issue_zones: Dict[str, float]
    classification_change_recommended: bool
    suggested_classification: Optional[ShooterLevelEnum] = None
    latest_evaluations: List[PracticeEvaluationRead] = []


class PracticeEvaluationFilter(BaseModel):
    session_id: Optional[UUID] = None
    shooter_id: Optional[UUID] = None
    evaluator_id: Optional[UUID] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    classification: Optional[ShooterLevelEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100


class RatingAnalysis(BaseModel):
    category: str  # "posture", "grip", etc.
    average: float
    trend: str  # "improving", "declining", "stable"
    suggested_improvements: Optional[str] = None
