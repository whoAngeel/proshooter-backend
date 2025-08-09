# 1. ACTUALIZAR ESQUEMAS EXISTENTES MANTENIENDO COMPATIBILIDAD
# src/presentation/schemas/target_analysis_schema.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime


# ✅ MANTENER esquemas existentes intactos
class ImpactDetection(BaseModel):
    """Esquema existente - mantener sin cambios"""

    tipo: str  # "impacto_fresco_dentro", "impacto_fresco_fuera", etc.
    centro_x: float
    centro_y: float
    confianza: float
    es_fresco: bool
    dentro_blanco: bool


class ConfidenceStats(BaseModel):
    """Esquema existente - mantener sin cambios"""

    promedio: float
    minimo: float
    maximo: float
    desviacion_estandar: float


# ✅ EXTENDER esquema principal con campos opcionales (compatibilidad)
class ExerciseAnalysisResponse(BaseModel):
    """
    Esquema de respuesta extendido que mantiene 100% compatibilidad
    con el formato existente y agrega campos opcionales de puntuación
    """

    # ✅ CAMPOS EXISTENTES (mantener exactos)
    exercise_id: UUID
    analysis_id: UUID
    analysis_timestamp: datetime

    # Estadísticas principales existentes
    total_impactos_detectados: int
    impactos_frescos_dentro: int
    impactos_frescos_fuera: int
    impactos_tapados_dentro: int
    impactos_tapados_fuera: int
    precision_porcentaje: float

    # Datos detallados existentes
    coordenadas_impactos: List[Dict[str, Any]]
    estadisticas_confianza: Dict[str, float]

    # Información de consolidación existente
    consolidation_info: Optional[Dict[str, Any]] = None

    # Metadata existentes
    modelo_version: str
    umbral_confianza: float

    # ✅ NUEVOS CAMPOS OPCIONALES (no rompen compatibilidad)
    puntuacion_total: Optional[int] = Field(
        None, description="Puntuación total del ejercicio"
    )
    puntuacion_promedio: Optional[float] = Field(
        None, description="Puntuación promedio por disparo"
    )
    puntuacion_maxima: Optional[int] = Field(
        None, description="Mejor disparo individual"
    )
    distribucion_puntuacion: Optional[Dict[str, int]] = Field(
        None, description="Distribución por zonas"
    )
    diametro_grupo: Optional[float] = Field(
        None, description="Diámetro del grupo en píxeles"
    )
    centro_grupo: Optional[Dict[str, float]] = Field(
        None, description="Centro del grupo de tiro"
    )
    eficiencia_puntuacion: Optional[float] = Field(
        None, description="Eficiencia vs máximo posible (%)"
    )

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override para excluir campos None en la serialización si se desea"""
        data = super().model_dump(**kwargs)

        # Opcional: remover campos de puntuación si son None (para compatibilidad total)
        if kwargs.get("exclude_none", False):
            return {k: v for k, v in data.items() if v is not None}

        return data


class ExerciseAnalysisRequest(BaseModel):
    """Esquema de request existente - mantener sin cambios"""

    confidence_threshold: Optional[float] = Field(0.25, ge=0.1, le=0.9)
    force_reanalysis: Optional[bool] = False


class EnhancedExerciseAnalysisRequest(ExerciseAnalysisRequest):
    """
    Esquema de request extendido que permite controlar la puntuación
    Compatible con el esquema existente
    """

    enable_scoring: Optional[bool] = Field(
        True, description="Habilitar cálculo de puntuación"
    )
    target_type: Optional[str] = Field(
        "PRO_SHOOTER", description="Tipo de blanco a analizar"
    )


# ✅ NUEVOS ESQUEMAS ESPECÍFICOS PARA PUNTUACIÓN
class ShotScoreDetail(BaseModel):
    """Detalle de puntuación de un disparo individual"""

    centro_x: float
    centro_y: float
    confianza: float
    score: int = Field(..., ge=0, le=10, description="Puntuación del disparo (0-10)")
    zone: str = Field(..., description="Zona del blanco")
    distance_from_center: float = Field(
        ..., description="Distancia al centro en píxeles"
    )
    distance_ratio: float = Field(..., description="Ratio de distancia normalizada")


class GroupStatisticsSchema(BaseModel):
    """Estadísticas del grupo de tiro"""

    center_x: float = Field(..., description="Centro X del grupo")
    center_y: float = Field(..., description="Centro Y del grupo")
    diameter: float = Field(..., description="Diámetro del grupo en píxeles")
    average_distance_from_center: float = Field(
        ..., description="Distancia promedio del centro"
    )
    std_deviation: float = Field(..., description="Desviación estándar")
    shots_count: int = Field(..., description="Número de disparos en el grupo")


class ScoreDistributionSchema(BaseModel):
    """Distribución de puntuación por zonas"""

    zone_10: int = Field(0, description="Disparos en zona de 10 puntos")
    zone_9: int = Field(0, description="Disparos en zona de 9 puntos")
    zone_8: int = Field(0, description="Disparos en zona de 8 puntos")
    zone_7: int = Field(0, description="Disparos en zona de 7 puntos")
    zone_6: int = Field(0, description="Disparos en zona de 6 puntos")
    zone_5: int = Field(0, description="Disparos en zona de 5 puntos")
    zone_4: int = Field(0, description="Disparos en zona de 4 puntos")
    zone_3: int = Field(0, description="Disparos en zona de 3 puntos")
    zone_2: int = Field(0, description="Disparos en zona de 2 puntos")
    zone_1: int = Field(0, description="Disparos en zona de 1 punto")
    zone_0: int = Field(0, description="Disparos fuera del blanco")

    @classmethod
    def from_dict(cls, distribution: Dict[str, int]) -> "ScoreDistributionSchema":
        """Convierte diccionario a esquema"""
        return cls(
            zone_10=distribution.get("10", 0),
            zone_9=distribution.get("9", 0),
            zone_8=distribution.get("8", 0),
            zone_7=distribution.get("7", 0),
            zone_6=distribution.get("6", 0),
            zone_5=distribution.get("5", 0),
            zone_4=distribution.get("4", 0),
            zone_3=distribution.get("3", 0),
            zone_2=distribution.get("2", 0),
            zone_1=distribution.get("1", 0),
            zone_0=distribution.get("0", 0),
        )


# ✅ ESQUEMA COMPLETO DE ANÁLISIS CON PUNTUACIÓN (nuevo, opcional)
class CompleteAnalysisResponse(BaseModel):
    """
    Respuesta completa con todos los datos de puntuación
    Para casos donde se quiera toda la información detallada
    """

    # Datos básicos
    exercise_id: UUID
    analysis_id: UUID
    analysis_timestamp: datetime

    # Estadísticas de impactos
    total_impactos_detectados: int
    impactos_frescos_dentro: int
    impactos_frescos_fuera: int
    impactos_tapados_dentro: int
    impactos_tapados_fuera: int
    precision_porcentaje: float

    # Puntuación detallada
    puntuacion_total: int
    puntuacion_promedio: float
    puntuacion_maxima: int
    distribucion_puntuacion: ScoreDistributionSchema
    eficiencia_puntuacion: float

    # Análisis de grupo
    grupo_estadisticas: Optional[GroupStatisticsSchema] = None
    disparos_detallados: List[ShotScoreDetail] = []

    # Metadatos
    modelo_version: str
    umbral_confianza: float
    tipo_blanco: str = "PRO_SHOOTER"


# ✅ ESQUEMAS PARA CONFIGURACIÓN DE BLANCOS
class TargetZoneSchema(BaseModel):
    """Esquema para zona de blanco"""

    score: int = Field(..., ge=0, le=10)
    radius_ratio: float = Field(..., ge=0, le=1)


class TargetConfigurationSchema(BaseModel):
    """Esquema para configuración de blanco"""

    name: str
    type: str
    center_x_ratio: float = Field(..., ge=0, le=1)
    center_y_ratio: float = Field(..., ge=0, le=1)
    zones: List[TargetZoneSchema]

    class Config:
        schema_extra = {
            "example": {
                "name": "PRO-SHOOTER",
                "type": "PRO_SHOOTER",
                "center_x_ratio": 0.5,
                "center_y_ratio": 0.5,
                "zones": [
                    {"score": 10, "radius_ratio": 0.045},
                    {"score": 9, "radius_ratio": 0.090},
                    # ... más zonas
                ],
            }
        }


# ✅ ESQUEMAS PARA EVOLUCIÓN Y ESTADÍSTICAS
class ShooterEvolutionEntry(BaseModel):
    """Entrada de evolución de un tirador"""

    analysis_timestamp: datetime
    total_score: int
    average_score_per_shot: float
    accuracy_percentage: float
    group_diameter: Optional[float] = None
    exercise_type: str
    session_date: datetime


class ShooterEvolutionResponse(BaseModel):
    """Respuesta de evolución del tirador"""

    shooter_id: UUID
    evolution_entries: List[ShooterEvolutionEntry]

    # Estadísticas resumidas
    total_sessions: int
    average_score_trend: float
    accuracy_trend: float
    improvement_percentage: Optional[float] = None


class SessionScoringStats(BaseModel):
    """Estadísticas de puntuación para una sesión"""

    session_id: UUID
    total_exercises_analyzed: int
    total_session_score: int
    average_score_per_exercise: float
    average_score_per_shot: float
    best_shot_score: int
    average_group_diameter: Optional[float] = None
    score_distribution: ScoreDistributionSchema
    accuracy_percentage: float


# ✅ ESQUEMAS DE ERROR MEJORADOS
class AnalysisErrorResponse(BaseModel):
    """Respuesta de error mejorada"""

    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "error_code": "INVALID_IMAGE_FORMAT",
                "error_message": "La imagen debe ser cuadrada (1:1) para análisis de puntuación",
                "details": {
                    "current_dimensions": "800x600",
                    "required_format": "square (1:1)",
                },
                "suggestions": [
                    "Recorte la imagen para que tenga el mismo ancho y alto",
                    "Asegúrese de que el centro del blanco esté en el centro de la imagen",
                ],
            }
        }


# ✅ CONVERSORES PARA MANTENER COMPATIBILIDAD
class SchemaConverter:
    """Utilidades para convertir entre formatos de esquemas"""

    @staticmethod
    def legacy_to_enhanced_response(
        legacy_data: Dict[str, Any], scoring_data: Optional[Dict[str, Any]] = None
    ) -> ExerciseAnalysisResponse:
        """
        Convierte datos legacy a formato de respuesta mejorado
        """
        # Datos básicos (obligatorios)
        response_data = {
            "exercise_id": legacy_data["exercise_id"],
            "analysis_id": legacy_data["analysis_id"],
            "analysis_timestamp": legacy_data["analysis_timestamp"],
            "total_impactos_detectados": legacy_data["total_impactos_detectados"],
            "impactos_frescos_dentro": legacy_data["impactos_frescos_dentro"],
            "impactos_frescos_fuera": legacy_data["impactos_frescos_fuera"],
            "impactos_tapados_dentro": legacy_data["impactos_tapados_dentro"],
            "impactos_tapados_fuera": legacy_data["impactos_tapados_fuera"],
            "precision_porcentaje": legacy_data["precision_porcentaje"],
            "coordenadas_impactos": legacy_data["coordenadas_impactos"],
            "estadisticas_confianza": legacy_data["estadisticas_confianza"],
            "modelo_version": legacy_data["modelo_version"],
            "umbral_confianza": legacy_data["umbral_confianza"],
            "consolidation_info": legacy_data.get("consolidation_info"),
        }

        # Agregar datos de puntuación si están disponibles
        if scoring_data:
            response_data.update(
                {
                    "puntuacion_total": scoring_data.get("total_score"),
                    "puntuacion_promedio": scoring_data.get("average_score_per_shot"),
                    "puntuacion_maxima": scoring_data.get("max_score_achieved"),
                    "distribucion_puntuacion": scoring_data.get("score_distribution"),
                    "diametro_grupo": scoring_data.get("shooting_group_diameter"),
                    "centro_grupo": (
                        {
                            "x": scoring_data.get("group_center_x"),
                            "y": scoring_data.get("group_center_y"),
                        }
                        if scoring_data.get("group_center_x") is not None
                        else None
                    ),
                    "eficiencia_puntuacion": scoring_data.get("score_efficiency"),
                }
            )

        return ExerciseAnalysisResponse(**response_data)

    @staticmethod
    def enhanced_to_complete_response(
        enhanced_response: ExerciseAnalysisResponse,
        detailed_shots: Optional[List[ShotScoreDetail]] = None,
        group_stats: Optional[GroupStatisticsSchema] = None,
    ) -> CompleteAnalysisResponse:
        """
        Convierte respuesta mejorada a respuesta completa con todos los detalles
        """
        score_distribution = ScoreDistributionSchema.from_dict(
            enhanced_response.distribucion_puntuacion or {}
        )

        return CompleteAnalysisResponse(
            exercise_id=enhanced_response.exercise_id,
            analysis_id=enhanced_response.analysis_id,
            analysis_timestamp=enhanced_response.analysis_timestamp,
            total_impactos_detectados=enhanced_response.total_impactos_detectados,
            impactos_frescos_dentro=enhanced_response.impactos_frescos_dentro,
            impactos_frescos_fuera=enhanced_response.impactos_frescos_fuera,
            impactos_tapados_dentro=enhanced_response.impactos_tapados_dentro,
            impactos_tapados_fuera=enhanced_response.impactos_tapados_fuera,
            precision_porcentaje=enhanced_response.precision_porcentaje,
            puntuacion_total=enhanced_response.puntuacion_total or 0,
            puntuacion_promedio=enhanced_response.puntuacion_promedio or 0.0,
            puntuacion_maxima=enhanced_response.puntuacion_maxima or 0,
            distribucion_puntuacion=score_distribution,
            eficiencia_puntuacion=enhanced_response.eficiencia_puntuacion or 0.0,
            grupo_estadisticas=group_stats,
            disparos_detallados=detailed_shots or [],
            modelo_version=enhanced_response.modelo_version,
            umbral_confianza=enhanced_response.umbral_confianza,
            tipo_blanco="PRO_SHOOTER",
        )


# ✅ VALIDADORES DE ESQUEMAS
from pydantic import field_validator, root_validator, model_validator


class EnhancedExerciseAnalysisRequestWithValidation(EnhancedExerciseAnalysisRequest):
    """Request con validaciones adicionales"""

    @field_validator("confidence_threshold")
    def validate_confidence_threshold(cls, v):
        if not 0.1 <= v <= 0.9:
            raise ValueError("confidence_threshold debe estar entre 0.1 y 0.9")
        return v

    @field_validator("target_type")
    def validate_target_type(cls, v):
        valid_types = ["PRO_SHOOTER", "IPSC", "ISSF"]
        if v not in valid_types:
            raise ValueError(f"target_type debe ser uno de: {valid_types}")
        return v

    @model_validator(mode="after")
    def validate_scoring_requirements(cls, values):
        enable_scoring = values.get("enable_scoring", True)
        target_type = values.get("target_type", "PRO_SHOOTER")

        if enable_scoring and target_type not in ["PRO_SHOOTER"]:
            raise ValueError(
                "Scoring solo está disponible para blancos PRO_SHOOTER actualmente"
            )

        return values


# ✅ SCHEMAS PARA ENDPOINTS DE CONFIGURACIÓN
class TargetConfigResponse(BaseModel):
    """Respuesta de configuración de blanco"""

    target_type: str
    scoring_zones: List[TargetZoneSchema]
    center_position: Dict[str, float]
    instructions: Dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "target_type": "PRO_SHOOTER",
                "scoring_zones": [
                    {"score": 10, "radius_ratio": 0.045},
                    {"score": 9, "radius_ratio": 0.090},
                ],
                "center_position": {"x_ratio": 0.5, "y_ratio": 0.5},
                "instructions": {
                    "image_format": "Cuadrado 1:1",
                    "center_requirement": "Centro del blanco debe coincidir con centro de imagen",
                    "min_resolution": "512x512 píxeles recomendado",
                    "supported_formats": ["JPG", "PNG", "WEBP"],
                },
            }
        }


# ✅ FACTORY PARA CREAR RESPUESTAS
class ResponseFactory:
    """Factory para crear diferentes tipos de respuestas"""

    @staticmethod
    def create_legacy_compatible_response(
        analysis_data: Dict[str, Any],
    ) -> ExerciseAnalysisResponse:
        """Crea respuesta compatible con formato legacy"""
        return ExerciseAnalysisResponse(
            **analysis_data,
            # Campos de puntuación como None para mantener compatibilidad
            puntuacion_total=None,
            puntuacion_promedio=None,
            puntuacion_maxima=None,
            distribucion_puntuacion=None,
            diametro_grupo=None,
            centro_grupo=None,
            eficiencia_puntuacion=None,
        )

    @staticmethod
    def create_enhanced_response(
        basic_data: Dict[str, Any], scoring_data: Dict[str, Any]
    ) -> ExerciseAnalysisResponse:
        """Crea respuesta con datos de puntuación"""
        return SchemaConverter.legacy_to_enhanced_response(basic_data, scoring_data)

    @staticmethod
    def create_error_response(
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> AnalysisErrorResponse:
        """Crea respuesta de error estructurada"""
        return AnalysisErrorResponse(
            error_code=error_code,
            error_message=error_message,
            details=details,
            suggestions=suggestions,
        )


# ✅ BACKWARD COMPATIBILITY ALIASES
# Mantener alias para códigothat ya usa los esquemas anteriores
ExerciseAnalysisSchema = ExerciseAnalysisResponse  # Alias de compatibilidad
ImpactDetectionSchema = ImpactDetection  # Alias de compatibilidad
ConfidenceStatsSchema = ConfidenceStats  # Alias de compatibilidad

# ✅ EXPORT ALL SCHEMAS
__all__ = [
    # Esquemas existentes (compatibilidad)
    "ImpactDetection",
    "ConfidenceStats",
    "ExerciseAnalysisResponse",
    "ExerciseAnalysisRequest",
    # Esquemas nuevos
    "EnhancedExerciseAnalysisRequest",
    "ShotScoreDetail",
    "GroupStatisticsSchema",
    "ScoreDistributionSchema",
    "CompleteAnalysisResponse",
    "TargetZoneSchema",
    "TargetConfigurationSchema",
    "ShooterEvolutionEntry",
    "ShooterEvolutionResponse",
    "SessionScoringStats",
    "AnalysisErrorResponse",
    "TargetConfigResponse",
    # Utilidades
    "SchemaConverter",
    "ResponseFactory",
    # Alias de compatibilidad
    "ExerciseAnalysisSchema",
    "ImpactDetectionSchema",
    "ConfidenceStatsSchema",
]
