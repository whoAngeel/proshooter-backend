from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator


class ExerciseTypeInfo(BaseModel):
    id: UUID = Field(..., description="ID of the exercise type")
    name: str = Field(..., description="Name of the exercise type")
    description: Optional[str] = Field(
        None, description="Description of the exercise type"
    )
    difficulty: int = Field(..., description="Difficulty level of the exercise type")
    objective: Optional[str] = Field(None, description="Objective of the exercise type")
    development: Optional[str] = Field(
        None, description="Development of the exercise type"
    )

    model_config = {"from_attributes": True}


class TargetInfo(BaseModel):
    id: UUID
    name: str
    target_type: str
    description: Optional[str] = None
    dimensions: Optional[str] = None
    distance_recommended: Optional[float] = None

    model_config = {"from_attributes": True}


class WeaponInfo(BaseModel):
    id: UUID
    name: str
    model: str
    serial_number: str
    weapon_type: str
    caliber: str

    model_config = {"from_attributes": True}


class AmmunitionInfo(BaseModel):
    id: UUID
    name: str
    caliber: str
    description: Optional[str] = None
    velocity: Optional[float] = None

    model_config = {"from_attributes": True}


class SessionInfo(BaseModel):
    id: UUID
    date: datetime
    location: str

    model_config = {"from_attributes": True}


class PracticeExerciseBase(BaseModel):
    session_id: UUID
    exercise_type_id: UUID
    target_id: UUID
    weapon_id: UUID
    ammunition_id: UUID
    distance: str
    firing_cadence: Optional[str] = None
    time_limit: Optional[str] = None
    ammunition_allocated: int = 0
    ammunition_used: int = 0
    hits: int = 0
    reaction_time: Optional[float] = None


class PracticeExerciseCreate(PracticeExerciseBase):
    @model_validator(mode="after")
    def validate_exercise_data(self) -> "PracticeExerciseCreate":
        if self.hits > self.ammunition_used:
            raise ValueError(
                "Los impactos no pueden ser mayores que la munición utilizada"
            )
        if self.ammunition_used > self.ammunition_allocated:
            raise ValueError(
                "La munición utilizada no puede ser mayor que la munición asignada"
            )
        return self


class PracticeExerciseUpdate(BaseModel):
    exercise_type_id: Optional[UUID] = None
    target_id: Optional[UUID] = None
    weapon_id: Optional[UUID] = None
    ammunition_id: Optional[UUID] = None
    distance: Optional[str] = None
    firing_cadence: Optional[str] = None
    time_limit: Optional[str] = None
    ammunition_allocated: Optional[int] = None
    ammunition_used: Optional[int] = None
    hits: Optional[int] = None
    reaction_time: Optional[float] = None

    @model_validator(mode="after")
    def validate_update_data(self) -> "PracticeExerciseUpdate":
        if self.hits is not None and self.ammunition_used is not None:
            if self.hits > self.ammunition_used:
                raise ValueError(
                    "Los impactos no pueden ser mayores que la munición utilizada"
                )
        if self.ammunition_used is not None and self.ammunition_allocated is not None:
            if self.ammunition_used > self.ammunition_allocated:
                raise ValueError(
                    "La munición utilizada no puede ser mayor que la munición asignada"
                )
        return self


class PracticeExerciseRead(PracticeExerciseBase):
    id: UUID
    accuracy_percentage: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Campos de puntuación y agrupamiento
    total_score: Optional[int] = None
    average_score_per_shot: Optional[float] = None
    max_score_achieved: Optional[int] = None
    score_distribution: Optional[Dict[str, int]] = None
    group_diameter: Optional[float] = None

    model_config = {"from_attributes": True}
    
    @field_validator('score_distribution', mode='before')
    @classmethod
    def parse_score_distribution(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v

class TargetAnalysisRead(BaseModel):
    id: UUID
    # accuracy_percentage: Optional[float]
    average_confidence: Optional[float]
    analysis_method: Optional[str]
    model_version: Optional[str]
    total_impacts_detected: Optional[int]
    fresh_impacts_inside: Optional[int]
    fresh_impacts_outside: Optional[int]
    confidence_threshold: Optional[float]
    analysis_timestamp: Optional[datetime]

    model_config = {"from_attributes": True}


class TargetImageRead(BaseModel):
    id: UUID
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: datetime
    analysis: Optional[TargetAnalysisRead] = None

    model_config = {"from_attributes": True}


class PracticeExerciseDetail(BaseModel):
    id: UUID
    session_id: UUID
    exercise_type: Optional[ExerciseTypeInfo]
    target: Optional[TargetInfo]
    weapon: Optional[WeaponInfo]
    ammunition: Optional[AmmunitionInfo]
    distance: str
    firing_cadence: Optional[str]
    time_limit: Optional[str]
    ammunition_allocated: int
    ammunition_used: int
    hits: int
    accuracy_percentage: float
    reaction_time: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    target_image: Optional[TargetImageRead]
    # Campos de puntuación y agrupamiento
    total_score: Optional[int] = None
    average_score_per_shot: Optional[float] = None
    max_score_achieved: Optional[int] = None
    score_distribution: Optional[Dict[str, int]] = None
    group_diameter: Optional[float] = None

    model_config = {"from_attributes": True}


class PracticeExerciseList(BaseModel):
    items: List[PracticeExerciseRead]
    total: int
    page: int
    size: int
    pages: int


class PracticeExerciseStatistics(BaseModel):
    total_exercises: int
    avg_accuracy: float
    total_ammunition_used: int
    total_hits: int
    hit_percentage: float
    avg_reaction_time: Optional[float] = None
    by_distance: Optional[List[Dict[str, Any]]] = None
    by_exercise_type: Optional[List[Dict[str, Any]]] = None
    by_weapon: Optional[List[Dict[str, Any]]] = None
    # by_ammunition: Optional[List[Dict[str, Any]]] = None


# Esquema para analisis especificos
class PerformanceAnalysis(BaseModel):
    category: str  # 'weapon', 'ammunition', "target", 'distance, etc
    items: List[Dict[str, Any]]
    avg_accuracy: float
    total_exercises: int


class PracticeExerciseFilter(BaseModel):
    session_id: Optional[UUID] = None
    shooter_id: Optional[UUID] = None  # para buscar ejercicios a traves de las sesion
    exercise_type_id: Optional[UUID] = None
    target_id: Optional[UUID] = None
    weapon_id: Optional[UUID] = None
    ammunition_id: Optional[UUID] = None
    distance: Optional[str] = None
    min_accuracy: Optional[float] = None
    max_accuracy: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None
    skip: int = 0
    limit: int = 100
