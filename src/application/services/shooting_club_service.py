from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from src.domain.enums.role_enum import RoleEnum
from src.infraestructure.database.repositories.shooting_club_repo import ShootingClubRepository
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.infraestructure.database.repositories.user_repo import UserRepository
from src.infraestructure.database.session import get_db
from src.presentation.schemas.shootingclub_schema import ShootingClubCreate, ShootingClubRead, ShootingClubUpdate

class ShootingClubService:
    """
    Servicio para administrar operaciones relacionadas con clubes de tiro.

    Esta capa de servicio implementa la lógica de negocio relacionada con los clubes de tiro,
    actúa como intermediario entre los controladores de la API y el repositorio, y se encarga
    de aplicar reglas de negocio, validaciones, y transformaciones de datos.
    """

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_club(self, club_data: ShootingClubCreate, current_user_id: UUID) -> Tuple[Any, Optional[str]]:
        """
        Crea un nuevo club de tiro.

        Args:
            club_data: Datos del club a crear
            current_user_id: ID del usuario que crea el club

        Returns:
            Tupla con el club creado y un mensaje de error (si hay error)
        """
        current_user = UserRepository.get_by_id(self.db, current_user_id)

        if not current_user:
            return None, "USER_NOT_FOUND"

        user_role_enum = RoleEnum.from_string(current_user.role)
        if not user_role_enum.can_create_club():
            return None, "USER_NOT_AUTHORIZED_TO_CREATE_CLUB"

        if user_role_enum == RoleEnum.INSTRUCTOR_JEFE:
            club_data_dict = club_data.model_dump()
            club_data_dict["chief_instructor_id"] = current_user.id

            existing_club = ShootingClubRepository.get_by_chief_instructor(self.db, current_user.id)
            if existing_club:
                return None, "CHIEF_INSTRUCTOR_ALREADY_HAS_A_CLUB"

        elif user_role_enum == RoleEnum.ADMIN:
            # si es ADMIN, puede especificar cualquier instructor jefe como el jefe del club
            chief_instructor = UserRepository.get_by_id(self.db, club_data.chief_instructor_id)
            if not chief_instructor:
                return None, "CHIEF_INSTRUCTOR_NOT_FOUND"

            if chief_instructor.role != RoleEnum.INSTRUCTOR_JEFE.value:
                # Solo un admin puede asignar a alguien como jefe
                # Si es INSTRUCTOR, intentar promoverlo a INSTRUCTOR_JEFE
                if chief_instructor.role == RoleEnum.INSTRUCTOR.value:
                    updated_user, error = UserRepository.promote_role(self.db, chief_instructor.id, RoleEnum.INSTRUCTOR_JEFE.value)
                    if error:
                        return None, f"ERROR_PROMOTING_INSTRUCTOR: {error}"
                else:
                    return None, "USER_NOT_INSTRUCTOR"

            existing_club = ShootingClubRepository.get_by_chief_instructor(self.db, chief_instructor.id)
            if existing_club:
                return None, "CHIEF_INSTRUCTOR_ALREADY_HAS_A_CLUB"

            club_data_dict = club_data.model_dump()
        else:
            return None, "USER_NOT_AUTHORIZED_TO_CREATE_CLUB"

        existing_club_by_name = ShootingClubRepository.get_by_name(self.db, club_data.name)
        if existing_club_by_name:
            return None, "CLUB_WITH_SAME_NAME_ALREADY_EXISTS"

        try:
            # Creamos el club
            new_club = ShootingClubRepository.create(self.db, club_data_dict)

            self.db.commit()

            return ShootingClubRepository.get_by_id(self.db, new_club.id), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_CREATING_CLUB: {str(e)}"


    def get_club_by_id(self, club_id: UUID) -> Any:
        return ShootingClubRepository.get_by_id(self.db, club_id)

    def get_club_by_chief_instructor(self, chief_instructor_id: UUID) -> Any:
        return ShootingClubRepository.get_by_chief_instructor(self.db, chief_instructor_id)

    def get_all_clubs(self, skip : int = 0, limit : int = 100) -> List[Any]:
        return ShootingClubRepository.get_all(self.db, skip, limit)

    def delete_club(self, club_id: UUID, current_user_id: UUID)-> Tuple[bool, Optional[str]]:
        club = ShootingClubRepository.get_by_id(self.db, club_id)
        if not club:
            return False, "CLUB_NOT_FOUND"

        current_user = UserRepository.get_by_id(self.db, current_user_id)
        if not current_user:
            return False, "USER_NOT_FOUND"

        user_role_enum = RoleEnum.from_string(current_user.role)
        if user_role_enum != RoleEnum.ADMIN:
            return False, "ONLY_ADMIN_CAN_DELETE_CLUBS"

        try:
            success = ShootingClubRepository.delete(self.db, club_id)
            if success:
                self.db.commit()
                return True, None
            else:
                return False, "ERROR_DELETING_CLUB"
        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_DELETING_CLUB: {str(e)}"

    def update_club(self, club_id: UUID, club_data: ShootingClubUpdate, current_user_id: UUID)-> Tuple[Any, Optional[str]]:
        club = ShootingClubRepository.get_by_id(self.db, club_id)
        if not club:
            return None, "CLUB_NOT_FOUND"

        current_user = UserRepository.get_by_id(self.db, current_user_id)
        if not current_user:
            return None, "USER_NOT_FOUND"

        user_role_enum = RoleEnum.from_string(current_user.role)
        is_admin = user_role_enum == RoleEnum.ADMIN
        is_club_owner = str(club.chief_instructor_id) == str(current_user_id)

        if not (is_admin or is_club_owner):
            return None, "USER_NOT_AUTHORIZED_TO_UPDATE_CLUB"

        if hasattr(club_data, "chief_instructor_id") and club_data.chief_instructor_id is not None and str(club_data.chief_instructor_id) != str(club.chief_instructor_id):
            # solo el admin puede cambiar el jefe de instructores
            if not is_admin:
                return None, "ONLY_ADMIN_CAN_CHANGE_CHIEF_INSTRUCTOR"

            # verificar qeu el nuevo jefe exista
            new_chief = UserRepository.get_by_id(self.db, club_data.chief_instructor_id)
            if not new_chief:
                return None, "NEW_CHIEF_INSTRUCTOR_NOT_FOUND"

            # Verificar que el nuevo jefe tenga el rol adecuado
            if new_chief.role != RoleEnum.INSTRUCTOR_JEFE.value:
                # Intentar promover si es instructor (solo admin puede hacer esto)
                if new_chief.role == RoleEnum.INSTRUCTOR.value:
                    _, error = UserRepository.promote_role(
                        self.db, new_chief.id, RoleEnum.INSTRUCTOR_JEFE.value
                    )
                    if error:
                        return None, f"ERROR_PROMOTING_INSTRUCTOR: {error}"
                else:
                    return None, "NEW_CHIEF_NOT_INSTRUCTOR_JEFE"

            # Verificar si el nuevo jefe ya tiene un club
            existing_club = ShootingClubRepository.get_by_chief_instructor(self.db, club_data.chief_instructor_id)
            if existing_club and str(existing_club.id) != str(club.id):
                return None, "NEW_CHIEF_ALREADY_HAS_CLUB"
        try:
            # Actualizar el club
            update_data = {k: v for k, v in club_data.model_dump().items() if v is not None}
            updated_club = ShootingClubRepository.update(self.db, club_id, update_data)

            # confirmar los cambios
            self.db.commit()

            return ShootingClubRepository.get_by_id(self.db, club_id), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPDATING_CLUB: {str(e)}"


    def toggle_club_active(self, club_id: UUID, current_user_id: UUID) -> Tuple[Any, Optional[str]]:
        """
        Cambia el estado de activación de un club de tiro.
        Permite que tanto el administrador como el dueño del club
        puedan activar o desactivar el club.

        Args:
            club_id: ID del club
            current_user_id: ID del usuario que realiza la acción

        Returns:
            Tupla con el club actualizado y un mensaje de error (si hay error)
        """
        # Verificar que el club exista
        club = ShootingClubRepository.get_by_id(self.db, club_id)
        if not club:
            return None, "CLUB_NOT_FOUND"

        # Verificar permisos
        current_user = UserRepository.get_by_id(self.db, current_user_id)
        if not current_user:
            return None, "USER_NOT_FOUND"

        # Verificar que el usuario sea admin o dueño del club
        user_role_enum = RoleEnum.from_string(current_user.role)
        is_admin = user_role_enum == RoleEnum.ADMIN
        is_club_owner = str(club.chief_instructor_id) == str(current_user_id)

        if not (is_admin or is_club_owner):
            return None, "USER_NOT_AUTHORIZED_TO_TOGGLE_CLUB_ACTIVE"

        try:
            # Cambiar el estado de activación
            updated_club = ShootingClubRepository.toggle_active(self.db, club_id)

            # Confirmar la transacción
            self.db.commit()

            # Devolver el club actualizado
            return ShootingClubRepository.get_by_id(self.db, club_id), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_TOGGLING_CLUB: {str(e)}"
