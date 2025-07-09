from fastapi import APIRouter, Depends, HTTPException, Body
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
    UserRead
    )

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = UserService.create_user(db, user_in)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return user

@router.get("/", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    return UserService.get_users(db)

@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(user_id: UUID, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden realizar esta acción")
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return user

@router.patch("/{user_id}/toggle-active")
def toggle_active(user_id: UUID, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Solo los administradores pueden realizar esta acción")

    user = UserService.toggle_active(db, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario no existe")
    return {
        # "id": user.id,
        "message": f"El usuario ha sido actualizado a {'activo' if user.is_active else 'inactivo'}",
        "id": user.id
    }

#
