from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
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
    club_service: ShootingClubService = Depends(),
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


    return club_service.get_all_clubs(skip, limit)

@router.get("/my-club", response_model=ShootingClubDetail)
async def get_my_club(
    current_user: dict = Depends(get_current_user),
    club_service: ShootingClubService = Depends(),
):
    """
    Obtiene el club de tiro del instructor jefe autenticado.

    Este endpoint permite a un usuario con el rol de INSTRUCTOR_JEFE
    acceder a los detalles de su propio club de tiro. No permite acceso
    a otros roles.

    Args:
        current_user: Usuario autenticado que realiza la solicitud.
        club_service: Servicio para gestionar clubes de tiro.

    Returns:
        ShootingClubDetail: Información detallada del club de tiro.

    Raises:
        HTTPException: Si el usuario no es un INSTRUCTOR_JEFE o si el club no se encuentra.
    """
    try:
        user_role_enum = RoleEnum.from_string(current_user.role)
        if user_role_enum != RoleEnum.INSTRUCTOR_JEFE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Solo los instructores jefes pueden acceder a su club. Tu rol actual es: {current_user.role}"
            )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol no reconocido")

    club = club_service.get_club_by_chief_instructor(current_user.id)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No eres Jefe de ningú club de tiro.")

    return club

@router.get("/search", response_model=List[ShootingClubWithChiefInstructor])
async def search_clubs(
    q: str = Query(..., description="Palabra clave para buscar clubes de tiro"),
    skip: int = Query(0, ge=0, description="Numero de registros a omitir (paginacion)"),
    limit: int = Query(10, ge=1, le=100, description="Limite de registros a devolver (paginacion)"),
    current_user: dict = Depends(get_current_user),
    club_service: ShootingClubService = Depends(),
):
    """
    Busca clubes de tiro por nombre o descripción.

    Permite encontrar clubes filtrando por términos que coincidan parcialmente
    con su nombre o descripción. Útil para búsquedas de texto libre.

    Args:
        q (str): Término de búsqueda
        skip (int): Número de registros a omitir (paginación)
        limit (int): Límite de registros a devolver (paginación)
        db (Session): Sesión de base de datos

    Returns:
        List[ShootingClubWithChiefInstructor]: Lista de clubes que coinciden con la búsqueda
    """
    return club_service.search_clubs(q, skip, limit)


@router.get("/{club_id}", response_model=ShootingClubDetail)
async def get_club_by_id(
    club_id: UUID,
    current_user: dict = Depends(get_current_user),
    club_service: ShootingClubService = Depends(),
):
    club = club_service.get_club_by_id(club_id)

    if not club.is_active:
        try:
            user_role_enum = RoleEnum.from_string(current_user.role)
            if user_role_enum == RoleEnum.TIRADOR:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No tienes permiso para ver un club inactivo"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver un club inactivo"
            )

    return club

@router.put("/{club_id}", response_model=ShootingClubRead)
async def update_club(
    club_id: UUID4 = Path(...),
    club_data: ShootingClubUpdate = ...,
    current_user: dict = Depends(get_current_user),
    club_service: ShootingClubService = Depends(),
):
    updated_club, error = club_service.update_club(club_id, club_data, current_user.id)

    if error:
        error_mappings = {
            "CLUB_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Club de tiro no encontrado"),
            "USER_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Usuario no encontrado"),
            "USER_NOT_AUTHORIZED_TO_UPDATE_CLUB": (status.HTTP_403_FORBIDDEN, "No tienes autorización para actualizar este club. Solo el dueño o un administrador pueden hacerlo."),
            "ONLY_ADMIN_CAN_CHANGE_CHIEF_INSTRUCTOR": (status.HTTP_403_FORBIDDEN, "Solo un administrador puede cambiar el jefe de instructores"),
            "NEW_CHIEF_INSTRUCTOR_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "El nuevo jefe de instructores no existe"),
            "NEW_CHIEF_NOT_INSTRUCTOR_JEFE": (status.HTTP_400_BAD_REQUEST, "El nuevo jefe debe tener rol de jefe de instructores"),
            "NEW_CHIEF_ALREADY_HAS_CLUB": (status.HTTP_409_CONFLICT, "El nuevo jefe ya tiene un club asignado"),
        }

        for prefix, (code, message) in error_mappings.items():
            if error.startswith(prefix):
                raise HTTPException(status_code=code, detail=message)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el club: {error}"
        )

    return updated_club

