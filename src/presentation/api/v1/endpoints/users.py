from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from uuid import UUID

from src.application.services.user_service import UserService
from src.infraestructure.database.session import get_db
from src.domain.enums.role_enum import RoleEnum
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.user_schemas import (
    UserBiometricDataCreate,
    UserBiometricDataUpdate,
    UserCreate,
    UserMedicalDataCreate,
    UserMedicalDataUpdate,
    UserPersonalDataCreate,
    UserPersonalDataUpdate,
    UserRead,
    UserFilter,
    UserList,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = UserService.create_user(db, user_in)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return user


@router.get("/", response_model=UserList)
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    filter_params = UserFilter(skip=skip, limit=limit)
    users = UserService.get_all_users(db, filter_params)
    return users


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden realizar esta acción",
        )
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return user


@router.patch("/{user_id}/toggle-active")
def toggle_active(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden realizar esta acción",
        )

    user = UserService.toggle_active(db, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario no existe")
    return {
        # "id": user.id,
        "message": f"El usuario ha sido actualizado a {'activo' if user.is_active else 'inactivo'}",
        "id": user.id,
    }


#
