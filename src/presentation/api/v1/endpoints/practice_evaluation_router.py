from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional

from src.application.services.practice_evaluation_service import PracticeEvaluationService
from src.domain.enums.role_enum import RoleEnum
from src.domain.enums.classification_enum import ShooterLevelEnum
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.practice_evaluation_schema import (
    PracticeEvaluationCreate,
    PracticeEvaluationRead,
    PracticeEvaluationUpdate
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
    current_user: dict = Depends(get_current_user)
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
        raise HTTPException(
            status_code=status_code,
            detail=error
        )
    return evaluation
