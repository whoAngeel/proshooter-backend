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
    PracticeExerciseList,
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
        service: Servicio para gestionar ejercicios (inyectado)

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


@router.get("/statistics", response_model=PracticeExerciseStatistics)
async def get_exercise_statistics(
    shooter_id: Optional[UUID] = Query(None, description="ID del tirador para filtrar estadísticas"),
    service: PracticeExerciseService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene estadísticas agregadas de ejercicios de práctica.

    Este endpoint proporciona estadísticas detalladas sobre ejercicios de práctica,
    opcionalmente filtradas por tirador. Incluye:
    - Total de ejercicios realizados
    - Precisión promedio
    - Total de munición utilizada y aciertos
    - Tiempo de reacción promedio
    - Estadísticas por distancia, tipo de ejercicio y arma

    Es útil para análisis de rendimiento y mejora continua.

    Parámetros:
        shooter_id: Opcional - ID del tirador para filtrar estadísticas
        service: Servicio para gestionar ejercicios (inyectado)

    Retorna:
        Estadísticas agregadas de ejercicios de práctica

    Códigos de estado:
        200: Operación exitosa
        404: Tirador no encontrado
        400: Error en el procesamiento de estadísticas
    """
    stats, error = service.get_exercise_statistics(shooter_id)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error == "SHOOTER_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return stats

@router.get("/{exercise_id}", response_model=PracticeExerciseDetail)
async def get_exercise(
    exercise_id: UUID = Path(..., description="ID del ejercicio de práctica a obtener"),
    service: PracticeExerciseService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene los detalles de un ejercicio de práctica específico.

    Este endpoint devuelve información completa sobre un ejercicio de práctica, incluyendo
    datos de sus entidades relacionadas (tipo de ejercicio, blanco, arma, munición y sesión).

    Parámetros:
        exercise_id: UUID del ejercicio a consultar
        service: Servicio para gestionar ejercicios (inyectado)

    Retorna:
        Información detallada del ejercicio de práctica

    Códigos de estado:
        200: Operación exitosa
        404: Ejercicio no encontrado
    """
    exercise, error = service.get_exercise_by_id(exercise_id)

    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )

    return exercise

@router.get('/', response_model=PracticeExerciseList)
async def get_exercises(
    session_id: Optional[UUID] = Query(None, description="ID de la sesión de práctica"),
    shooter_id: Optional[UUID] = Query(None, description="ID del tirador"),
    exercise_type_id: Optional[UUID] = Query(None, description="ID del tipo de ejercicio"),
    target_id: Optional[UUID] = Query(None, description="ID del blanco"),
    weapon_id: Optional[UUID] = Query(None, description="ID del arma"),
    ammunition_id: Optional[UUID] = Query(None, description="ID de la municion"),
    distance: Optional[str] = Query(None, description="Distancia en metros, ej. 15 metros"),
    min_accuracy: Optional[float] = Query(None, description="Precision minima"),
    max_accuracy: Optional[float] = Query(None, description="Precision maxima"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha final"),
    search: Optional[str] = Query(None, description="Termino de busqueda"),
    skip: int = Query(0, ge=0, description="Numero de registros a omitir (para la paginacion)"),
    limit: int = Query(100, ge=1, le=100, description="Numero maximo de registros a devolver"),
    service: PracticeExerciseService = Depends(),
    current_user: dict = Depends(get_current_user)
):

    """
    Lista ejercicios de práctica con opciones avanzadas de filtrado y paginación.

    Este endpoint permite recuperar ejercicios de práctica aplicando diversos criterios
    de filtrado como sesión, tirador, tipo de ejercicio, arma, rango de precisión, etc.
    Los resultados se devuelven paginados con información del total de registros.

    Parámetros:
        session_id: Opcional - Filtrar por sesión específica
        shooter_id: Opcional - Filtrar por tirador específico
        exercise_type_id: Opcional - Filtrar por tipo de ejercicio
        target_id: Opcional - Filtrar por tipo de blanco
        weapon_id: Opcional - Filtrar por arma específica
        ammunition_id: Opcional - Filtrar por munición específica
        distance: Opcional - Filtrar por distancia
        min_accuracy: Opcional - Precisión mínima (0-100)
        max_accuracy: Opcional - Precisión máxima (0-100)
        start_date: Opcional - Fecha de inicio para filtrar sesiones
        end_date: Opcional - Fecha final para filtrar sesiones
        search: Opcional - Término de búsqueda general
        skip: Número de registros a omitir (para paginación)
        limit: Número máximo de registros a devolver
        service: Servicio para gestionar ejercicios (inyectado)

    Retorna:
        Lista paginada de ejercicios con información de paginación

    Códigos de estado:
        200: Operación exitosa
    """
    filter_params = PracticeExerciseFilter(
        session_id=session_id,
        shooter_id=shooter_id,
        exercise_type_id=exercise_type_id,
        target_id=target_id,
        weapon_id=weapon_id,
        ammunition_id=ammunition_id,
        distance=distance,
        min_accuracy=min_accuracy,
        max_accuracy=max_accuracy,
        start_date=start_date,
        end_date=end_date,
        search=search,
        skip=skip,
        limit=limit
    )

    return service.get_all_exercises(filter_params)


@router.put('/{exercise_id}', response_model=PracticeExerciseRead)
async def update_exercise(
    exercise_data: PracticeExerciseUpdate,
    exercise_id: UUID,
    service: PracticeExerciseService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza un ejercicio de práctica existente.

    Este endpoint permite modificar los datos de un ejercicio de práctica,
    como tipo de ejercicio, arma, munición, blanco o estadísticas de disparos.

    El sistema verifica:
    - Que el ejercicio existe
    - Que las entidades relacionadas actualizadas existen
    - La compatibilidad entre arma y munición si se modifican
    - Que los aciertos no superen la munición utilizada

    Automáticamente recalcula el porcentaje de precisión y actualiza
    los totales de la sesión a la que pertenece el ejercicio.

    Parámetros:
        exercise_data: Datos a actualizar
        exercise_id: UUID del ejercicio a actualizar
        service: Servicio para gestionar ejercicios (inyectado)

    Retorna:
        El ejercicio actualizado

    Códigos de estado:
        200: Ejercicio actualizado exitosamente
        400: Datos de entrada inválidos
        404: Ejercicio o entidad relacionada no encontrada
        409: Arma y munición no compatibles
    """
    exercise, error = service.udpate_exercise(exercise_id, exercise_data)
    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error in [
            "PRACTICE_EXERCISE_NOT_FOUND",
            "EXERCISE_TYPE_NOT_FOUND",
            "TARGET_NOT_FOUND",
            "WEAPON_NOT_FOUND",
            "AMMUNITION_NOT_FOUND"
        ]:
            status_code = status.HTTP_404_NOT_FOUND
        elif error == "WEAPON_AMMUNITION_NOT_COMPATIBLE":
            status_code = status.HTTP_409_CONFLICT

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return exercise

@router.delete('/{exercise_id}')
async def delete_exercise(
    exercise_id: UUID = Path(..., description="ID del ejercicio de practica a eliminar"),
    service: PracticeExerciseService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina un ejercicio de práctica.

    Este endpoint permite eliminar permanentemente un ejercicio de práctica y sus datos asociados.
    Automáticamente actualiza los totales de la sesión a la que pertenecía el ejercicio.

    Parámetros:
        exercise_id: UUID del ejercicio a eliminar
        service: Servicio para gestionar ejercicios (inyectado)

    Retorna:
        204 No Content en caso de éxito

    Códigos de estado:
        204: Ejercicio eliminado exitosamente
        404: Ejercicio no encontrado
        400: Error en la eliminación
    """
    if current_user.role != RoleEnum.ADMIN:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden realizar esta acción"
        )

    success, error = service.delete_exercise(exercise_id)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST
        if error == "EXERCISE_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return {
        "message": f"{"Ejercicio eliminado exitosamente" if success else "Error en la eliminación"}",
        "id": exercise_id
    }