@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_club(
    club_id: UUID4 = Path(...),
    current_user: dict = Depends(get_current_user),
    club_service: ShootingClubService = Depends(),
):
    try:
        user_role_enum = RoleEnum.from_string(current_user.role)
        if user_role_enum != RoleEnum.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Solo los administradores pueden eliminar clubes. Tu rol actual es: {current_user.role}"
            )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Rol no reconocido {current_user.role}")

    success, error = club_service.delete_club(club_id, current_user.id)

    if error:
        error_mappings = {
            "CLUB_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Club de tiro no encontrado"),
            "USER_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Usuario no encontrado"),
            "ONLY_ADMIN_CAN_DELETE_CLUB": (status.HTTP_403_FORBIDDEN, "Solo un administrador puede eliminar un club"),
        }

        for prefix, (code, message) in error_mappings.items():
            if error.startswith(prefix):
                raise HTTPException(status_code=code, detail=message)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar el club: {error}"
        )

    return {
        "message": "Club de tiro eliminado correctamente",
        "club_id": club_id
    }



@router.patch("/{club_id}/toggle-active")
async def toggle_active(
    club_id: UUID,
    current_user: dict = Depends(get_current_user),
    club_service: ShootingClubService = Depends(),
):
    # try:
    #     user_role_enum = RoleEnum.from_string(current_user.role)
    #     if user_role_enum != RoleEnum.ADMIN:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail=f"Solo un administrador o el jefe de instructores puede activar o desactivar un club. Tu rol actual es: {current_user.role}"
    #         )
    # except ValueError:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol no reconocido")

    club, error = club_service.toggle_club_active(club_id, current_user.id)

    if error:
        error_mappings = {
            "CLUB_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Club de tiro no encontrado"),
            "USER_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Usuario no encontrado"),
            "USER_NOT_AUTHORIZED_TO_TOGGLE_CLUB_ACTIVE": (status.HTTP_403_FORBIDDEN, "Solo un administrador puede activar o desactivar un club"),
            "ERROR_TOGGLING_CLUB" : (status.HTTP_400_BAD_REQUEST, "Error al activar o desactivar el club"),
        }

        for prefix, (code, message) in error_mappings.items():
            if error.startswith(prefix):
                raise HTTPException(status_code=code, detail=message)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al activar o desactivar el club: {error}"
        )

    return {
        "message": "Club de tiro actualizado correctamente como activo" if club.is_active else "Club de tiro actualizado correctamente como inactivo",
        "club_id": club_id
    }

@router.post("/{club_id}/add_member", response_model=ClubMemberDetail, status_code=status.HTTP_201_CREATED)
async def add_member(
    club_id: UUID = Path(...),
    member_data: ShooterClubAssignment = ...,
    current_user: dict = Depends(get_current_user),
    club_service: ShootingClubService = Depends(),
):
    """
    Añade un tirador como miembro del club directamente.

    Esta operación solo puede ser realizada por el jefe de instructores del club.
    Un tirador solo puede pertenecer a un club a la vez.

    Args:
        club_id (UUID): ID del club al que se añadirá el tirador
        member_data (ShooterClubAssignment): Datos con el ID del tirador a añadir
        db (Session): Sesión de base de datos
        current_user (Dict): Usuario autenticado actual

    Returns:
        ClubMemberDetail: Detalles del tirador añadido al club
    """
    try:
        user_role_enum = RoleEnum.from_string(current_user.role)
        if user_role_enum != RoleEnum.ADMIN and user_role_enum != RoleEnum.INSTRUCTOR_JEFE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Solo los administradores pueden agregar miembros a clubes. Tu rol actual es: {current_user.role}"
            )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Rol no reconocido {current_user.role}")

    updated_shooter , error = club_service.add_member(club_id, member_data.shooter_id, current_user.id)

    if error:
        error_mappings = {
            "CLUB_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Club de tiro no encontrado"),
            "USER_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Usuario no encontrado"),
            "SHOOTER_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Tirador no encontrado"),
            "USER_NOT_AUTHORIZED_TO_ADD_MEMBER_TO_CLUB": (status.HTTP_403_FORBIDDEN, "No tienes autorización para agregar miembros a este club. Solo el dueño o un administrador pueden hacerlo."),
            "SHOOTER_ALREADY_IN_CLUB": (status.HTTP_409_CONFLICT, "El tirador ya pertenece a este club"),
            "ERROR_ADDING_MEMBER_TO_CLUB" : (status.HTTP_400_BAD_REQUEST, "Error al agregar el miembro al club"),
        }

        for prefix, (code, message) in error_mappings.items():
            if error.startswith(prefix):
                raise HTTPException(status_code=code, detail=message)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al agregar el miembro al club: {error}"
        )
    return updated_shooter
