from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional
from uuid import UUID

from src.application.services.ammunition_service import AmmunitionService
from src.infraestructure.auth.jwt_config import get_current_user
from src.domain.enums.ammo_enum import AmmoType
from src.presentation.schemas.ammo_schema import AmmunitionCreate, AmmunitionUpdate, AmmunitionDetail, AmmunitionRead
from src.presentation.schemas.weapon_schema import WeaponRead
from src.presentation.schemas.user_schemas import UserRead
from src.domain.enums.role_enum import RoleEnum

router = APIRouter(prefix="/ammunition", tags=["ammunition"])

@router.post("/", response_model=AmmunitionRead, status_code=201)
async def create_ammunition(
    ammunition_data: AmmunitionCreate,
    ammunition_service: AmmunitionService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo administradores pueden crear municiones")

    ammo, error = ammunition_service.create_ammunition(ammunition_data)

    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return ammo


@router.get("/", response_model=List[AmmunitionRead])
async def get_all_ammunition(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    ammo_type: Optional[AmmoType] = Query(None),
    caliber: Optional[str] = Query(None),
    ammunition_service: AmmunitionService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    return ammunition_service.get_all_munition(skip, limit, active_only, ammo_type, caliber)

@router.get("/search", response_model=List[AmmunitionRead])
async def search_ammunition(
    term: str = Query(..., description="Search term to find in name or description"),
    ammunition_service: AmmunitionService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    return ammunition_service.search_ammunition(term)

@router.get("/{ammunition_id}", response_model=AmmunitionDetail)
async def get_ammunition_detail(
    ammunition_id: UUID = Path(...),
    ammunition_service: AmmunitionService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    ammunition, error = ammunition_service.get_ammunition_detail(ammunition_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    return ammunition


@router.put("/{ammunition_id}", response_model=AmmunitionRead)
async def update_ammunition(
    ammunition_id: UUID = Path(...),
    ammunition_data: AmmunitionUpdate = Body(...),
    ammunition_service: AmmunitionService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo administradores pueden actualizar municiones")

    ammunition, error = ammunition_service.update_ammunition(ammunition_id, ammunition_data)

    if error:
        if error == "AMMUNITION_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return ammunition


@router.delete("/{ammunition_id}")
async def delete_ammunition(
    ammunition_id: UUID = Path(...),
    soft_delete: bool = Query(True),
    ammunition_service: AmmunitionService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo administradores pueden eliminar municiones")

    success, error = ammunition_service.delete_ammunition(ammunition_id, soft_delete)
    if error:
        if error == "AMMUNITION_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {
        "message": "Municion eliminada correctamente",
        "id": ammunition_id
    }

@router.get("/{ammunition_id}/compatible-weapons", response_model=List[WeaponRead])
async def get_compatible_weapons(
    ammunition_id: UUID = Path(...),
    ammunition_service: AmmunitionService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    weapons_list, error = ammunition_service.get_compatible_weapons(ammunition_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    return weapons_list

@router.get("/for-weapon/{weapon_id}", response_model=List[AmmunitionRead])
async def get_ammunition_for_weapon(
    weapon_id: UUID = Path(...),
    ammunition_service: AmmunitionService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    return ammunition_service.get_ammunition_by_weapon(weapon_id)
