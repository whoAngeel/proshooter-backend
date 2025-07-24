from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from src.infraestructure.database.models.shooter_stats_model import ShooterStatsModel
from src.presentation.schemas.user_stats_schema import ShooterStatsUpdate
from src.infraestructure.database.models.practice_session_model import (
    IndividualPracticeSessionModel,
)


class ShooterStatsRepository:
    @staticmethod
    def create(db: Session, shooter_id: UUID):
        existing_stats = db.execute(
            select(ShooterStatsModel).where(ShooterStatsModel.shooter_id == shooter_id)
        ).scalar_one_or_none()

        if existing_stats:
            return None

        new_shooter_stats = ShooterStatsModel(shooter_id=shooter_id)

        db.add(new_shooter_stats)
        db.flush()
        return new_shooter_stats

    @staticmethod
    def update(db: Session, shooter_id: UUID, updates: dict):
        """
        Actualiza estadísticas del tirador con un diccionario de campos
        """
        try:
            shooter_stats = (
                db.query(ShooterStatsModel)
                .filter(ShooterStatsModel.shooter_id == shooter_id)
                .first()
            )

            if not shooter_stats:
                return None

            # Actualizar solo campos que existen en el modelo
            for key, value in updates.items():
                if hasattr(shooter_stats, key):
                    setattr(shooter_stats, key, value)

            db.commit()
            db.refresh(shooter_stats)
            return shooter_stats

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_by_shooter_id(db: Session, shooter_id: UUID):
        return (
            db.query(ShooterStatsModel)
            .filter(ShooterStatsModel.shooter_id == shooter_id)
            .first()
        )

    # TODO: implementar metodo para cambiar el nivel ()
