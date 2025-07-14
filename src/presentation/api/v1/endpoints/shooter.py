from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, Body
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.enums.classification_enum import ShooterLevelEnum
from src.domain.enums.role_enum import RoleEnum

from src.application.services.shooter_service import ShooterService
from src.infraestructure.auth.jwt_config import get_current_user
from src.infraestructure.database.session import get_db
from src.presentation.schemas.shooter_schema import (
    ShooterRead,
    ShooterReadLite,
    ShooterDetail,
    ShooterUpdate,
    ShooterList,
    ShooterFilter,
    ShooterClassificationHistory,
    ShooterPerformanceSummary,
    ShooterComparisonResult,
)
from src.application.services.user_service import UserService

router = APIRouter(
    prefix="/shooters",
    tags=["Shooters"],
    responses={404: {"description": "Not found"}},
)


# Endpoint para validar si un nickname está disponible
@router.get("/validate-nickname", summary="Valida si un nickname está disponible")
async def validate_nickname(
    nickname: str = Query(
        ..., min_length=3, max_length=32, description="Nickname a validar"
    ),
    shooter_service: ShooterService = Depends(),
):
    """
    Verifica si un nickname de tirador está disponible.
    Retorna {"available": true/false}
    """
    is_available = shooter_service.is_nickname_available(nickname)
    return {"available": is_available}


# Endpoint para obtener todos los tiradores con paginación
@router.get("/", response_model=ShooterList)
async def get_all_shooters(
    skip: int = Query(0, ge=0, description="Índice de inicio de la página"),
    limit: int = Query(
        100, ge=1, le=500, description="Cantidad de tiradores por página (máx 500)"
    ),
    shooter_service: ShooterService = Depends(),
):
    """
    Obtiene una lista paginada de todos los tiradores.

    Permite filtrar y paginar los resultados.

    Parámetros:
        skip: Índice de inicio (offset)
        limit: Cantidad de resultados por página (default 100)
    Retorna:
        Lista paginada de tiradores
    """
    filter_params = ShooterFilter(skip=skip, limit=limit)
    shooters = shooter_service.get_all_shooters(filter_params)
    return shooters


@router.get("/{user_id}", response_model=ShooterDetail)
async def get_shooter(
    user_id: UUID = Path(..., description="ID del usuario/tirador a obtener"),
    shooter_service: ShooterService = Depends(),
):
    """
    Obtiene los detalles completos de un tirador específico.

    Este endpoint devuelve información detallada sobre un tirador, incluyendo:
    - Datos básicos del tirador (nivel, rango, club)
    - Información del usuario asociado
    - Estadísticas de rendimiento
    - Conteo de sesiones y evaluaciones
    - Progreso reciente (mejorando, estable, declinando)
    - Nombre del club si está asignado

    Es útil para ver el perfil completo de un tirador con toda la información relevante.

    Parámetros:
        user_id: UUID del usuario que también es el ID del tirador
        shooter_service: Servicio de tiradores (inyectado)

    Retorna:
        Información detallada completa del tirador

    Códigos de estado:
        200: Operación exitosa
        404: Tirador no encontrado
    """
    shooter, error = shooter_service.get_shooter_by_id(user_id)

    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)

    return shooter