@router.get("/session/{session_id}", response_model=List[PracticeExerciseRead])
async def get_session_exercises(
    session_id: UUID = Path(..., description="ID de la sesión de práctica"),
    service: PracticeExerciseService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene todos los ejercicios realizados en una sesión de práctica específica.

    Este endpoint devuelve la lista completa de ejercicios asociados a una sesión
    de práctica, ordenados por fecha de creación. Es útil para ver el detalle
    completo de una sesión.

    Parámetros:
        session_id: UUID de la sesión de práctica
        service: Servicio para gestionar ejercicios (inyectado)

    Retorna:
        Lista de ejercicios realizados en la sesión

    Códigos de estado:
        200: Operación exitosa
        404: Sesión de práctica no encontrada
    """
    # TODO: Puede tener paginacion
    exercises, error = service.get_session_exercises(session_id)

    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )

    return exercises



@router.get("/analysis/{category}", response_model=PerformanceAnalysis)
async def get_performance_analysis(
    category: str = Path(..., description="Categoría de análisis: 'weapon', 'target', 'ammunition', 'distance' o 'exercise_type'"),
    shooter_id: Optional[UUID] = Query(None, description="ID del tirador para filtrar el análisis"),
    service: PracticeExerciseService = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene análisis de rendimiento por categoría específica.

    Este endpoint proporciona un análisis detallado del rendimiento en ejercicios
    agrupados por una categoría específica (arma, blanco, munición, distancia o tipo de ejercicio).

    Es especialmente útil para identificar fortalezas y áreas de mejora, como por ejemplo:
    - Qué armas proporcionan mejor precisión
    - A qué distancias se obtienen mejores resultados
    - Qué tipos de ejercicios resultan más desafiantes

    Parámetros:
        category: Categoría de análisis ('weapon', 'target', 'ammunition', 'distance', 'exercise_type')
        shooter_id: Opcional - ID del tirador para filtrar el análisis
        service: Servicio para gestionar ejercicios (inyectado)

    Retorna:
        Análisis de rendimiento para la categoría solicitada

    Códigos de estado:
        200: Operación exitosa
        400: Categoría inválida
        404: Tirador no encontrado
    """
    analysis, error = service.get_performance_analysis(category, shooter_id)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error == "SHOOTER_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND

        raise HTTPException(
            status_code=status_code,
            detail=error
        )

    return analysis
