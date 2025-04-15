from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional
from uuid import UUID

from src.application.services.practice_type_service import ExerciseTypeService
from src.presentation.schemas.exercise_type_schema import (
    ExerciseTypeCreate,
    ExerciseTypeUpdate,
    ExerciseTypeDetail,
    ExerciseTypeList,
    ExerciseTypeFilter,
    ExerciseTypeRead,
)
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.user_schemas import UserRead
from src.domain.enums.role_enum import RoleEnum

router = APIRouter(
    prefix="/exercises/types",
    tags=["exercise-types"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ExerciseTypeRead, status_code=status.HTTP_201_CREATED)
async def create_exercise_type(
    exercise_type_data: ExerciseTypeCreate,
    service: ExerciseTypeService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    '''
    Crear un nuevo tipo de ejercicio.
    Args:
        exercise_type_data (ExerciseTypeCreate): Datos del tipo de ejercicio a crear.
        current_user (dict): Usuario actual obtenido del token JWT.
    '''
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para crear tipos de ejercicio")

    exercise_type, error = service.create_exercise_type(exercise_type_data)
    if error:
        status_code = status.HTTP_400_BAD_REQUEST
        if error == "EXERCISE_TYPE_NAME_ALREADY_EXISTS":
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=error)

    return exercise_type
