from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator


class ExerciseTypeBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=700)
    type: str = Field(..., description="Tipo de ejercicio")
    difficulty: int = Field(ge=1, le=5)  # dificultad del 1 al 5
    objective: Optional[str] = Field(None, description="Objetivo del ejercicio")
    development: Optional[str] = Field(None, description="Desarrollo del ejercicio")


class ExerciseTypeCreate(ExerciseTypeBase):
    pass

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        allowed_types = {"reaction", "movement", "precision"}
        if v not in allowed_types:
            raise ValueError(f"type must be one of {allowed_types}")
        return v


class ExerciseTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    type: Optional[str] = Field(None, description="Tipo de ejercicio")
    objective: Optional[str] = Field(None)
    development: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        allowed_types = {"reaction", "movement", "precision"}
        if v not in allowed_types:
            raise ValueError(f"type must be one of {allowed_types}")
        return v


class ExerciseTypeRead(ExerciseTypeBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExerciseTypeDetail(ExerciseTypeRead):
    exercises_count: int = Field(
        0, description="Cantidad de ejercicios asociados a este tipo"
    )

    model_config = {"from_attributes": True}


class ExerciseTypeList(BaseModel):
    items: List[ExerciseTypeRead]
    total: int
    page: int
    size: int
    pages: int


class ExerciseTypeFilter(BaseModel):
    search: Optional[str] = Field(None, description="Término de búsqueda")
    difficulty: Optional[int] = None
    active_only: bool = True
    skip: int = 0
    limit: int = 100
