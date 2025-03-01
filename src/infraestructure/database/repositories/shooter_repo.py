from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from uuid import UUID
from src.infraestructure.database.models.shooter_model import ShooterModel
from src.infraestructure.database.models.user_model import UserModel

class ShooterRepository:
    @staticmethod
    def get_by_user_id(db:Session, user_id: UUID):
        return db.execute(select(ShooterModel).where(ShooterModel.user_id==user_id)).scalar_one_or_none()
        # return db.query(ShooterModel).options(
        #     joinedload(ShooterModel.user).joinedload(UserModel)
        # )

    @staticmethod
    def create(db: Session, shooter_data: ShooterModel):
        shooter = ShooterModel(**shooter_data.dict())
        db.add(shooter)
        db.commit()
        db.refresh(shooter)
        return shooter

    @staticmethod
    def get_all(db:Session):
        return db.query(ShooterModel).options(
            joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
            joinedload(ShooterModel.stats)
        ).all()
