from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body

from src.application.services.target_analysis_service import TargetAnalysisService
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.target_analysis_schema import (
    ExerciseAnalysisResponse,
    ExerciseAnalysisRequest,
    # Nuevos esquemas opcionales
    EnhancedExerciseAnalysisRequest,
    CompleteAnalysisResponse,
    TargetConfigResponse,
    AnalysisErrorResponse,
    SessionScoringStats,
)
from src.infraestructure.database.session import get_db
from src.application.services.enhanced_target_analysis_service import (
    EnhancedTargetAnalysisService,
)
from src.application.services.target_analysis_factory import (
    TargetAnalysisServiceFactory,
)

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/exercise/{exercise_id}/analyze/", response_model=ExerciseAnalysisResponse
)
async def analyze_exercise_image(
    exercise_id: UUID = Path(..., description="ID del ejercicio a analizar"),
    request: ExerciseAnalysisRequest = Body(..., description="Parámetros de análisis"),
    service: EnhancedTargetAnalysisService = Depends(
        TargetAnalysisServiceFactory.create_enhanced_service
    ),
    current_user=Depends(get_current_user),
):
    """
    Analiza la imagen de un ejercicio y devuelve los resultados del análisis.
    """
    try:
        # Usar el método de compatibilidad total del servicio mejorado
        result, error = service.analyze_exercise_image(
            exercise_id=exercise_id,
            confidence_threshold=request.confidence_threshold,
            force_reanalysis=request.force_reanalysis,
        )

        if error:
            # Mantener el mismo manejo de errores
            raise HTTPException(status_code=400, detail=error)

        return result

    except HTTPException:
        raise
    except Exception as e:
        # Mantener el mismo manejo de errores
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/exercise/{exercise_id}/analysis/", response_model=ExerciseAnalysisResponse
)
async def get_exercise_analysis(
    exercise_id: UUID,
    service: EnhancedTargetAnalysisService = Depends(
        TargetAnalysisServiceFactory.create_enhanced_service
    ),
    current_user=Depends(get_current_user),
):
    """
    Obtiene el análisis más reciente de un ejercicio
    """

    result, error = service.get_exercise_analysis(exercise_id=exercise_id)
    if error == "EXERCISE_OR_IMAGE_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Ejercicio o imagen no encontrado")
    elif error == "ANALYSIS_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    if error:
        raise HTTPException(status_code=500, detail=error)

    return result


@router.post(
    "/exercise/{exercise_id}/analyze-enhanced", response_model=ExerciseAnalysisResponse
)
async def analyze_exercise_with_enhanced_options(
    exercise_id: UUID = Path(..., description="ID del ejercicio a analizar"),
    request: EnhancedExerciseAnalysisRequest = Body(
        ..., description="Parámetros de análisis mejorados"
    ),
    service: EnhancedTargetAnalysisService = Depends(
        TargetAnalysisServiceFactory.create_enhanced_service
    ),
    current_user=Depends(get_current_user),
):
    """
    🚀 NUEVO: Análisis mejorado con opciones avanzadas

    **Características adicionales:**
    - Control explícito de puntuación (enable_scoring)
    - Selección de tipo de blanco (target_type)
    - Validaciones mejoradas de imagen
    - Respuesta con datos completos de puntuación

    **Uso recomendado:**
    - Para interfaces que quieren controlar el cálculo de puntuación
    - Para análisis detallado con métricas avanzadas
    - Para desarrollo y testing de nuevas características
    """
    try:
        result, error = service.analyze_exercise_image(
            exercise_id=exercise_id,
            confidence_threshold=request.confidence_threshold,
            force_reanalysis=request.force_reanalysis,
            enable_scoring=request.enable_scoring,  # ✅ Control explícito
        )

        if error:
            # Mapear errores específicos para mejor UX
            error_mapping = {
                "EXERCISE_OR_IMAGE_NOT_FOUND": {
                    "status": 404,
                    "detail": "Ejercicio o imagen no encontrados",
                },
                "DETECTION_ERROR": {
                    "status": 422,
                    "detail": "Error en la detección de impactos - revisar calidad de imagen",
                },
                "ENHANCED_ANALYSIS_ERROR": {
                    "status": 500,
                    "detail": "Error en el análisis mejorado",
                },
            }

            error_code = error.split(":")[0]
            error_info = error_mapping.get(error_code, {"status": 500, "detail": error})

            raise HTTPException(
                status_code=error_info["status"], detail=error_info["detail"]
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en análisis mejorado: {str(e)}"
        )


@router.get("/exercise/{exercise_id}", response_model=ExerciseAnalysisResponse)
async def get_exercise_analysis(
    exercise_id: UUID = Path(..., description="ID del ejercicio"),
    service: EnhancedTargetAnalysisService = Depends(
        TargetAnalysisServiceFactory.create_enhanced_service
    ),
    current_user=Depends(get_current_user),
):
    """
    ✅ ENDPOINT EXISTENTE - Obtiene análisis existente

    **Mejorado automáticamente:**
    - Ahora incluye datos de puntuación si están disponibles
    - Mantiene compatibilidad total con respuestas anteriores
    - Campos de puntuación aparecen solo si fueron calculados
    """
    try:
        result, error = service.get_exercise_analysis_with_scoring(exercise_id)

        if error:
            status_code = 404 if "NOT_FOUND" in error else 500
            raise HTTPException(status_code=status_code, detail=error)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener análisis: {str(e)}"
        )


@router.post(
    "/exercise/{exercise_id}/reanalyze-scoring", response_model=ExerciseAnalysisResponse
)
async def reanalyze_exercise_with_scoring(
    exercise_id: UUID = Path(..., description="ID del ejercicio a re-analizar"),
    confidence_threshold: float = Query(
        0.25, ge=0.1, le=0.9, description="Umbral de confianza"
    ),
    service: EnhancedTargetAnalysisService = Depends(
        TargetAnalysisServiceFactory.create_enhanced_service
    ),
    current_user=Depends(get_current_user),
):
    """
    🔄 NUEVO: Re-analiza un ejercicio existente agregando datos de puntuación

    **Útil para:**
    - Migrar análisis existentes al nuevo sistema
    - Recalcular puntuación con diferentes parámetros
    - Corregir análisis con problemas

    **Comportamiento:**
    - Fuerza nuevo análisis con puntuación habilitada
    - Actualiza datos existentes sin crear duplicados
    - Mantiene historial en análisis timestamp
    """
    try:
        result, error = service.analyze_exercise_image(
            exercise_id=exercise_id,
            confidence_threshold=confidence_threshold,
            force_reanalysis=True,  # Forzar re-análisis
            enable_scoring=True,  # Asegurar que se calcula puntuación
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en re-análisis: {str(e)}")
