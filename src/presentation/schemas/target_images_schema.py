# src/presentation/schemas/target_image_schema.py
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# Esquemas para información relacionada
class ExerciseInfo(BaseModel):
    """Información básica del ejercicio asociado a la imagen."""

    id: UUID
    exercise_type: Optional[str] = None
    distance: Optional[str] = None
    accuracy_percentage: Optional[float] = None

    model_config = {"from_attributes": True}


class SessionInfo(BaseModel):
    """Información de la sesión a la que pertenece el ejercicio."""

    id: UUID
    date: datetime
    location: str
    shooter_id: UUID

    model_config = {"from_attributes": True}


class AnalysisInfo(BaseModel):
    """Información básica sobre el análisis de la imagen."""

    id: UUID
    total_impacts_detected: int
    analysis_confidence: float
    analysis_timestamp: datetime

    model_config = {"from_attributes": True}


# Esquemas base para las imágenes de blancos
class TargetImageBase(BaseModel):
    """Esquema base que define los campos comunes para las imágenes de blancos."""

    exercise_id: UUID
    file_path: str
    file_size: int = Field(gt=0, description="Tamaño del archivo en bytes")
    content_type: str

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, value: str) -> str:
        """Valida que el tipo de contenido sea un formato de imagen soportado."""
        allowed_types = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/tiff",
            "image/bmp",
            "image/webp",
        ]
        if value.lower() not in allowed_types:
            raise ValueError(
                f'Tipo de contenido no soportado: {value}. Tipos permitidos: {", ".join(allowed_types)}'
            )
        return value.lower()

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, value: str) -> str:
        """Valida que la ruta del archivo no esté vacía y tenga un formato básico válido."""
        if not value or not value.strip():
            raise ValueError("La ruta del archivo no puede estar vacía")

        # Verificar que tenga una extensión de archivo válida
        valid_extensions = [".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".webp"]
        if not any(value.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(
                f'El archivo debe tener una extensión válida: {", ".join(valid_extensions)}'
            )

        return value.strip()


class TargetImageCreate(TargetImageBase):
    """Esquema para crear una nueva imagen de blanco."""

    pass


class TargetImageUpdate(BaseModel):
    """Esquema para actualizar una imagen de blanco existente."""

    file_path: Optional[str] = None
    file_size: Optional[int] = Field(None, gt=0)
    content_type: Optional[str] = None

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, value: Optional[str]) -> Optional[str]:
        """Valida el tipo de contenido solo si se proporciona."""
        if value is None:
            return value

        allowed_types = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/tiff",
            "image/bmp",
            "image/webp",
        ]
        if value.lower() not in allowed_types:
            raise ValueError(f"Tipo de contenido no soportado: {value}")
        return value.lower()


class TargetImageRead(TargetImageBase):
    """Esquema para leer información de una imagen de blanco."""

    id: UUID
    uploaded_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TargetImageDetail(TargetImageRead):
    """Esquema detallado que incluye información relacionada."""

    exercise: Optional[ExerciseInfo] = None
    session: Optional[SessionInfo] = None
    analyses: List[AnalysisInfo] = []
    analysis_count: int = 0

    model_config = {"from_attributes": True}


class TargetImageList(BaseModel):
    """Esquema para listas paginadas de imágenes de blancos."""

    items: List[TargetImageRead]
    total: int
    page: int
    size: int
    pages: int


class TargetImageFilter(BaseModel):
    """Esquema para filtrar imágenes de blancos en consultas."""

    exercise_id: Optional[UUID] = None
    shooter_id: Optional[UUID] = None
    content_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_size: Optional[int] = Field(None, gt=0)
    max_size: Optional[int] = Field(None, gt=0)
    has_analysis: Optional[bool] = None
    skip: int = 0
    limit: int = 100

    @field_validator("max_size")
    @classmethod
    def validate_size_range(cls, max_size: Optional[int], info) -> Optional[int]:
        """Valida que el tamaño máximo sea mayor que el mínimo si ambos están presentes."""
        if max_size is not None and hasattr(info.data, "min_size"):
            min_size = info.data.get("min_size")
            if min_size is not None and max_size <= min_size:
                raise ValueError("El tamaño máximo debe ser mayor que el tamaño mínimo")
        return max_size


class TargetImageUploadResponse(BaseModel):
    """Esquema para la respuesta después de subir una imagen."""

    image_id: UUID
    file_path: str
    file_size: int
    content_type: str
    upload_status: str
    message: str


class TargetImageAnalysisSummary(BaseModel):
    """Esquema para resumir el estado de análisis de las imágenes."""

    total_images: int
    analyzed_images: int
    pending_analysis: int
    analysis_percentage: float
    recent_uploads: List[TargetImageRead] = []


class ExerciseImageGallery(BaseModel):
    """Esquema para mostrar todas las imágenes de un ejercicio como galería."""

    exercise_id: UUID
    exercise_info: ExerciseInfo
    images: List[TargetImageRead]
    total_images: int
    total_size_mb: float


class ShooterImageHistory(BaseModel):
    """Esquema para mostrar el historial de imágenes de un tirador."""

    shooter_id: UUID
    images: List[TargetImageDetail]
    date_range: Dict[str, datetime]
    total_images: int
    total_size_mb: float
    content_type_distribution: Dict[str, int]
