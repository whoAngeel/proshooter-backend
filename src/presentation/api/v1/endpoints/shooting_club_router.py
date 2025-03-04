from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from src.infraestructure.database.session import get_db
from src.infraestructure.auth.jwt_config import get_current_user
from uuid import UUID

from src.application.services.shooting_club_service import ShootingClubService
from src.presentation.schemas.shootingclub_schema import *
from src.domain.enums.role_enum import RoleEnum


router = APIRouter(prefix="/shooting_clubs", tags=["shooting_clubs"])

@router.post("/", response_model=ShootingClubRead)
async def create_club(
    club_data: ShootingClubBase,
    current_user = Depends(get_current_user),
    club_service: ShootingClubService = Depends()
):
    """
    Crea un nuevo club de tiro.

    Si el usuario es INSTRUCTOR_JEFE, será automáticamente asignado como el
    jefe de instructores del club, independientemente del valor proporcionado
    en club_data.chief_instructor_id.

    Si el usuario es ADMIN, puede especificar cualquier INSTRUCTOR_JEFE como
    jefe del club.

    Args:
        club_data: Datos del club a crear
        current_user: Usuario autenticado que realiza la solicitud
        club_service: Servicio para gestionar clubes de tiro

    Returns:
        ShootingClubRead: Datos del club creado

    Raises:
        HTTPException: Si ocurre un error durante la creación
    """
    try:
        user_role_enum = RoleEnum.from_string(current_user.role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol no recognido")

    if not user_role_enum.can_create_club():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tienes permiso para crear un club. Tu rol actual es: {current_user.role}"
        )

    club, error = club_service.create_club(club_data, current_user.id)

    if error:
        error_mappings = {
            "USER_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Usuario no encontrado"),
            "USER_NOT_AUTHORIZED_TO_CREATE_CLUB": (status.HTTP_403_FORBIDDEN, "No tienes autorización para crear un club"),
            "CHIEF_INSTRUCTOR_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Jefe de instructores no encontrado"),
            "USER_NOT_CHIEF_INSTRUCTOR": (status.HTTP_400_BAD_REQUEST, "El usuario especificado no es jefe de instructores"),
            "USER_NOT_INSTRUCTOR": (status.HTTP_400_BAD_REQUEST, "El usuario especificado no es instructor"),
            "CHIEF_INSTRUCTOR_ALREADY_HAS_CLUB": (status.HTTP_409_CONFLICT, "El jefe de instructores ya tiene un club asignado"),
            "CLUB_WITH_SAME_NAME_ALREADY_EXISTS": (status.HTTP_409_CONFLICT, "Ya existe un club con ese nombre"),
        }
        # Obtener código y mensaje según el error
        for prefix, (code, message) in error_mappings.items():
            if error.startswith(prefix):
                raise HTTPException(status_code=code, detail=message)

        # Error genérico
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el club: {error}"
        )

    return club



@router.get("/", response_model=List[ShootingClubWithChiefInstructor])
async def get_all_clubs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    """
    Obtiene una lista de todos los clubes de tiro.

    Args:
        skip: Número de registros a omitir (paginación)
        limit: Número máximo de registros a devolver (paginación)
        include_inactive: Si se deben incluir clubes inactivos
        current_user: Usuario autenticado que realiza la solicitud
        club_service: Servicio para gestionar clubes de tiro

    Returns:
        List[ShootingClubWithChiefInstructor]: Lista de clubes de tiro
    """


    return ShootingClubService.get_all_clubs(db, skip, limit)

@router.get("/my-club", response_model=ShootingClubDetail)
async def get_my_club(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        user_role_enum = RoleEnum.from_string(current_user.role)
        if user_role_enum != RoleEnum.INSTRUCTOR_JEFE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Solo los instructores jefes pueden acceder a su club. Tu rol actual es: {current_user.role}"
            )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol no reconocido")

    club = ShootingClubService.get_club_by_chief_instructor(db, current_user.id)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No eres Jefe de ningú club de tiro.")

    return club
