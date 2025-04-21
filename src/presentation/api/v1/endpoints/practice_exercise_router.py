from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.application.services.practice_exercise_service import PracticeExerciseService
from src.infraestructure.auth.jwt_config import get_current_user
from src.domain.enums.role_enum import RoleEnum
from src.presentation.schemas.practice_exercise_schema import (
    PracticeExerciseCreate,
    PracticeExerciseRead,
    PracticeExerciseDetail,
    PracticeExerciseUpdate,
    PracticeExerciseList,
    PracticeExerciseStatistics,
    PracticeExerciseFilter,
    PerformanceAnalysis
)

router = APIRouter(
    prefix="/practice-exercises",
    tags=["Practice Exercises"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=PracticeExerciseRead, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    exercise_data: PracticeExerciseCreate,
    service: PracticeExerciseService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Crea un nuevo ejercicio de práctica de tiro.

    Este endpoint permite registrar un ejercicio específico realizado durante una sesión de práctica.
    El ejercicio incluye detalles como el tipo de ejercicio, arma, munición, blanco utilizado y
    estadísticas de precisión.

    El sistema verifica automáticamente:
    - Que la sesión de práctica existe
    - Que el tipo de ejercicio, arma, munición y blanco existen
    - Que el arma y la munición son compatibles
    - Que el número de aciertos no supera la munición utilizada

    Además, actualiza automáticamente los totales de la sesión a la que pertenece.

    Parámetros:
        exercise_data: Datos del ejercicio a crear
        exercise_service: Servicio para gestionar ejercicios (inyectado)

    Retorna:
        El ejercicio de práctica creado con su ID y campos calculados

    Códigos de estado:
        201: Ejercicio creado exitosamente
        400: Datos de entrada inválidos
        404: Entidad relacionada no encontrada (sesión, tipo de ejercicio, etc.)
        409: Arma y munición no compatibles
    """
    exercise, error = service.create_exercise(exercise_data)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST
        if error in [
            "PRACTICE_SESSION_NOT_FOUND",
            "EXERCISE_TYPE_NOT_FOUND",
            "WEAPON_NOT_FOUND",
            "TARGET_NOT_FOUND",
            "AMMUNITION_NOT_FOUND",
        ]:
            status_code = status.HTTP_404_NOT_FOUND
        elif error == "WEAPON_AMMUNITION_NOT_COMPATIBLE":
            status_code = status.HTTP_409_CONFLICT

        raise HTTPException(status_code=status_code, detail=error)

    return exercise
