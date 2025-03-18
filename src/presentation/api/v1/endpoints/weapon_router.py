from fastapi import APIRouter, Depends, Query, Body, Path ,HTTPException, status
from typing import List, Optional
from uuid import UUID

from src.application.services.weapon_service import WeaponService
from src.domain.enums.weapon_type_enum import WeaponTypeEnum
from src.presentation.schemas.weapon_schema import WeaponCreate, WeaponUpdate, WeaponDetail, WeaponRead
from src.presentation.schemas.ammo_schema import AmmunitionRead
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.user_schemas import UserRead
from src.domain.enums.role_enum import RoleEnum

router = APIRouter(prefix="/weapons", tags=["weapons"])

@router.post("/", response_model=WeaponRead, status_code=201)
async def create_weapon(
    weapon_data: WeaponCreate,
    weapon_service: WeaponService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo administradores pueden crear armas")

    weapon, error = weapon_service.create_weapon(weapon_data)

    if error:
        raise HTTPException(status_code=400, detail=error)

    return weapon

@router.get("/", response_model=List[WeaponRead])
async def get_all_weapons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    weapon_type: Optional[WeaponTypeEnum] = Query(None),
    caliber: Optional[str] = Query(None),
    weapon_service: WeaponService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    return weapon_service.get_all_weapons(skip, limit, active_only, weapon_type, caliber)

@router.get("/search", response_model=List[WeaponRead])
async def search_weapons(
    term: str = Query(..., description="Search term to find in name or description"),
    weapon_service: WeaponService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    return weapon_service.search_weapons(term)


@router.get("/{weapon_id}", response_model=WeaponDetail)
async def get_weapon_detail(
    weapon_id: UUID=Path(...),
    weapon_service: WeaponService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    weapon, error = weapon_service.get_weapon_detail(weapon_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return weapon

@router.put("/{weapon_id}", response_model=WeaponRead)
async def update_weapon(
    weapon_id: UUID = Path(...),
    weapon_data: WeaponUpdate = Body(...),
    weapon_service: WeaponService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo administradores pueden actualizar armas")

    weapon, error = weapon_service.update_weapon(weapon_id, weapon_data)
    if error:
        if error == "WEAPON_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return weapon

@router.delete("/{weapon_id}")
async def delete_weapon(
    weapon_id: UUID = Path(...),
    soft_delete: bool = Query(True),
    weapon_service: WeaponService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo administradores pueden eliminar armas")

    success, error = weapon_service.delete_weapon(weapon_id, soft_delete)
    if error:
        if error == "WEAPON_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {
        "message": "Arma eliminada correctamente",
        "id": weapon_id
    }

@router.get("/{weapon_id}/compatible-ammunition", response_model=List[AmmunitionRead])
async def get_compatible_ammunition(
    weapon_id: UUID = Path(...),
    weapon_service: WeaponService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    ammunition_list, error = weapon_service.get_compatible_ammunition(weapon_id)
    if error:
        if error == "WEAPON_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return ammunition_list

@router.post("/{weapon_id}/compatible-ammunition/{ammunition_id}")
async def add_compatible_ammunition(
    weapon_id: UUID = Path(...),
    ammunition_id: UUID = Path(...),
    weapon_service: WeaponService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo administradores pueden agregar municiones compatibles")

    success, error = weapon_service.add_compatible_ammunition(weapon_id, ammunition_id)
    if error:
        if error == "WEAPON_OR_AMMUNITION_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return {
        "message": "Municiones compatibles agregadas correctamente",
    }

@router.delete("/{weapon_id}/compatible-ammunition/{ammunition_id}")
async def remove_compatible_ammunition(
    weapon_id: UUID = Path(...),
    ammunition_id: UUID = Path(...),
    weapon_service: WeaponService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo administradores pueden eliminar municiones compatibles")

    success, error = weapon_service.remove_compatible_ammunition(weapon_id, ammunition_id)
    if error:
        if error == "COMPATIBILITY_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return {
        "message": "Municiones compatibles eliminadas correctamente",
    }
