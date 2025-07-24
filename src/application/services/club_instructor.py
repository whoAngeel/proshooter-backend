from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional, Tuple
from fastapi import HTTPException, Depends


from src.infraestructure.database.session import get_db
from src.infraestructure.database.repositories.instructor import InstructorRepository
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.presentation.schemas.instructor import (
    AvailableInstructorsResponse,
    InstructorBasicInfo,
)
from src.infraestructure.database.models.shooting_club_model import ShootingClubModel


class ClubInstructorService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_available_instructors_for_shooter(
        self, shooter_id: UUID
    ) -> AvailableInstructorsResponse:
        shooter = ShooterRepository.get_by_id(self.db, shooter_id)
        if not shooter:
            raise HTTPException(status_code=404, detail="Tirador no encontrado")
        if not shooter.club_id:
            return AvailableInstructorsResponse(
                success=True, instructors=[], club_name=None, total_count=0
            )

        # Obtener instructores del mismo club
        instructors = InstructorRepository.get_available_instructors_for_shooter(
            self.db, shooter_id
        )

        instructor_list = []
        for instructor in instructors:
            instructor_info = InstructorBasicInfo(
                id=instructor.id,
                email=instructor.email,
                role=instructor.role,
                full_name=self._get_full_name(instructor),
                is_chief_instructor=instructor.role == "INSTRUCTOR_JEFE",
            )
            instructor_list.append(instructor_info)

        # Obtener el nombre del club
        club = (
            self.db.query(ShootingClubModel)
            .filter(ShootingClubModel.id == shooter.club_id)
            .first()
        )
        club_name = club.name if club else None

        return AvailableInstructorsResponse(
            success=True,
            instructors=instructor_list,
            club_name=club_name,
            total_count=len(instructor_list),
        )

    def validate_instructor_selection(
        self, instructor_id: UUID, shooter_id: UUID
    ) -> Tuple[bool, str]:
        """
        Valida si el instructor seleccionado es válido para el tirador.
        """
        if not InstructorRepository.validate_instructor_permission(
            self.db, instructor_id
        ):
            return False, "Usuario no es instructor válido"
        # validar que estan en el mismo club
        if not InstructorRepository.is_instructor_in_same_club(
            self.db, instructor_id, shooter_id
        ):
            return False, "Instructor no pertenece al mismo club que el tirador"
        return True, None

    def get_club_instructors(self, club_id: UUID) -> List[InstructorBasicInfo]:
        """
        Obtiene todos los instructores de un club.
        """
        instructors = InstructorRepository.get_instructors_by_club(self.db, club_id)

        instructor_list = []
        for instructor in instructors:
            instructor_info = InstructorBasicInfo(
                id=instructor.id,
                email=instructor.email,
                role=instructor.role,
                full_name=self._get_full_name(instructor),
                is_chief_instructor=instructor.role == "INSTRUCTOR_JEFE",
            )
            instructor_list.append(instructor_info)
        return instructor_list

    def get_instructor_club_info(self, instructor_id: UUID) -> Optional[UUID]:
        return InstructorRepository.get_instructor_basic_info(self.db, instructor_id)

    def _get_full_name(self, user) -> str:
        if user.personal_data:
            first_name = user.personal_data.first_name or ""
            second_name = user.personal_data.second_name or ""
            last_name1 = user.personal_data.last_name1 or ""
            last_name2 = user.personal_data.last_name2 or ""
            return f"{first_name} {second_name} {last_name1} {last_name2}".strip()
        return user.email  # Fallback to email if personal data is not available
