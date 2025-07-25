# schemas/instructor_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class InstructorBasicInfo(BaseModel):
    id: UUID
    email: str
    role: str
    full_name: str
    is_chief_instructor: bool


class AvailableInstructorsResponse(BaseModel):
    success: bool
    instructors: List[InstructorBasicInfo] = Field(default=[])
    club_name: Optional[str] = None
    total_count: int = Field(default=0)


class InstructorClubInfo(BaseModel):
    instructor_id: UUID
    club_id: Optional[UUID]
    club_name: Optional[str]
    can_evaluate: bool


# Para actualizar esquemas de sesión
class PracticeSessionCreateRequest(BaseModel):
    # Agregar a tu esquema existente
    instructor_id: Optional[UUID] = Field(
        None, description="ID del instructor asignado (opcional)"
    )
    location: str = Field(default="Not specified")
    date: Optional[str] = None  # Ajustar según tu implementación actual


class PracticeSessionWithInstructor(BaseModel):
    id: UUID
    shooter_id: UUID
    instructor_id: Optional[UUID]
    instructor_info: Optional[InstructorBasicInfo] = None
    location: str
    total_shots_fired: int
    total_hits: int
    accuracy_percentage: float
    evaluation_pending: bool
    is_finished: bool
    date: str  # Ajustar tipo según tu implementación

    class Config:
        from_attributes = True
