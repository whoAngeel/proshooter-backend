from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from uuid import UUID
from src.infraestructure.database.models.shooter_model import ShooterModel
from src.infraestructure.database.models.user_model import UserModel
from src.infraestructure.database.models.shooter_stats_model import ShooterStatsModel
from src.domain.enums.role_enum import RoleEnum

class ShooterRepository:
    @staticmethod
    def get_by_user_id(db:Session, user_id: UUID):
        return db.execute(select(ShooterModel).where(ShooterModel.user_id==user_id)).scalar_one_or_none()

    @staticmethod
    def create(db: Session, user_id: UUID):
        shooter = ShooterModel(
            user_id = user_id
        )
        db.add(shooter)
        db.flush()
        # db.refresh(shooter)
        return shooter

    @staticmethod
    def get_all(db:Session):
        return db.query(ShooterModel).options(
            joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
            joinedload(ShooterModel.stats)
        ).all()

    @staticmethod
    def create_shooter_stats(db:Session, shooter_id: UUID):
        shooter = ShooterRepository.get_by_user_id(db, shooter_id)
        if not shooter:
            return None

        new_shooter_stats = ShooterStatsModel(
            user_id = shooter_id
        )

        db.add(new_shooter_stats)
        db.commit()
        db.refresh(new_shooter_stats)
        return new_shooter_stats
