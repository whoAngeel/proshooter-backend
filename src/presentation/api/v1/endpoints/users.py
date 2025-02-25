from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.application.services.user_service import UserService
from src.infraestructure.database.session import get_db
from src.presentation.schemas.user_schemas import (
    UserCreate,
    UserRead,
    UserPersonalDataCreate,
    UserMedicalDataCreate,
    UserBiometricDataCreate,
    UserPersonalDataUpdate,
    UserMedicalDataUpdate
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
def get_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return user

@router.patch("/{user_id}", response_model=UserRead)
def toggle_active(user_id: UUID, db: Session = Depends(get_db)):
    user = UserService.toggle_active(db, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario no existe")
    return user

#* ------ PERSONAL DATA ------
@router.post("/{user_id}/personal_data")
def create_personal_data(user_id: UUID, data_in: UserPersonalDataCreate, db: Session = Depends(get_db)):
    personal_data, error_code = UserService.create_personal_data(db, user_id, data_in)
    if error_code == "PERSONAL_DATA_ALREADY_EXISTS":
        raise HTTPException(status_code=400, detail="Los datos personales ya existen")
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=400, detail="El usuario no existe")
    return personal_data

@router.patch("/{user_id}/personal_data")
def update_personal_data(user_id: UUID, data_in: UserPersonalDataUpdate, db: Session = Depends(get_db)):
    personal_data, error_code = UserService.update_personal_data(db, user_id, data_in)
    if error_code == "PERSONAL_DATA_NOT_FOUND":
        raise HTTPException(status_code=400, detail="Los datos personales no existen")
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=400, detail="El usuario no existe")
    return personal_data


#* ------ MEDICAL DATA ------
@router.post("/{user_id}/medical_data")
def add_medical_data(user_id: UUID, data_in: UserMedicalDataCreate, db: Session = Depends(get_db)):
    medical_data, error_code = UserService.create_medical_data(db, user_id, data_in)
    if error_code == "MEDICAL_DATA_ALREADY_EXISTS":
        raise HTTPException(status_code=400, detail="Los datos médicos ya existen")
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=400, detail="El usuario no existe")
    return {"message": "Datos médicos creados", "data": medical_data}

@router.patch("/{user_id}/medical_data")
def update_medical_data(user_id: UUID, data_in: UserMedicalDataUpdate, db: Session = Depends(get_db)):
    medical_data, error_code = UserService.update_medical_data(db, user_id, data_in)
    if error_code == "MEDICAL_DATA_ALREADY_EXISTS":
        raise HTTPException(status_code=400, detail="Los datos médicos no existen")
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=400, detail="El usuario no existe")
    return {"message": "Datos médicos actualizados", "data": medical_data}


#* ------ BIOMETRIC DATA ------

@router.post("/{user_id}/biometric_data")
def add_biometric_data(user_id: UUID, data_in: UserBiometricDataCreate, db: Session = Depends(get_db)):
    user = UserService.add_biometric_data(db, user_id, data_in)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return user
