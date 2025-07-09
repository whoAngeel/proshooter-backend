from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.infraestructure.database.models.ammunition_model import AmmunitionModel
from src.domain.enums.ammo_enum import AmmoType

class AmmunitionRepository:
    @staticmethod
    def create(db: Session, ammunition_data: dict) -> AmmunitionModel:
        ammunition = AmmunitionModel(**ammunition_data)
        db.add(ammunition)
        db.flush()
        return ammunition

    @staticmethod
    def get_by_id(db: Session, ammo_id: UUID) -> Optional[AmmunitionModel]:
        return db.query(AmmunitionModel).filter(AmmunitionModel.id == ammo_id).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[AmmunitionModel]:
        query = db.query(AmmunitionModel)

        if active_only:
            query = query.filter(AmmunitionModel.is_active == True)

        return query.order_by(AmmunitionModel.name).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_type(db: Session, ammo_type: AmmoType) -> List[AmmunitionModel]:
        return db.query(AmmunitionModel).filter(AmmunitionModel.ammo_type == ammo_type).all()

    @staticmethod
    def get_by_caliber(db: Session, caliber: str) -> List[AmmunitionModel]:
        return db.query(AmmunitionModel).filter(AmmunitionModel.caliber == caliber).all()

    @staticmethod
    def search_by_term(db: Session, term: str) -> List[AmmunitionModel]:
        search_pattern = f"%{term}%"

        return db.query(AmmunitionModel).filter(
            or_(
                AmmunitionModel.name.ilike(search_pattern),
                AmmunitionModel.brand.ilike(search_pattern),
                AmmunitionModel.caliber.ilike(search_pattern),
                AmmunitionModel.description.ilike(search_pattern)
            )
        ).order_by(AmmunitionModel.name).all()

    @staticmethod
    def update(db: Session, ammo_id: UUID, ammunition_data: dict) -> Optional[AmmunitionModel]:
        ammunition = AmmunitionRepository.get_by_id(db, ammo_id)
        if not ammunition:
            return None

        for key, value in ammunition_data.items():
            setattr(ammunition, key, value)

        db.flush()
        return ammunition

    @staticmethod
    def delete(db: Session, ammo_id: UUID) -> bool:
        ammunition = AmmunitionRepository.get_by_id(db, ammo_id)
        if not ammunition:
            return False
        db.delete(ammunition)
        return True

    @staticmethod
    def desactivate(db: Session, ammo_id: UUID) -> Optional[AmmunitionModel]:
        ammunition = AmmunitionRepository.get_by_id(db, ammo_id)
        if not ammunition:
            return None
        ammunition.is_active = False
        db.flush()
        return ammunition

    @staticmethod
    def get_compatible_weapons(db: Session, ammo_id: UUID) -> List:
        ammunition = AmmunitionRepository.get_by_id(db, ammo_id)
        if not ammunition:
            return []

        return ammunition.compatible_weapons

    @staticmethod
    def get_by_weapon_id(db: Session, weapon_id: UUID) -> List[AmmunitionModel]:
        from src.infraestructure.database.models.weapon_model import WeaponModel
        from src.infraestructure.database.models.weapon_ammunition_compatibility_model import WeaponAmmunitionCompatibilityModel

        return db.query(AmmunitionModel).join(
            WeaponAmmunitionCompatibilityModel,
            AmmunitionModel.id == WeaponAmmunitionCompatibilityModel.ammunition_id
        ).filter(
            WeaponAmmunitionCompatibilityModel.weapon_id == weapon_id
        ).all()