@router.put("/{user_id}", response_model=ShooterRead)
async def update_shooter(
    shooter_data: ShooterUpdate,
    user_id: UUID = Path(..., description="ID del tirador a actualizar"),
    shooter_service: ShooterService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Actualiza la información de un tirador existente.

    Este endpoint permite modificar los datos de un tirador como:
    - Nivel de clasificación
    - Rango asignado
    - Club al que pertenece

    # TODO: validar quien edita el tirador

    La actualización es parcial, por lo que solo se modificarán los campos
    que se proporcionen en la solicitud.

    Parámetros:
        shooter_data: Datos a actualizar del tirador
        user_id: UUID del tirador a actualizar
        shooter_service: Servicio de tiradores (inyectado)

    Retorna:
        Información actualizada del tirador

    Códigos de estado:
        200: Tirador actualizado exitosamente
        404: Tirador o club no encontrado
        400: Datos de entrada inválidos
    """
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.INSTRUCTOR]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes permiso para actualizar tiradores",
        )

    shooter, error = shooter_service.update_shooter(user_id, shooter_data)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error in ["SHOOTER_NOT_FOUND", "CLUB_NOT_FOUND", "NICKNAME_ALREADY_EXISTS"]:
            status_code = status.HTTP_404_NOT_FOUND

        raise HTTPException(status_code=status_code, detail=error)

    return shooter


@router.patch("/{user_id}/classification", status_code=status.HTTP_200_OK)
async def update_shooter_classification(
    new_level: ShooterLevelEnum,
    user_id: UUID = Path(..., description="ID del tirador"),
    shooter_service: ShooterService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Actualiza específicamente la clasificación de un tirador.

    Este endpoint permite cambiar la clasificación de un tirador a un nuevo nivel.
    Se utiliza típicamente cuando:
    - Un instructor determina que un tirador ha alcanzado un nuevo nivel
    - Se corrige manualmente una clasificación
    - Se implementa una decisión administrativa sobre el nivel de un tirador

    Los niveles disponibles son:
    - TE (Tirador Experto): 90-100% de efectividad
    - TC (Tirador Confiable): 70-89% de efectividad
    - TM (Tirador Medio): 40-69% de efectividad
    - TR (Tirador Regular): 10-39% de efectividad

    El cambio de clasificación se registra para mantener un historial.

    Parámetros:
        new_level: Nueva clasificación para el tirador
        user_id: UUID del tirador
        shooter_service: Servicio de tiradores (inyectado)

    Retorna:
        Confirmación del cambio de clasificación

    Códigos de estado:
        200: Clasificación actualizada exitosamente
        404: Tirador no encontrado
        400: Nivel de clasificación inválido
    """
    success, error = shooter_service.update_shooter_classification(user_id, new_level)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error == "SHOOTER_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND

        raise HTTPException(status_code=status_code, detail=error)

    return {
        "message": f"Clasificación actualizada exitosamente a {new_level.value}",
        "success": True,
    }


@router.patch("/{user_id}/club/{club_id}", status_code=status.HTTP_200_OK)
async def assign_shooter_to_club(
    user_id: UUID = Path(..., description="ID del tirador"),
    club_id: UUID = Path(..., description="ID del club"),
    shooter_service: ShooterService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Asigna un tirador a un club específico.

    Este endpoint permite asociar un tirador con un club de tiro específico.
    Es útil para:
    - Registrar la pertenencia de un tirador a un club
    - Transferir un tirador de un club a otro
    - Organizar tiradores por ubicación o afiliación

    La asignación permite posteriormente filtrar tiradores por club y
    generar estadísticas específicas del club.

    Parámetros:
        user_id: UUID del tirador a asignar
        club_id: UUID del club al que se asignará el tirador
        shooter_service: Servicio de tiradores (inyectado)

    Retorna:
        Confirmación de la asignación al club

    Códigos de estado:
        200: Tirador asignado al club exitosamente
        404: Tirador o club no encontrado
        400: Error en la asignación
    """
    success, error = shooter_service.assign_shooter_to_club(user_id, club_id)

    if error:
        status_code = status.HTTP_400_BAD_REQUEST

        if error in ["SHOOTER_NOT_FOUND", "CLUB_NOT_FOUND"]:
            status_code = status.HTTP_404_NOT_FOUND

        raise HTTPException(status_code=status_code, detail=error)

    return {"message": "Tirador asignado al club exitosamente", "success": True}


@router.get("/{user_id}/performance", response_model=ShooterPerformanceSummary)
async def get_shooter_performance(
    user_id: UUID = Path(..., description="ID del tirador"),
    shooter_service: ShooterService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene un resumen completo del rendimiento de un tirador.

    Este endpoint proporciona un análisis detallado del rendimiento del tirador,
    incluyendo:
    - Estadísticas generales (total de sesiones, disparos, precisión)
    - Tendencia reciente (mejorando, estable, declinando)
    - Fortalezas y debilidades identificadas
    - Ejercicios recomendados para mejorar
    - Evaluaciones recientes

    Es especialmente útil para:
    - Instructores que evalúan el progreso de sus estudiantes
    - Tiradores que quieren entender su rendimiento
    - Administradores que generan reportes de rendimiento

    Parámetros:
        user_id: UUID del tirador
        shooter_service: Servicio de tiradores (inyectado)

    Retorna:
        Resumen completo del rendimiento del tirador

    Códigos de estado:
        200: Operación exitosa
        404: Tirador no encontrado
        400: Error obteniendo datos de rendimiento
    """
    performance, error = shooter_service.get_shooter_performance(user_id)

    if error:
        status_code = status.HTTP_404_NOT_FOUND

        if error.startswith("ERROR_"):
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(status_code=status_code, detail=error)

    return performance


@router.get(
    "/{user_id}/classification-history", response_model=ShooterClassificationHistory
)
async def get_classification_history(
    user_id: UUID = Path(..., description="ID del tirador"),
    shooter_service: ShooterService = Depends(),
):
    """
    Obtiene el historial de cambios de clasificación de un tirador.

    Este endpoint devuelve información sobre la evolución de la clasificación
    del tirador a lo largo del tiempo, incluyendo:
    - Lista de cambios de clasificación con fechas
    - Clasificación actual
    - Días transcurridos en la clasificación actual
    - Tendencia de progresión (ascendente, estable, descendente)

    Es útil para:
    - Seguir la evolución de un tirador
    - Verificar la consistencia en las clasificaciones
    - Identificar patrones de mejora o deterioro
    - Generar reportes de progreso

    Parámetros:
        user_id: UUID del tirador
        shooter_service: Servicio de tiradores (inyectado)

    Retorna:
        Historial completo de clasificaciones del tirador

    Códigos de estado:
        200: Operación exitosa
        404: Tirador no encontrado
        400: Error obteniendo historial
    """
    history, error = shooter_service.get_classification_history(user_id)

    if error:
        status_code = status.HTTP_404_NOT_FOUND

        if error.startswith("ERROR_"):
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(status_code=status_code, detail=error)

    return history


@router.get(
    "/{user_id}/compare/{other_user_id}", response_model=ShooterComparisonResult
)
async def compare_shooters(
    user_id: UUID = Path(..., description="ID del primer tirador"),
    other_user_id: UUID = Path(..., description="ID del segundo tirador"),
    shooter_service: ShooterService = Depends(),
):
    """
    Compara el rendimiento entre dos tiradores específicos.

    Este endpoint realiza una comparación detallada entre dos tiradores,
    proporcionando:
    - Diferencias en precisión general
    - Diferencias en tiempos de reacción
    - Comparación de fortalezas por categorías
    - Recomendaciones personalizadas basadas en las diferencias

    La comparación es útil para:
    - Instructores que evalúan diferentes enfoques de entrenamiento
    - Tiradores que quieren aprender de compañeros más experimentados
    - Identificar áreas específicas donde un tirador puede mejorar
    - Análisis de técnicas y metodologías de entrenamiento

    Parámetros:
        user_id: UUID del primer tirador
        other_user_id: UUID del segundo tirador a comparar
        shooter_service: Servicio de tiradores (inyectado)

    Retorna:
        Análisis comparativo detallado entre los dos tiradores

    Códigos de estado:
        200: Operación exitosa
        404: Uno o ambos tiradores no encontrados
        400: Error en la comparación
    """
    comparison, error = shooter_service.compare_shooters(user_id, other_user_id)

    if error:
        status_code = status.HTTP_404_NOT_FOUND

        if error.startswith("ERROR_"):
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(status_code=status_code, detail=error)

    return comparison


@router.get("/rankings/top", response_model=List[Dict[str, Any]])
async def get_top_shooters(
    criteria: str = Query(
        "accuracy",
        description="Criterio de ranking: 'accuracy', 'effectiveness', 'hit_factor'",
    ),
    limit: int = Query(
        10, ge=1, le=50, description="Número de tiradores en el ranking"
    ),
    shooter_service: ShooterService = Depends(),
):
    """
    Obtiene el ranking de los mejores tiradores según un criterio específico.

    Este endpoint devuelve una lista de los tiradores con mejor rendimiento
    según el criterio especificado. Los criterios disponibles son:

    - **accuracy**: Precisión general (porcentaje de aciertos)
    - **effectiveness**: Efectividad general basada en evaluaciones recientes
    - **hit_factor**: Factor de hit (puntos por tiempo), métrica usada en IPSC

    El ranking es útil para:
    - Identificar a los tiradores más destacados
    - Motivar la competencia sana entre tiradores
    - Reconocer logros y mejoras
    - Establecer objetivos de rendimiento
    - Generar reportes de desempeño del club o institución

    Parámetros:
        criteria: Criterio para el ranking ('accuracy', 'effectiveness', 'hit_factor')
        limit: Número máximo de tiradores a devolver (1-50)
        shooter_service: Servicio de tiradores (inyectado)

    Retorna:
        Lista ordenada de los mejores tiradores según el criterio

    Códigos de estado:
        200: Operación exitosa
        400: Criterio inválido o error en la consulta
    """
    top_shooters, error = shooter_service.get_top_shooters(limit, criteria)

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return top_shooters


@router.patch("/{shooter_id}/promote", response_model=ShooterReadLite)
def promote_user(
    shooter_id: UUID,
    new_role: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    # user, error = UserService.promote(db, shooter_id, new_role)
    updated_user, error = UserService.promote_role(db, shooter_id, new_role)

    # Manejar posibles errores
    if error:
        error_messages = {
            "USER_NOT_FOUND": ("Usuario no encontrado", 404),
            "USER_NOT_ACTIVE": ("El usuario no está activo", 400),
            "INVALID_ROLE": ("Rol inválido", 400),
            "DATABASE_ERROR": ("Error en la base de datos", 500),
        }

        if error.startswith("INVALID_PROMOTION:"):
            roles = error.split(":", 1)[1].split(">")
            detail = f"Promoción no válida. Un {roles[0]} no puede ser promovido directamente a {roles[1]}"
            raise HTTPException(status_code=400, detail=detail)
        else:
            detail, status_code = error_messages.get(error, ("Error desconocido", 500))
            raise HTTPException(status_code=status_code, detail=detail)

    shooter = ShooterService.get_shooter_by_user_id(db, shooter_id)
    if not shooter:
        raise HTTPException(status_code=400, detail="El tirador no existe")
    return shooter
