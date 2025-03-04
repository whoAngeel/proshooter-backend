from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime

class ShootingClubBase(BaseModel):
    name : str = Field(..., min_length=3, max_length=100, description="El nombre debe tener entre 3 y 100 caracteres")
    description: Optional[str] = Field(None, description="La descripción del Club de tiro")

class ShootingClubCreate(ShootingClubBase):
    chief_instructor_id: UUID4 = Field(..., description="ID del jefe de instructores que administrará el club")

class ShootingClubUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="El nombre debe tener entre 3 y 100 caracteres")
    description: Optional[str] = Field(None, description="La descripción del Club de tiro")
    is_active: Optional[bool] = Field(None, description="Indica si el Club de tiro está activo")

class ShootingClubRead(ShootingClubBase):
    id: UUID4 = Field(..., description="ID del Club de tiro")
    chief_instructor_id: UUID4 = Field(..., description="ID del jefe de instructores que administrará el club")
    is_active: bool = Field(..., description="Indica si el Club de tiro está activo")
    created_at: datetime = Field(..., description="Fecha de creación del Club de tiro")
    updated_at: Optional[datetime] = Field(None, description="Fecha de actualización del Club de tiro")

    class Config:
        from_attributes = True

class ShootingClubWithChiefInstructor(ShootingClubRead):
    from src.presentation.schemas.user_schemas import UserReadLite
    chief_instructor: Optional[UserReadLite] = Field(None, description="Datos del jefe de instructores")

class ClubMemberStatsBasic(BaseModel):
    total_shots: int = Field(0, description="Total de tiros realizados")
    acuracy: int = Field(0, description="Precisión del tirador")
    average_hit_factor: float = Field(0.0, description="Factor de acierto promedio")

    class Config:
        from_attributes = True

class ClubMemberBasic(BaseModel):
    user_id = UUID4 = Field(..., description="ID del tirador")
    classification: str = Field(..., description="Clasificación del tirador")
    stats: Optional[ClubMemberStatsBasic] = Field(None, description="Estadísticas básicas del tirador")

    class Config:
        from_attributes = True

class ClubMemberDetail(ClubMemberBasic):
    from src.presentation.schemas.user_schemas import UserReadLite

    user = Optional[UserReadLite] = Field(None, description="Datos del tirador")

    class Config:
        from_attributes = True

class ShootingClubWithBasicStats(ShootingClubWithChiefInstructor):
    member_count: int = Field(0, description="Cantidad de miembros del Club de tiro")
    average_accuracy: float = Field(0.0, description="Precisión promedio del Club de tiro")

class ShootingClubDetail(ShootingClubWithBasicStats):
    members: List[ClubMemberDetail] = Field([], description="Miembros del Club de tiro")
    best_shooter: Optional[Dict[str, Any]] = Field(None, description="Tirador con mejor precisión del Club de tiro")

class ShootingClubStatistics(BaseModel):
    """
    Esquema específico para estadísticas del club.
    Contiene métricas detalladas de rendimiento.
    """
    member_count: int = Field(0, description="Número de miembros en el club")
    average_accuracy: float = Field(0, description="Precisión promedio de los miembros")
    best_accuracy: float = Field(0, description="Mejor precisión entre los miembros")
    best_shooter: Optional[Dict[str, Any]] = Field(None, description="Información del mejor tirador")
    total_shots: int = Field(0, description="Total de disparos realizados por los miembros")
    message: Optional[str] = Field(None, description="Mensaje informativo si aplica")

class ShooterClubAssignment(BaseModel):
    """
    Esquema para asignar un tirador a un club.
    Utilizado para operaciones de gestión de membresía.
    """
    shooter_id: UUID4 = Field(..., description="ID del tirador a asignar al club")


from src.presentation.schemas.user_schemas import UserReadLite
from src.presentation.schemas.shooter_schema import ShooterReadLite
from src.presentation.schemas.user_stats_schema import ShooterStatsRead

ShootingClubWithChiefInstructor.model_rebuild()
ClubMemberDetail.model_rebuild()
