from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional, Tuple, Dict, Any

from infraestructure.database.repositories.shooting_club_repo import ShootingClubRepository
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.infraestructure.database.repositories.user_repo import UserRepository
from src.presentation.schemas.shootingclub_schema import ShootingClubCreate, ShootingClubRead

class ShootingClubService:
    """
    Servicio para administrar operaciones relacionadas con clubes de tiro.

    Esta capa de servicio implementa la lógica de negocio relacionada con los clubes de tiro,
    actúa como intermediario entre los controladores de la API y el repositorio, y se encarga
    de aplicar reglas de negocio, validaciones, y transformaciones de datos.
    """

    @staticmethod
    def create_club(db: Session, club_data: ShootingClubCreate) -> Tuple[Any, Optional[str]]:

        # Verificar que el jefe de instructores existe
        chief_instructor = UserRepository.get_by_id(db, club_data.chief_instructor_id)
        if not chief_instructor:
            return None, "CHIEF_INSTRUCTOR_NOT_FOUND"

        # Verificar que el jefe de instructores tenga el rol adecuado
        if chief_instructor.role != "CHIEF_INSTRUCTOR":
            return None, "USER_NOT_CHIEF_INSTRUCTOR"

        # Verificar que el jefe de instructores no tenga ya un club
        existing_club = ShootingClubRepository.get_by_chief_instructor(db, club_data.chief_instructor_id)
        if existing_club:
            return None, "CHIEF_INSTRUCTOR_ALREADY_HAS_CLUB"

        # Verificar que no exista un club con el mismo nombre
        existing_club_by_name = ShootingClubRepository.get_by_name(db, club_data.name)
        if existing_club_by_name:
            return None, "CLUB_WITH_SAME_NAME_ALREADY_EXISTS"

        try:
            # Crear el club de tiro
            club_dict = club_data.dict()
            new_club = ShootingClubRepository.create(db, club_dict)

            db.commit()

            return ShootingClubRepository.get_by_id(db, new_club.id), None
        except Exception as e:
            db.rollback()
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
