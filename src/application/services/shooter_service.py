from sqlalchemy.orm import Session
from uuid import UUID

from src.infraestructure.database.repositories.shooter_repo import ShooterRepository

from src.presentation.schemas.shooter_schema import ShooterCreate

class ShooterService:
    @staticmethod
    def get_shooters(db: Session):
        return ShooterRepository.get_all(db)

    @staticmethod
    def create_shooter(db: Session, user_id: UUID, shooter_data: ShooterCreate):
        existing_shooter = ShooterRepository.get_by_user_id(db, user_id)
        if existing_shooter:
            return None, "SHOOTER_ALREADY_EXISTS"
        return ShooterRepository.create(db, shooter_data), None

    @staticmethod
    def get_shooter_by_user_id(db: Session, user_id: UUID):
        return ShooterRepository.get_by_user_id(db, user_id)
