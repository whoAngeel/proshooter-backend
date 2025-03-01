from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from src.infraestructure.database.models.shooter_stats_model import ShooterStatsModel
from src.presentation.schemas.user_stats_schema import ShooterStatsUpdate
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
    def edit(db: Session, shooter_id: UUID, data_in: ShooterStatsUpdate):
        shooter_stats = db.query(ShooterStatsModel).filter(ShooterStatsModel.shooter_id == shooter_id).first()

        if not shooter_stats:
            return None

        # actualizar los campos que no vienen vacios
        if data_in.total_shots:
            shooter_stats.total_shots = shooter_stats.shots
        if data_in.accuracy:
            shooter_stats.accuracy = shooter_stats.accuracy
        if data_in.average_hit_factor:
            shooter_stats.average_hit_factor = shooter_stats.average_hit_factor
        if data_in.effectiveness:
            shooter_stats.effectiveness = shooter_stats.effectiveness

        db.commit()
        db.refresh(shooter_stats)
        return shooter_stats
