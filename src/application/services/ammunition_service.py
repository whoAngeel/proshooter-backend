from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from src.domain.enums.ammo_enum import AmmoType
from src.infraestructure.database.repositories.ammunition_repo import AmmunitionRepository
from src.infraestructure.database.models.ammunition_model import AmmunitionModel
from src.infraestructure.database.session import get_db
from src.presentation.schemas.ammo_schema import AmmunitionCreate, AmmunitionRead, AmmunitionDetail, AmmunitionUpdate
from src.presentation.schemas.weapon_schema import WeaponRead

class AmmunitionService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_ammunition(self, ammunition_data: AmmunitionCreate)-> Tuple[Optional[AmmunitionRead], Optional[str]]:
        try:
            existing = self.db.query(AmmunitionModel).filter_by(
                name=ammunition_data.name,
                caliber=ammunition_data.caliber,
                brand=ammunition_data.brand
            ).first()

            if existing:
                return None, "AMMUNITION_ALREADY_EXISTS"

            ammunition_dict = ammunition_data.dict(exclude_unset=True)
            new_ammunition = AmmunitionRepository.create(self.db, ammunition_dict)

            self.db.commit()
            return AmmunitionRead.model_validate(new_ammunition), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_CREATING_AMMUNITION: {str(e)}"

    def get_ammunition_by_id(self, ammo_id: UUID)-> Tuple[Optional[AmmunitionRead], Optional[str]]:
        ammunition = AmmunitionRepository.get_by_id(self.db, ammo_id)
        if not ammunition:
            return None, "AMMUNITION_NOT_FOUND"
        return AmmunitionRead.model_validate(ammunition), None

    def get_ammunition_detail(self, ammo_id: UUID)-> Tuple[Optional[AmmunitionDetail], Optional[str]]:
        ammunition = AmmunitionRepository.get_by_id(self.db, ammo_id)
        if not ammunition:
            return None, "AMMUNITION_NOT_FOUND"
        return AmmunitionDetail.model_validate(ammunition), None

    def get_all_munition(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        ammo_type: Optional[AmmoType] = None,
        caliber: Optional[str] = None
    ) -> List[AmmunitionRead]:
        if ammo_type:
            ammunition = AmmunitionRepository.get_by_type(self.db, ammo_type)
        elif caliber:
            ammunition = AmmunitionRepository.get_by_caliber(self.db, caliber)
        else:
            ammunition = AmmunitionRepository.get_all(self.db, skip, limit, active_only)

        return [AmmunitionRead.model_validate(ammo) for ammo in ammunition]

    def search_ammunition(self, term: str)-> List[AmmunitionRead]:
        ammunition = AmmunitionRepository.search_by_term(self.db, term)
        return [AmmunitionRead.model_validate(ammo) for ammo in ammunition]

    def update_ammunition(
        self,
        ammo_id: UUID,
        ammunition_data: AmmunitionUpdate
    )-> Tuple[Optional[AmmunitionRead], Optional[str]]:
        try:
            # Verificar que la munición existe
            existing_ammunition = AmmunitionRepository.get_by_id(self.db, ammo_id=ammo_id)
            if not existing_ammunition:
                return None, "AMMUNITION_NOT_FOUND"

            # Verificar duplicados solo si se cambia alguno de estos campos
            if any([ammunition_data.name, ammunition_data.caliber, ammunition_data.brand]):
                name = ammunition_data.name or existing_ammunition.name
                caliber = ammunition_data.caliber or existing_ammunition.caliber
                brand = ammunition_data.brand or existing_ammunition.brand

                duplicate = self.db.query(AmmunitionModel).filter(
                    AmmunitionModel.name == name,
                    AmmunitionModel.caliber == caliber,
                    AmmunitionModel.brand == brand,
                    AmmunitionModel.id != ammo_id
                ).first()

                if duplicate:
                    return None, "AMMUNITION_WITH_SAME_NAME_AND_CALIBER_ALREADY_EXISTS"

            # Actualizar la munición
            ammunition_dict = ammunition_data.model_dump(exclude_unset=True, exclude_none=True)
            updated_ammunition = AmmunitionRepository.update(self.db, ammo_id, ammunition_dict)

            self.db.commit()

            return AmmunitionRead.model_validate(updated_ammunition), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPDATING_AMMUNITION: {str(e)}"

    def delete_ammunition(self, ammo_id: UUID, soft_delete: bool = True)-> Tuple[Optional[bool], Optional[str]]:
        try:
            existing_ammunition = AmmunitionRepository.get_by_id(self.db, ammo_id)
            if not existing_ammunition:
                return False, "AMMUNITION_NOT_FOUND"

            if soft_delete:
                AmmunitionRepository.deactivate(self.db, ammo_id)
            else:
                AmmunitionRepository.delete(self.db, ammo_id)

            self.db.commit()
            return True, None
        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_DELETING_AMMUNITION: {str(e)}"

    def get_compatible_weapons(self, ammunition_id: UUID) -> Tuple[Optional[List[WeaponRead]], Optional[str]]:
        ammunition = AmmunitionRepository.get_by_id(self.db, ammunition_id)
        if not ammunition:
            return None, "AMMUNITION_NOT_FOUND"

        weapons_list = AmmunitionRepository.get_compatible_weapons(self.db, ammunition_id)

        return [WeaponRead.model_validate(weapon) for weapon in weapons_list], None

    def get_ammunition_by_weapon(self, weapon_id: UUID) -> List[AmmunitionRead]:
        ammunition_list = AmmunitionRepository.get_by_weapon_id(self.db, weapon_id)
        return [AmmunitionRead.model_validate(ammo) for ammo in ammunition_list]
