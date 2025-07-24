from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_
from uuid import UUID
from typing import List, Optional

from src.infraestructure.database.models.user_model import UserModel
from src.infraestructure.database.models.shooter_model import ShooterModel
from src.infraestructure.database.models.shooting_club_model import ShootingClubModel


class InstructorRepository:
    @staticmethod
    def get_instructors_by_club(db: Session, club_id: UUID) -> List[UserModel]:
        query = (
            select(UserModel)
            .join(ShooterModel, UserModel.id == ShooterModel.user_id)
            .where(
                and_(
                    UserModel.role.in_(["INSTRUCTOR", "INSTRUCTOR_JEFE"]),
                    ShooterModel.club_id == club_id,
                    UserModel.is_active == True,
                )
            )
            .options(
                joinedload(UserModel.personal_data),
                joinedload(UserModel.shooter),
            )
        )
        result = db.execute(query)
        return result.scalars().all()

    @staticmethod
    def get_available_instructors_for_shooter(
        db: Session, shooter_id: UUID
    ) -> List[UserModel]:
        # obtener club del shooter
        shooter_query = select(ShooterModel.club_id).where(
            ShooterModel.user_id == shooter_id
        )
        shooter_result = db.execute(shooter_query)
        club_id = shooter_result.scalar_one_or_none()

        if not club_id:
            return []  # Sin club = sin instructores disponibles

        return InstructorRepository.get_instructors_by_club(db, club_id)

    @staticmethod
    def is_instructor_in_same_club(
        db: Session, instructor_id: UUID, shooter_id: UUID
    ) -> bool:
        # Verificar que instructor y shooter estén en el mismo club
        # query = (
        #     select(
        #         ShooterModel.club_id.label("instructor_club"),
        #         ShooterModel.club_id.label("shooter_club"),
        #     )
        #     .select_from(ShooterModel.alias("instructor_shooter"))
        #     .join(
        #         ShooterModel.alias("target_shooter"),
        #         ShooterModel.alias("instructor_shooter").c.club_id
        #         == ShooterModel.alias("target_shooter").c.club_id,
        #     )
        #     .where(
        #         and_(
        #             ShooterModel.alias("instructor_shooter").c.user_id == instructor_id,
        #             ShooterModel.alias("target_shooter").c.user_id == shooter_id,
        #         )
        #     )
        # )

        # Versión más simple y clara
        instructor_club_query = select(ShooterModel.club_id).where(
            ShooterModel.user_id == instructor_id
        )
        shooter_club_query = select(ShooterModel.club_id).where(
            ShooterModel.user_id == shooter_id
        )

        instructor_club = db.execute(instructor_club_query).scalar_one_or_none()
        shooter_club = db.execute(shooter_club_query).scalar_one_or_none()

        return (
            instructor_club is not None
            and shooter_club is not None
            and instructor_club == shooter_club
        )

    @staticmethod
    def validate_instructor_permission(db: Session, user_id: UUID) -> bool:
        query = select(UserModel).where(
            and_(
                UserModel.id == user_id,
                UserModel.role.in_(["INSTRUCTOR", "INSTRUCTOR_JEFE"]),
                UserModel.is_active == True,
            )
        )

        result = db.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    def get_instructor_basic_info(
        db: Session, instructor_id: UUID
    ) -> Optional[UserModel]:
        query = (
            select(UserModel)
            .where(
                UserModel.id == instructor_id,
            )
            .options(
                joinedload(UserModel.personal_data),
                joinedload(UserModel.shooter),
            )
        )
        result = db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def get_club_by_instructor(db: Session, instructor_id: UUID) -> Optional[UUID]:
        query = select(ShooterModel.club_id).where(
            ShooterModel.user_id == instructor_id
        )
        result = db.execute(query)
        return result.scalar_one_or_none()
