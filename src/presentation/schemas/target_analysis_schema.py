from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class ImpactDetection(BaseModel):
    tipo: str  # "impacto_fresco_dentro", "impacto_fresco_fuera", etc.
    centro_x: float
    centro_y: float
    confianza: float
    es_fresco: bool
    dentro_blanco: bool


class ConfidenceStats(BaseModel):
    promedio: float
    minimo: float
    maximo: float
    desviacion_estandar: float


class ExerciseAnalysisResponse(BaseModel):
    exercise_id: UUID
    analysis_id: UUID
    analysis_timestamp: datetime

    # Estadísticas principales
    total_impactos_detectados: int
    impactos_frescos_dentro: int
    impactos_frescos_fuera: int
    impactos_tapados_dentro: int
    impactos_tapados_fuera: int
    precision_porcentaje: float

    # Datos detallados
    coordenadas_impactos: List[ImpactDetection]
    estadisticas_confianza: ConfidenceStats

    # Metadata
    modelo_version: str
    umbral_confianza: float


class ExerciseAnalysisRequest(BaseModel):
    confidence_threshold: Optional[float] = 0.25
    force_reanalysis: Optional[bool] = False
