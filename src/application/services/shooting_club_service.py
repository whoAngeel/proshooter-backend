from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from src.domain.enums.role_enum import RoleEnum
from src.infraestructure.database.repositories.shooting_club_repo import ShootingClubRepository
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.infraestructure.database.repositories.user_repo import UserRepository
from src.infraestructure.database.session import get_db
from src.presentation.schemas.shootingclub_schema import ShootingClubCreate, ShootingClubRead

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



    @staticmethod
    def get_club_by_id(db: Session, club_id: UUID) -> Any:
        return ShootingClubRepository.get_by_id(db, club_id)

    @staticmethod
    def get_club_by_chief_instructor(db: Session, chief_instructor_id: UUID) -> Any:
        return ShootingClubRepository.get_by_chief_instructor(db, chief_instructor_id)

    @staticmethod
    def get_all_clubs(db: Session, skip : int = 0, limit : int = 100) -> List[Any]:
        return ShootingClubRepository.get_all(db, skip, limit)

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
