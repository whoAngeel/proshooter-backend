from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.application.services.practice_session_service import PracticeSessionService
from src.infraestructure.auth.jwt_config import get_current_user
from src.infraestructure.database.session import get_db
from src.domain.enums.role_enum import RoleEnum
from src.presentation.schemas.practice_session_schema import (
    IndividualPracticeSessionCreate,
    IndividualPracticeSessionRead,
    IndividualPracticeSessionUpdate,
    IndividualPracticeSessionDetail,
    IndividualPracticeSessionList,
    IndividualPracticeSessionStatistics,
    IndividualPracticeSessionFilter,
)
from src.application.services.finalize_session import SessionFinalizationService
from src.presentation.schemas.sesion_finalization import (
    FinishSessionRequest,
    FinishSessionResponse,
    SessionStatusResponse,
    ReopenSessionRequest,
    ReopenSessionResponse,
)
from src.presentation.schemas.instructor import PracticeSessionCreateRequest

router = APIRouter(
    prefix="/practice-sessions",
    tags=["Practice Sessions"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
# @router.post("/",  status_code=status.HTTP_201_CREATED)
async def create_practice_session(
    session_data: PracticeSessionCreateRequest,
    service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
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

    """
    try:
        shotoer_id = current_user.id

        session, error = service.create_session(session_data, shotoer_id)
        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": True,
            "session_id": str(session.id),
            "instructor_assigned": session.instructor_id is not None,
            "can_be_evaluated": session.instructor_id is not None,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}",
        )


@router.get("/recent", response_model=List[IndividualPracticeSessionRead])
async def get_recent_sessions(
    shooter_id: Optional[UUID] = Query(None, description="Filtrar por ID del tirador"),
    limit: int = Query(
        5, ge=1, le=20, description="Número máximo de sesiones a devolver"
    ),
    session_service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(get_current_user),
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
    try:
        session, error = session_service.get_session_by_id(session_id)

        if error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)

        return session
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=IndividualPracticeSessionList)
async def list_practice_sessions(
    shooter_id: Optional[UUID] = Query(None, description="Filtrar por ID del tirador"),
    instructor_id: Optional[UUID] = Query(
        None, description="Filtrar por ID del instructor"
    ),
    location: Optional[str] = Query(None, description="Filtrar por ubicación"),
    start_date: Optional[datetime] = Query(
        None, description="Fecha de inicio para filtrar"
    ),
    end_date: Optional[datetime] = Query(None, description="Fecha final para filtrar"),
    min_accuracy: Optional[float] = Query(
        None, ge=0, le=100, description="Precisión mínima"
    ),
    max_accuracy: Optional[float] = Query(
        None, ge=0, le=100, description="Precisión máxima"
    ),
    search: Optional[str] = Query(
        None, description="Término de búsqueda en ubicación o nombre del tirador"
    ),
    skip: int = Query(
        0, ge=0, description="Número de registros a omitir (para paginación)"
    ),
    limit: int = Query(
        100, ge=1, le=100, description="Número máximo de registros a devolver"
    ),
    session_service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user),
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
        limit=limit,
    )
    # TODO: Testear cuando haya mas datos
    return session_service.get_all_sessions(filter_params)


@router.put("/{session_id}", response_model=IndividualPracticeSessionRead)
async def update_practice_session(
    session_data: IndividualPracticeSessionUpdate,
    session_id: UUID = Path(
        ..., description="ID de la sesión de práctica a actualizar"
    ),
    service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user),
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
        raise HTTPException(status_code=status_code, detail=error)

    return session


@router.delete("/{session_id}")
async def delete_practice_session(
    session_id: UUID = Path(..., description="ID de la sesion de practica"),
    service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user),
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
            detail="Solo los administradores pueden realizar esta acción",
        )

    success, error = service.delete_session(session_id)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST
        if error == "PRACTICE_SESSION_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status_code, detail=error)

    return {
        "detail": (
            f"{session_id} deleted successfully"
            if success
            else "Error deleting session"
        )
    }


@router.get(
    "/shooter/{shooter_id}/statistics",
    response_model=IndividualPracticeSessionStatistics,
)
async def get_shooter_statistics(
    shooter_id: UUID = Path(
        ..., description="ID del tirador para obtener estadísticas"
    ),
    period: Optional[str] = Query(
        None, description="Período para las estadísticas (week, month, year)"
    ),
    session_service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user),
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

        raise HTTPException(status_code=status_code, detail=error)

    return stats


@router.post("/{session_id}/finish/", response_model=FinishSessionResponse)
async def finish_practice_session(
    request: FinishSessionRequest,
    session_id: UUID = Path(..., description="ID de la sesión de práctica a finalizar"),
    service: SessionFinalizationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Finaliza una sesión de práctica
    - Consolida todos los ejercicios
    - Valida que esté lista para finalizar
    - Marca como terminada y lista para evaluación
    """
    try:
        shooter_id = current_user.id

        result = service.finish_session(session_id, shooter_id)

        return FinishSessionResponse(
            success=True,
            data=result,
        )
    except HTTPException as e:
        return FinishSessionResponse(
            success=False,
            error=str(e.detail),
        )

    except Exception as e:
        return FinishSessionResponse(
            success=False,
            error=f"Error interno: {str(e)}",
        )


@router.get("/{session_id}/status/", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: UUID = Path(..., description="ID de la sesión de práctica"),
    service: SessionFinalizationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene el estado actual de una sesión
    - Si puede finalizarse
    - Si puede modificarse
    - Qué le falta para estar completa
    """
    try:
        status = service.get_session_status(session_id)

        if "error" in status:
            return SessionStatusResponse(
                success=False,
                error=status["error"],
            )
        return SessionStatusResponse(
            success=True,
            data=status,
        )
    except HTTPException as e:
        return SessionStatusResponse(
            success=False,
            error=str(e.detail),
        )


@router.get("/{session_id}/validate-completion/")
async def validate_session_for_completion(
    session_id: UUID = Path(..., description="ID de la sesión de práctica"),
    service: SessionFinalizationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Valida si una sesión puede finalizarse
    Útil para mostrar warnings ANTES de intentar finalizar
    """
    try:
        validation = service.validate_session_for_completion(session_id)

        return {
            "can_finish": validation.can_finish,
            "reason": validation.reason,
            "missing_requirements": validation.missing_requirements,
            "exercises_count": validation.exercises_count,
            "exercises_with_images": validation.exercises_with_images,
            "exercises_needing_analysis": validation.exercises_needing_analysis,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/reopen/")
async def reopen_practice_session(
    request: ReopenSessionRequest,
    session_id: UUID = Path(..., description="ID de la sesión de práctica a reabrir"),
    service: SessionFinalizationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Reabre una sesión de práctica finalizada
    Permite volver a modificarla si es necesario
    """
    try:
        if not request.confirmation:
            raise HTTPException(
                status_code=400, detail="Debe confirmar que desea reabrir la sesión"
            )

        shooter_id = current_user.shooter.user_id

        result = service.reopen_session(session_id, shooter_id)

        return ReopenSessionResponse(**result)
    except HTTPException as e:
        return ReopenSessionResponse(
            success=False, message=e.detail, session_id=session_id, can_modify=False
        )
    except Exception as e:
        return ReopenSessionResponse(
            success=False,
            message=f"Error interno: {str(e)}",
            session_id=session_id,
            can_modify=False,
        )


@router.get("/{session_id}/can-modify/")
async def can_modify_session(
    session_id: UUID = Path(..., description="ID de la sesión de práctica"),
    service: SessionFinalizationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Verifica rápidamente si una sesión puede modificarse
    Útil para habilitar/deshabilitar botones en el frontend
    """
    try:
        can_modify = service.can_modify_session(session_id)

        return {
            "session_id": str(session_id),
            "can_modify": can_modify,
            "message": (
                "Puede modificarse"
                if can_modify
                else "Sesión finalizada - no se puede modificar"
            ),
        }
    except Exception as e:
        return {"session_id": str(session_id), "can_modify": False, "error": str(e)}


@router.get("/exercise/{exercise_id}/can-modify/")
async def can_modify_exercise(
    exercise_id: UUID = Path(..., description="ID del ejercicio de práctica"),
    # service: SessionFinalizationService = Depends(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Verifica si un ejercicio de práctica puede modificarse
    Útil para habilitar/deshabilitar botones en el frontend
    """
    try:
        # from utils.session_protection import validate_exercise_modification_allowed
        from src.infraestructure.utils.session_protection import (
            validate_exercise_modification_allowed,
        )

        validate_exercise_modification_allowed(db, exercise_id)

        return {
            "exercise_id": str(exercise_id),
            "can_modify": True,
            "message": "Ejercicio puede modificarse",
        }
    except HTTPException as e:
        return {
            "exercise_id": str(exercise_id),
            "can_modify": False,
            "message": e.detail,
        }


@router.get("/{session_id}/details")
async def get_session_with_instructor_details(
    session_id: UUID,
    service: PracticeSessionService = Depends(),
    current_user=Depends(get_current_user),
):
    """
    Obtiene detalles de sesión incluyendo información del instructor
    """

    session_details = service.get_session_with_instructor_info(session_id)

    if not session_details:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    return session_details


@router.patch("/{session_id}/instructor")
async def update_session_instructor(
    session_id: UUID,
    instructor_id: UUID = Query(
        None, description="Id del instructor"
    ),  # None para remover instructor
    service: PracticeSessionService = Depends(),
    current_user=Depends(get_current_user),
):
    """
    Actualiza el instructor asignado a una sesión
    Solo si la sesión no está finalizada
    """
    try:
        shooter_id = current_user.shooter.user_id

        success, error = service.update_session_instructor(
            session_id, instructor_id, shooter_id
        )

        if not success:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": True,
            "message": "Instructor actualizado correctamente",
            "instructor_id": str(instructor_id) if instructor_id else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
