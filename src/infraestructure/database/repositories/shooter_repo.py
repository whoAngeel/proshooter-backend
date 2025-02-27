from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from src.infraestructure.database.models.shooter_model import ShooterModel

class ShooterRepository:
    @staticmethod
    def get_by_user_id(db:Session, user_id: UUID):
        return db.execute(select(ShooterModel).where(ShooterModel.user_id==user_id)).scalar_one_or_none()

    @staticmethod
    def create(db: Session, shooter_data: ShooterModel):
        shooter = ShooterModel(**shooter_data.dict())
        db.add(shooter)
        db.commit()
        db.refresh(shooter)
        return shooter

    @staticmethod
    def get_all(db:Session):
        return db.execute(select(ShooterModel)).scalars().all()
