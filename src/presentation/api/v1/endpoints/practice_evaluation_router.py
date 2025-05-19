from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional
from uuid import UUID

from datetime import datetime

from src.application.services.practice_evaluation_service import (
    PracticeEvaluationService,
)
from src.domain.enums.role_enum import RoleEnum
from src.domain.enums.classification_enum import ShooterLevelEnum
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.practice_evaluation_schema import (
    PracticeEvaluationCreate,
    PracticeEvaluationRead,
    PracticeEvaluationUpdate,
    PracticeEvaluationDetail,
    PracticeEvaluationFilter,
    PracticeEvaluationList,
    RatingAnalysis,
    ShooterEvaluationStatistics,
)


router = APIRouter(
    prefix="/practice-evaluations",
    tags=["Evaluaciones de la sesión de practica"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=PracticeEvaluationRead, status_code=201)
async def create_evaluation(
    evaluation_data: PracticeEvaluationCreate,
    service: PracticeEvaluationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Crea una nueva evaluación para una sesión de práctica de tiro.

    Este endpoint permite registrar la evaluación formal de una sesión de práctica de tiro,
    incluyendo calificación final, clasificación, puntos fuertes y débiles, y calificaciones
    específicas para aspectos como postura, agarre, alineación visual, etc.

    La evaluación automáticamente:
    - Marca la sesión como evaluada
    - Actualiza las estadísticas del tirador
    - Puede contribuir a cambios en la clasificación del tirador si muestra un patrón consistente

    Parámetros:
        evaluation_data: Datos completos de la evaluación a crear
        evaluation_service: Servicio de evaluaciones (inyectado)

    Retorna:
        La evaluación creada con su ID y campos calculados

    Códigos de estado:
        201: Evaluación creada exitosamente
        400: Datos de entrada inválidos
        404: Sesión o evaluador no encontrado
        409: La sesión ya tiene una evaluación
    """
    evaluation, error = service.create_evaluation(evaluation_data)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST
        if error in [
            "PRACTICE_SESSION_NOT_FOUND",
            "EVALUATOR_NOT_FOUND",
        ]:
            status_code = status.HTTP_404_NOT_FOUND
        elif error == "EVALUATOR_NOT_AUTHORIZED":
            status_code = status.HTTP_403_FORBIDDEN
        elif error == "SESSION_ALREADY_EVALUATED":
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=error)
    return evaluation


@router.get("/", response_model=PracticeEvaluationDetail)
async def get_evaluation(
    evaluation_id: UUID = Query(..., description="ID de la evaluación a recuperar"),
    service: PracticeEvaluationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene los detalles completos de una evaluación específica.

    Este endpoint devuelve información detallada sobre una evaluación de práctica de tiro,
    incluyendo calificaciones específicas, comentarios, zonas problemáticas identificadas,
    y datos de la sesión relacionada.

    Parámetros:
        evaluation_id: UUID de la evaluación a consultar
        evaluation_service: Servicio de evaluaciones (inyectado)

    Retorna:
        Información completa de la evaluación solicitada

    Códigos de estado:
        200: Operación exitosa
        404: Evaluación no encontrada
    """

    evaluation, error = service.get_evaluation_by_id(evaluation_id=evaluation_id)

    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada",
        )
    return evaluation


@router.get("/session", response_model=PracticeEvaluationDetail)
async def get_session_evaluation(
    session_id: UUID = Query(
        ..., description="ID de la sesión de práctica a consultar"
    ),
    evaluation_service: PracticeEvaluationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene la evaluación asociada a una sesión de práctica específica.

    Este endpoint permite recuperar la evaluación completa asociada a una sesión
    específica de práctica de tiro. Cada sesión puede tener como máximo una evaluación.

    Parámetros:
        session_id: UUID de la sesión de práctica
        evaluation_service: Servicio de evaluaciones (inyectado)

    Retorna:
        La evaluación completa de la sesión solicitada

    Códigos de estado:
        200: Operación exitosa
        404: Sesión no encontrada o sin evaluación
    """
    evaluation, error = evaluation_service.get_evaluation_by_session(session_id)

    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada",
        )
    return evaluation


@router.get("/", response_model=PracticeEvaluationList)
async def list_evaluations(
    session_id: Optional[UUID] = Query(None, description="Filtrar por ID de sesión"),
    shooter_id: Optional[UUID] = Query(None, description="Filtrar por ID del tirador"),
    evaluator_id: Optional[UUID] = Query(
        None, description="Filtrar por ID del evaluador"
    ),
    min_score: Optional[float] = Query(
        None, ge=0, le=100, description="Puntuación mínima"
    ),
    max_score: Optional[float] = Query(
        None, ge=0, le=100, description="Puntuación máxima"
    ),
    classification: Optional[ShooterLevelEnum] = Query(
        None, description="Filtrar por clasificación"
    ),
    start_date: Optional[datetime] = Query(
        None, description="Fecha de inicio para filtrar"
    ),
    end_date: Optional[datetime] = Query(None, description="Fecha final para filtrar"),
    skip: int = Query(
        0, ge=0, description="Número de registros a omitir (para paginación)"
    ),
    limit: int = Query(
        100, ge=1, le=100, description="Número máximo de registros a devolver"
    ),
    evaluation_service: PracticeEvaluationService = Depends(),
):
    """
    Lista evaluaciones con opciones avanzadas de filtrado y paginación.

    Este endpoint permite recuperar múltiples evaluaciones de práctica aplicando
    diversos criterios de filtrado como sesión, tirador, evaluador, rango de puntuación,
    clasificación, o rango de fechas. Los resultados se devuelven paginados.

    Parámetros:
        session_id: Opcional - Filtrar por sesión específica
        shooter_id: Opcional - Filtrar por tirador específico
        evaluator_id: Opcional - Filtrar por evaluador específico
        min_score: Opcional - Puntuación mínima (0-100)
        max_score: Opcional - Puntuación máxima (0-100)
        classification: Opcional - Filtrar por clasificación (TE, TC, TM, TR)
        start_date: Opcional - Fecha de inicio para filtrar
        end_date: Opcional - Fecha final para filtrar
        skip: Número de registros a omitir (para paginación)
        limit: Número máximo de registros a devolver
        evaluation_service: Servicio de evaluaciones (inyectado)

    Retorna:
        Lista paginada de evaluaciones con información de paginación

    Códigos de estado:
        200: Operación exitosa
    """
    filter_params = PracticeEvaluationFilter(
        session_id=session_id,
        shooter_id=shooter_id,
        evaluator_id=evaluator_id,
        min_score=min_score,
        max_score=max_score,
        classification=classification,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

    return evaluation_service.get_all_evaluations(filter_params)


@router.put("/", response_model=PracticeEvaluationRead)
async def update_evaluation(
    evaluation_data: PracticeEvaluationUpdate,
    evaluation_id: UUID = Path(..., description="ID de la evaluación a actualizar"),
    evaluation_service: PracticeEvaluationService = Depends(),
):
    """
    Actualiza una evaluación de práctica existente.

    Este endpoint permite modificar los datos de una evaluación de práctica de tiro.
    Se pueden actualizar calificaciones, comentarios, identificación de zonas problemáticas
    y otros aspectos de la evaluación.

    La actualización automáticamente:
    - Recalcula estadísticas del tirador si es necesario
    - Puede contribuir a cambios en la clasificación del tirador

    Parámetros:
        evaluation_data: Datos a actualizar
        evaluation_id: UUID de la evaluación a actualizar
        evaluation_service: Servicio de evaluaciones (inyectado)

    Retorna:
        La evaluación actualizada

    Códigos de estado:
        200: Evaluación actualizada exitosamente
        400: Datos de entrada inválidos
        404: Evaluación o evaluador no encontrado
    """
    evaluation, error = evaluation_service.update_evaluation(
        evaluation_id, evaluation_data
    )

    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error in ["PRACTICE_EVALUATION_NOT_FOUND", "EVALUATOR_NOT_FOUND"]:
            status_code = status.HTTP_404_NOT_FOUND

        raise HTTPException(status_code=status_code, detail=error)

    return evaluation


@router.delete("/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evaluation(
    evaluation_id: UUID = Path(..., description="ID de la evaluación a eliminar"),
    evaluation_service: PracticeEvaluationService = Depends(),
):
    """
    Elimina una evaluación de práctica.

    Este endpoint permite eliminar permanentemente una evaluación de práctica de tiro.
    Al eliminar una evaluación, la sesión asociada vuelve a estado "pendiente de evaluación"
    y las estadísticas del tirador se recalculan.

    Parámetros:
        evaluation_id: UUID de la evaluación a eliminar
        evaluation_service: Servicio de evaluaciones (inyectado)

    Retorna:
        204 No Content en caso de éxito

    Códigos de estado:
        204: Evaluación eliminada exitosamente
        404: Evaluación no encontrada
        400: Error en la eliminación
    """
    success, error = evaluation_service.delete_evaluation(evaluation_id)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error == "PRACTICE_EVALUATION_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND

        raise HTTPException(status_code=status_code, detail=error)


@router.get(
    "/shooter/{shooter_id}/statistics", response_model=ShooterEvaluationStatistics
)
async def get_shooter_statistics(
    shooter_id: UUID = Path(
        ..., description="ID del tirador para obtener estadísticas"
    ),
    evaluation_service: PracticeEvaluationService = Depends(),
):
    """
    Obtiene estadísticas completas de evaluaciones para un tirador.

    Este endpoint proporciona un análisis detallado del historial de evaluaciones
    de un tirador, incluyendo:
    - Puntuación media
    - Distribución de clasificaciones
    - Tendencia reciente (mejorando, empeorando o estable)
    - Calificaciones promedio por categoría (postura, agarre, etc.)
    - Zonas problemáticas comunes
    - Recomendación de cambio de clasificación si corresponde
    - Últimas evaluaciones

    Es útil para análisis de rendimiento a largo plazo y para identificar
    áreas de mejora prioritarias.

    Parámetros:
        shooter_id: UUID del tirador
        evaluation_service: Servicio de evaluaciones (inyectado)

    Retorna:
        Estadísticas detalladas sobre las evaluaciones del tirador

    Códigos de estado:
        200: Operación exitosa
        404: Tirador no encontrado o sin evaluaciones
    """
    statistics, error = evaluation_service.get_shooter_evaluation_statistics(shooter_id)

    if error:
        status_code = status.HTTP_404_NOT_FOUND

        if error == "NO_EVALUATIONS_FOUND":
            status_code = status.HTTP_404_NOT_FOUND

        raise HTTPException(status_code=status_code, detail=error)

    return statistics


@router.get("/shooter/{shooter_id}/rating/{category}", response_model=RatingAnalysis)
async def get_rating_analysis(
    category: str = Path(
        ...,
        description="Categoría a analizar: 'posture', 'grip', 'sight_alignment', 'trigger_control', 'breathing'",
    ),
    shooter_id: UUID = Path(..., description="ID del tirador"),
    evaluation_service: PracticeEvaluationService = Depends(),
):
    """
    Obtiene análisis detallado de una categoría específica de evaluación.

    Este endpoint proporciona un análisis específico para una categoría particular
    de la evaluación (postura, agarre, alineación visual, control del gatillo, respiración).

    El análisis incluye:
    - Promedio histórico para la categoría
    - Tendencia (mejorando, empeorando o estable)
    - Sugerencias de mejora personalizadas

    Es útil para concentrarse en el desarrollo de habilidades específicas
    y para seguir el progreso en aspectos particulares de la técnica de tiro.

    Parámetros:
        category: Categoría a analizar ('posture', 'grip', 'sight_alignment', 'trigger_control', 'breathing')
        shooter_id: UUID del tirador
        evaluation_service: Servicio de evaluaciones (inyectado)

    Retorna:
        Análisis detallado para la categoría solicitada

    Códigos de estado:
        200: Operación exitosa
        400: Categoría inválida
        404: Tirador no encontrado o sin datos para la categoría
    """
    analysis, error = evaluation_service.get_rating_analysis(shooter_id, category)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error == "SHOOTER_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        elif error.startswith("NO_DATA_FOR_CATEGORY"):
            status_code = status.HTTP_404_NOT_FOUND
        elif error.startswith("INVALID_CATEGORY"):
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(status_code=status_code, detail=error)

    return analysis
