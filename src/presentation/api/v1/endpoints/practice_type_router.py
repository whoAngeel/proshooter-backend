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
    current_user: dict = Depends(get_current_user),
):
    """
    Crear un nuevo tipo de ejercicio.
    Args:
        exercise_type_data (ExerciseTypeCreate): Datos del tipo de ejercicio a crear.
        current_user (dict): Usuario actual obtenido del token JWT.
    Returns:
        Tipo de ejercicio creado
    Raises:
        HTTPException: si hay un error l crear el tipo de ejercicio
    """
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear tipos de ejercicio",
        )

    exercise_type, error = service.create_exercise_type(exercise_type_data)
    if error:
        status_code = status.HTTP_400_BAD_REQUEST
        if error == "EXERCISE_TYPE_NAME_ALREADY_EXISTS":
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=error)

    return exercise_type


@router.get("/{exercise_type_id}", response_model=ExerciseTypeDetail)
async def get_exercise_type(
    exercise_type_id: UUID = Path(..., description="ID del tipo de ejercicio"),
    service: ExerciseTypeService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtener un tipo de ejercicio por su ID.
    Args:
        exercise_type_id (UUID): ID del tipo de ejercicio a obtener.
        current_user (dict): Usuario actual obtenido del token JWT.
    Returns:
        Detalle del tipo de ejercicio obtenido
    Raises:
        HTTPException: si hay un error al obtener el tipo de ejercicio
    """

    exercise_type, error = service.get_exercise_type_detail(exercise_type_id)

    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    return exercise_type


@router.get("/", response_model=ExerciseTypeList)
async def list_exercise_types(
    search: Optional[str] = Query(
        None, description="Término de búsqueda en nombre o descripcion"
    ),
    difficulty: Optional[int] = Query(
        None, description="Filtrar por nivel de dificultad"
    ),
    active_only: bool = Query(
        True, description="Mostrar solo los tipos de ejercicio activos"
    ),
    skip: int = Query(0, description="Numero de registros a omitir"),
    limit: int = Query(100, description="Numero Maximo de registros a devolver"),
    service: ExerciseTypeService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Listar tipos de ejercicio.
    Args:
        search (Optional[str]): Término de búsqueda en nombre o descripcion.
        difficulty (Optional[int]): Nivel de dificultad.
        active_only (bool): Mostrar solo los tipos de ejercicio activos.
        skip (int): Numero de registros a omitir.
        limit (int): Numero Maximo de registros a devolver.
        current_user (dict): Usuario actual obtenido del token JWT.
    Returns:
        Lista todos los tipos de ejercicio con opciones de filtrado y paginación.
    Raises:
        HTTPException: si hay un error al listar los tipos de ejercicio
    """
    filter_params = ExerciseTypeFilter(
        search=search,
        difficulty=difficulty,
        active_only=active_only,
        skip=skip,
        limit=limit,
    )
    return service.get_all_exercise_types(filter_params)


@router.put("/{exercise_type_id}", response_model=ExerciseTypeRead)
async def update_exercise_type(
    exercise_type_data: ExerciseTypeUpdate,
    exercise_type_id: UUID = Path(
        ..., description="ID del tipo de ejercicio a actualizar"
    ),
    service: ExerciseTypeService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Actualizar un tipo de ejercicio.
    Args:
        exercise_type_data (ExerciseTypeUpdate): Datos a actualizar.
        exercise_type_id (UUID): ID del tipo de ejercicio a actualizar.
        current_user (dict): Usuario actual obtenido del token JWT.
    Returns:
        Tipo de ejercicio actualizado
    Raises:
        HTTPException: si hay un error al actualizar el tipo de ejercicio
    """
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar tipos de ejercicio",
        )

    exercise_type, error = service.update_exercise_type(
        exercise_type_id, exercise_type_data
    )

    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error == "EXERCISE_TYPE_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        elif error == "EXERCISE_TYPE_NAME_ALREADY_EXISTS":
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=error)
    return exercise_type


@router.delete("/{exercise_type_id}")
async def delete_exercise_type(
    exercise_type_id: UUID = Path(
        ..., description="ID del tipo de ejercicio a eliminar"
    ),
    service: ExerciseTypeService = Depends(),
    soft_delete: bool = Query(
        True,
        description="Indica si se debe eliminar logicamente o no el tipo de ejercicio",
    ),
    current_user: dict = Depends(get_current_user),
):
    """
    Eliminar un tipo de ejercicio.
    Args:
        exercise_type_id (UUID): ID del tipo de ejercicio a eliminar.
        current_user (dict): Usuario actual obtenido del token JWT.
    Returns:
        Detalle del tipo de ejercicio eliminado
    Raises:
        HTTPException: si hay un error al eliminar el tipo de ejercicio
    """
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar tipos de ejercicio",
        )

    delete_result, error = service.delete_exercise_type(exercise_type_id, soft_delete)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST
        if error == "EXERCISE_TYPE_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        elif error == "CANNOT_DELETE_EXERCISE_TYPE_WITH_ASSOCIATED_EXERCISES":
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=error)

    return {
        "detail": f"Eliminado {'exitoso' if delete_result else 'fallido'}",
        "soft_delete": soft_delete,
        "exercise_type_id": exercise_type_id,
    }


@router.get("/{exercise_type_id}/exercises")
async def get_exercises_by_type(
    exercise_type_id: UUID = Path(..., description="ID del tipo de ejercicio"),
    service: ExerciseTypeService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    exercices, error = service.get_exercises_by_type(exercise_type_id)

    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    return exercices
