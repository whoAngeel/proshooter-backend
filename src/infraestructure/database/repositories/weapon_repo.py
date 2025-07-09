from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.infraestructure.database.models.weapon_model import WeaponModel
from src.domain.enums.weapon_type_enum import WeaponTypeEnum
# from src.infraestructure.database.models.weapon_ammunition_copmatibility_model import WeaponAmmunitionCompatibilityModel
# from src.infraestructure

class WeaponRepository:
    @staticmethod
    def create(db: Session, weapon_data: dict) -> WeaponModel:
        weapon = WeaponModel(**weapon_data)
        db.add(weapon)
        db.flush()
        return weapon

    @staticmethod
    def get_by_id(db: Session, weapon_id: UUID) -> Optional[WeaponModel]:
        return db.query(WeaponModel).filter(WeaponModel.id == weapon_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[WeaponModel]:
        query = db.query(WeaponModel)

        if active_only:
            query = query.filter(WeaponModel.is_active == True)

        return query.order_by(WeaponModel.name).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_type(db: Session, weapon_type: WeaponTypeEnum) -> List[WeaponModel]:
        return db.query(WeaponModel).filter(WeaponModel.weapon_type == weapon_type).all()

    @staticmethod
    def get_by_caliber(db: Session, caliber: str)-> List[WeaponModel]:
        return db.query(WeaponModel).filter(WeaponModel.caliber == caliber).all()

    @staticmethod
    def search_by_term(db: Session, term: str) -> List[WeaponModel]:
        search_pattern = f"%{term}%"

        return db.query(WeaponModel).filter(
            or_(
                WeaponModel.name.ilike(search_pattern),
                WeaponModel.brand.ilike(search_pattern),
                WeaponModel.model.ilike(search_pattern),
                WeaponModel.serial_number.ilike(search_pattern),
                WeaponModel.description.ilike(search_pattern),
                WeaponModel.caliber.ilike(search_pattern)
            )
        ).order_by(WeaponModel.name).all()

    @staticmethod
    def update(db: Session, weapon_id: UUID, weapon_data: dict)-> Optional[WeaponModel]:
        weapon = WeaponRepository.get_by_id(db, weapon_id)
        if not weapon:
            return None

        for key, value in weapon_data.items():
            setattr(weapon, key, value)

        db.flush()
        return weapon

    @staticmethod
    def delete(db: Session, weapon_id: UUID)-> bool:
        """
        Elimina un arma de la base de datos.

        Args:
            db (Session): Sesión de base de datos.
            weapon_id (UUID): ID del arma a eliminar.

        Returns:
            bool: True si el arma fue eliminada, False si no existe.
        """
        weapon = WeaponRepository.get_by_id(db, weapon_id)
        if not weapon:
            return False
        db.delete(weapon)
        return True

    @staticmethod
    def desactivate(db: Session, weapon_id: UUID)-> Optional[WeaponModel]:
        weapon = WeaponRepository.get_by_id(db, weapon_id)
        if not weapon:
            return None
        weapon.is_active = False
        db.flush()
        return weapon

    @staticmethod # TODO: Implement
    def get_compatible_ammunition(db: Session, weapon_id: UUID)-> List:
        weapon = WeaponRepository.get_by_id(db, weapon_id)
        if not weapon:
            return []

        return weapon.compatible_ammunition

    @staticmethod
    def add_compatible_ammunition(db: Session, weapon_id: UUID, ammunition_id: UUID) -> bool:
        from src.infraestructure.database.repositories.ammunition_repo import AmmunitionRepository

        weapon = WeaponRepository.get_by_id(db, weapon_id)
        ammunition = AmmunitionRepository.get_by_id(db, ammunition_id)

        if not weapon or not ammunition:
            return False

        if ammunition in weapon.compatible_ammunition:
            return True  # Ya existe la compatibilidad

        weapon.compatible_ammunition.append(ammunition)
        db.flush()
        return True

    @staticmethod
    def remove_compatible_ammunition(db: Session, weapon_id: UUID, ammunition_id: UUID) -> bool:
        from src.infraestructure.database.repositories.ammunition_repo import AmmunitionRepository

        weapon = WeaponRepository.get_by_id(db, weapon_id)
        ammunition = AmmunitionRepository.get_by_id(db, ammunition_id)

        if not weapon or not ammunition:
            return False

        if ammunition not in weapon.compatible_ammunition:
            return False  # No existe la compatibilidad

        weapon.compatible_ammunition.remove(ammunition)
        db.flush()
        return True

    @staticmethod
    def get_by_ammunition_id(db: Session, ammunition_id: UUID) -> List[WeaponModel]:
        from src.infraestructure.database.models.weapon_model import WeaponModel
        from src.infraestructure.database.models.weapon_ammunition_compatibility_model import WeaponAmmunitionCompatibilityModel

        return db.query(WeaponModel).join(
            WeaponAmmunitionCompatibilityModel,
            WeaponModel.id == WeaponAmmunitionCompatibilityModel.weapon_id
        ).filter(
            WeaponAmmunitionCompatibilityModel.ammunition_id == ammunition_id
        ).all()

    @staticmethod
    def get_by_type_name(db: Session, type_name: str) -> List[WeaponModel]:
        try:
            enum_member = WeaponTypeEnum.from_string(type_name)
            return db.query(WeaponModel).filter(WeaponModel.weapon_type == enum_member).all()
        except ValueError:
            return []

    @staticmethod
    def check_compatibility(db: Session, weapon_id: UUID, ammunition_id: UUID) -> bool:
        from src.infraestructure.database.models.weapon_ammunition_compatibility_model import WeaponAmmunitionCompatibilityModel

        return db.query(WeaponAmmunitionCompatibilityModel).filter(
            WeaponAmmunitionCompatibilityModel.weapon_id == weapon_id,
            WeaponAmmunitionCompatibilityModel.ammunition_id == ammunition_id
        ).first() is not None
