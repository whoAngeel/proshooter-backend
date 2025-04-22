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
    IndividualPracticeSessionStatistics,
    IndividualPracticeSessionFilter
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


@router.get("/recent", response_model=List[IndividualPracticeSessionRead])
async def get_recent_sessions(
    shooter_id: Optional[UUID] = Query(None, description="Filtrar por ID del tirador"),
    limit: int = Query(5, ge=1, le=20, description="Número máximo de sesiones a devolver"),
    session_service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene las sesiones de práctica más recientes.

    Este endpoint recupera las sesiones de práctica más recientes, opcionalmente filtradas
    por un tirador específico. Es útil para paneles de control o para mostrar actividad reciente.

    Parámetros:
        shooter_id: Opcional - Filtrar por tirador específico
        limit: Número máximo de sesiones a devolver (entre 1 y 20)
        session_service: Servicio para gestionar sesiones de práctica (inyectado)

    Retorna:
        Lista de las sesiones de práctica más recientes
    """
    return session_service.get_recent_sessions(shooter_id, limit)


# @router.get("/{session_id}" )
@router.get("/{session_id}", response_model=IndividualPracticeSessionDetail)
async def get_practice_session(
    session_id: UUID = Path(..., description="ID de la sesión de práctica a obtener"),
    session_service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user)
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

@router.get("/", response_model=IndividualPracticeSessionList)
async def list_practice_sessions(
    shooter_id: Optional[UUID] = Query(None, description="Filtrar por ID del tirador"),
    instructor_id: Optional[UUID] = Query(None, description="Filtrar por ID del instructor"),
    location: Optional[str] = Query(None, description="Filtrar por ubicación"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio para filtrar"),
    end_date: Optional[datetime] = Query(None, description="Fecha final para filtrar"),
    min_accuracy: Optional[float] = Query(None, ge=0, le=100, description="Precisión mínima"),
    max_accuracy: Optional[float] = Query(None, ge=0, le=100, description="Precisión máxima"),
    search: Optional[str] = Query(None, description="Término de búsqueda en ubicación o nombre del tirador"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir (para paginación)"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a devolver"),
    session_service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista sesiones de práctica con opciones de filtrado y paginación.

    Este endpoint permite recuperar múltiples sesiones de práctica con diversas opciones
    de filtrado como tirador, instructor, ubicación, rango de fechas, rango de precisión
    o búsqueda por texto. Los resultados se devuelven paginados.

    Parámetros:
        shooter_id: Opcional - Filtrar por tirador específico
        instructor_id: Opcional - Filtrar por instructor específico
        location: Opcional - Filtrar por ubicación (búsqueda parcial)
        start_date: Opcional - Fecha de inicio para filtrar
        end_date: Opcional - Fecha final para filtrar
        min_accuracy: Opcional - Precisión mínima (0-100)
        max_accuracy: Opcional - Precisión máxima (0-100)
        search: Opcional - Término de búsqueda general
        skip: Número de registros a omitir (para paginación)
        limit: Número máximo de registros a devolver
        session_service: Servicio para gestionar sesiones de práctica (inyectado)

    Retorna:
        Lista paginada de sesiones de práctica con información de paginación

    Notas:
        - Si se especifican múltiples filtros, se aplicará el siguiente orden de prioridad:
          1. Búsqueda general (search)
          2. Tirador específico (shooter_id)
          3. Instructor específico (instructor_id)
          4. Ubicación (location)
          5. Rango de fechas (start_date y end_date)
          6. Rango de precisión (min_accuracy y max_accuracy)
    """
    # Construir objeto de filtro con todos los parámetros
    filter_params = IndividualPracticeSessionFilter(
        shooter_id=shooter_id,
        instructor_id=instructor_id,
        location=location,
        start_date=start_date,
        end_date=end_date,
        min_accuracy=min_accuracy,
        max_accuracy=max_accuracy,
        search=search,
        skip=skip,
        limit=limit
    )
    # TODO: Testear cuando haya mas datos
    return session_service.get_all_sessions(filter_params)

@router.put("/{session_id}", response_model=IndividualPracticeSessionRead)
async def update_practice_session(
    session_data: IndividualPracticeSessionUpdate,
    session_id: UUID = Path(..., description="ID de la sesión de práctica a actualizar"),
    service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza una sesión de práctica existente.

    Este endpoint permite modificar los datos de una sesión de práctica ya existente.
    Se pueden actualizar campos como la fecha, ubicación, instructor, o estadísticas de disparos.

    Si se actualizan los disparos o aciertos, el sistema recalculará automáticamente el porcentaje de precisión.

    Parámetros:
        session_data: Datos a actualizar en la sesión de práctica
        session_id: UUID de la sesión de práctica a actualizar
        session_service: Servicio para gestionar sesiones de práctica (inyectado)

    Retorna:
        La sesión de práctica actualizada

    Códigos de estado:
        200: Sesión actualizada exitosamente
        400: Datos de entrada inválidos
        404: Sesión de práctica o instructor no encontrado
    """

    # TODO validar quien puede actualizar la sesion

    session, error = service.update_session(session_id, session_data)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST
        if error == "PRACTICE_SESSION_NOT_FOUND" or error == "INSTRUCTOR_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return session

@router.delete('/{session_id}')
async def delete_practice_session(
    session_id: UUID = Path(..., description="ID de la sesion de practica"),
    service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina una sesión de práctica.

    Este endpoint permite eliminar permanentemente una sesión de práctica y todos
    sus datos asociados, como ejercicios y evaluaciones.

    Parámetros:
        session_id: UUID de la sesión de práctica a eliminar
        session_service: Servicio para gestionar sesiones de práctica (inyectado)

    Retorna:
        204 No Content en caso de éxito

    Códigos de estado:
        204: Sesión eliminada exitosamente
        404: Sesión de práctica no encontrada
        400: Error en la eliminación
    """
    if current_user.role != RoleEnum.ADMIN:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden realizar esta acción"
        )

    success, error = service.delete_session(session_id)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST
        if error == "PRACTICE_SESSION_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return {"detail": f"{f"{session_id} deleted successfully" if success else "Error deleting session"}"}

@router.get("/shooter/{shooter_id}/statistics", response_model=IndividualPracticeSessionStatistics)
async def get_shooter_statistics(
    shooter_id: UUID = Path(..., description="ID del tirador para obtener estadísticas"),
    period: Optional[str] = Query(None, description="Período para las estadísticas (week, month, year)"),
    session_service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene estadísticas de sesiones de práctica para un tirador específico.

    Este endpoint proporciona información estadística agregada sobre las sesiones de práctica
    de un tirador, como el total de sesiones, promedio de precisión, total de disparos, total de aciertos,
    y las ubicaciones más frecuentes donde se realizaron las prácticas.

    Opcionalmente, se pueden filtrar las estadísticas por un período específico.

    Parámetros:
        shooter_id: UUID del tirador para obtener estadísticas
        period: Opcional - Período para las estadísticas ("week", "month", "year" o None para todo el tiempo)
        session_service: Servicio para gestionar sesiones de práctica (inyectado)

    Retorna:
        Estadísticas de las sesiones de práctica del tirador

    Códigos de estado:
        200: Operación exitosa
        404: Tirador no encontrado
        400: Período inválido o error en el procesamiento de estadísticas
    """
    stats, error = session_service.get_shooter_statistics(shooter_id, period)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error == "SHOOTER_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        elif error == "INVALID_PERIOD":
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return stats
