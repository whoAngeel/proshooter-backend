from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from src.domain.enums.weapon_type_enum import WeaponTypeEnum
from src.infraestructure.database.models.weapon_model import WeaponModel
from src.infraestructure.database.repositories.weapon_repo import WeaponRepository
from src.infraestructure.database.session import get_db
from src.presentation.schemas.weapon_schema import (
    WeaponCreate,
    WeaponUpdate,
    WeaponRead,
    WeaponDetail,
)


class WeaponService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db


    def create_weapon(self, weapon_data: WeaponCreate)-> Tuple[Optional[WeaponRead], Optional[str]]:
        try:
            # verificar si ya existe un arma con el mismo nombre
            existing_weapons = self.db.query(WeaponModel).filter_by(serial_number=weapon_data.serial_number).first()
            if existing_weapons:
                return None, "WEAPON_WITH_SAME_SERIAL_NUMBER_ALREADY_EXISTS"

            # Crear el arma
            weapon_dict = weapon_data.model_dump(exclude_unset=True)
            new_weapon = WeaponRepository.create(self.db, weapon_dict)

            self.db.commit()

            return WeaponRead.model_validate(new_weapon), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_CREATING_WEAPON: {str(e)}"

    def get_weapon_by_id(self, weapon_id: UUID) -> Tuple[Optional[WeaponRead], Optional[str]]:
        try:
            weapon = WeaponRepository.get_by_id(self.db, weapon_id)
            if not weapon:
                return None, "WEAPON_NOT_FOUND"
            return WeaponRead.model_validate(weapon), None
        except Exception as e:
            return None, f"ERROR_GETTING_WEAPON: {str(e)}"

    def get_weapon_detail(self, weapon_id: UUID) -> Tuple[Optional[WeaponDetail], Optional[str]]:
        try:
            weapon = WeaponRepository.get_by_id(self.db, weapon_id)
            if not weapon:
                return None, "WEAPON_NOT_FOUND"
            return WeaponDetail.model_validate(weapon), None
        except Exception as e:
            return None, f"ERROR_GETTING_WEAPON: {str(e)}"

    def get_all_weapons(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        weapon_type: Optional[WeaponTypeEnum] = None,
        caliber: Optional[str] = None
    ) -> List[WeaponRead]:
        if weapon_type:
            weapons =- WeaponRepository.get_by_type(self.db, weapon_type)
        elif caliber:
            weapons = WeaponRepository.get_by_caliber(self.db, caliber)
        else:
            weapons = WeaponRepository.get_all(self.db, skip, limit, active_only)

        return  [WeaponRead.model_validate(weapon) for weapon in weapons]

    def search_weapons(self, term: str)-> List[WeaponRead]:
        weapons = WeaponRepository.search_by_term(self.db, term)
        return [WeaponRead.model_validate(weapon) for weapon in weapons]

    def update_weapon(
        self,
        weapon_id: UUID,
        weapon_data: WeaponUpdate,
    ) -> Tuple[Optional[WeaponRead], Optional[str]]:
        try:
            existing_weapon = WeaponRepository.get_by_id(self.db, weapon_id)
            if not existing_weapon:
                return None, "WEAPON_NOT_FOUND"

            if weapon_data.serial_number and weapon_data.serial_number != existing_weapon.serial_number:
                duplicate = self.db.query(WeaponModel).filter_by(serial_number=weapon_data.serial_number).first()
                if duplicate:
                    return None, "WEAPON_WITH_SAME_SERIAL_NUMBER_ALREADY_EXISTS"

            weapon_dict = weapon_data.model_dump(exclude_unset=True)
            updated_weapon = WeaponRepository.update(self.db, weapon_id, weapon_dict)

            self.db.commit()

            return WeaponRead.model_validate(updated_weapon), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPDATING_WEAPON: {str(e)}"

    def delete_weapon(self, weapon_id: UUID, soft_delete: bool = True) -> Tuple[bool, Optional[str]]:
        try:
            existing_weapon = WeaponRepository.get_by_id(self.db, weapon_id)
            if not existing_weapon:
                return False, "WEAPON_NOT_FOUND"

            if soft_delete:
                WeaponRepository.desactivate(self.db, weapon_id)
            else:
                WeaponRepository.delete(self.db, weapon_id)

            self.db.commit()
            return True, None

        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_DELETING_WEAPON: {str(e)}"

    def get_compatible_ammunition(self, weapon_id: UUID)-> Tuple[Optional[List], Optional[str]]:
        weapon = WeaponRepository.get_by_id(self.db, weapon_id)
        if not weapon:
            return None, "WEAPON_NOT_FOUND"
        ammunition_list = WeaponRepository.get_compatible_ammunition(self.db, weapon_id)

        # from src.presentation.schemas
        # TODO : implementar el retorno de la municion compatible

    def add_compatible_ammunition(
        self,
        weapon_id: UUID,
        ammunition_id: UUID,
    )-> Tuple[bool, Optional[str]]:
        try:
            # TODO : implementar la logica para agregar municion compatible
            pass
        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_ADDING_AMMUNITION: {str(e)}"

    def remove_compatible_ammunition(
        self,
        weapon_id: UUID,
        ammunition_id: UUID,
    )-> Tuple[bool, Optional[str]]:
        try:
            # TODO : implementar la logica para quitar municion compatible
            pass
        except Exception as e:
            self.db.rollback()
