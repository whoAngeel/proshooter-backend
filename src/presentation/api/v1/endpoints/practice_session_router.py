from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from src.application.services.practice_session_service import PracticeSessionService
from src.infraestructure.auth.jwt_config import get_current_user
from src.domain.enums.role_enum import RoleEnum
from src.presentation.schemas.practice_session_schema import (
    IndividualPracticeSessionCreate,
    IndividualPracticeSessionRead,
    IndividualPracticeSessionUpdate,
    IndividualPracticeSessionDetail,
    IndividualPracticeSessionList,
    IndividualPracticeSessionStatistics
)

router = APIRouter(
    prefix="/practice-sessions",
    tags=["Practice Sessions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=IndividualPracticeSessionRead, status_code=status.HTTP_201_CREATED)
# @router.post("/",  status_code=status.HTTP_201_CREATED)
async def create_practice_session(
    session_data: IndividualPracticeSessionCreate,
    service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    '''
    Crea una nueva sesion de practica individual

    Este endpoint permite la creacion de una nueva sesion de practica de tiro para un tirador especifico
    Requiere informacion como el id del tirador, fecha, ubicacion, estadisticas y estadisticas de tiro.

    El sistema calcula automaticamente el porcentaje de precision basado en la relacion entre aciertos y disparos totales.

    Params:
        session_data: Datos para la nueva sesion de practica

    Returns:
        La sesion de practica creada

    Status Code:
        201: Sesión creada exitosamente
        400: Datos de entrada inválidos
        404: Tirador o instructor no encontrado

    '''
    current_user_id = current_user.id

    if current_user.role != RoleEnum.TIRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Solo los tiradores pueden crear sesiones de practica. Tu rol actual es: {current_user.role}"
        )

    session, error = service.create_session(session_data, current_user_id)
    if error:
        status_code = status.HTTP_400_BAD_REQUEST
        if error == "SHOOTER_NOT_FOUND" or error == "INSTRUCTOR_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status_code,
            detail=error
        )
    return session

# @router.get("/{session_id}" )
@router.get("/{session_id}", response_model=IndividualPracticeSessionDetail)
async def get_practice_session(
    session_id: UUID = Path(..., description="ID de la sesión de práctica a obtener"),
    session_service: PracticeSessionService = Depends()
):
    """
    Obtiene los detalles de una sesión de práctica específica.

    Recupera información detallada sobre una sesión de práctica, incluyendo datos del tirador,
    instructor, ejercicios realizados y evaluación asociada si existe.

    Parámetros:
        session_id: UUID de la sesión de práctica a obtener
        session_service: Servicio para gestionar sesiones de práctica (inyectado)

    Retorna:
        Información detallada de la sesión de práctica solicitada

    Códigos de estado:
        200: Operación exitosa
        404: Sesión de práctica no encontrada
    """
    session, error = session_service.get_session_by_id(session_id)

    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )

    return session
