from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path, status
from sqlalchemy.orm import Session
from uuid import UUID
import json

from src.application.services.user_service import UserService
from src.application.services.shooter_service import ShooterService
from src.infraestructure.auth.jwt_config import get_current_user
from src.infraestructure.database.session import get_db
from src.presentation.schemas.user_schemas import (
    UserBiometricDataCreate,
    UserBiometricDataUpdate,
    UserMedicalDataCreate,
    UserMedicalDataUpdate,
    UserPersonalDataCreate,
    UserPersonalDataUpdate,
    UserRead,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserRead)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Obtener los datos del usuario autenticado
    Args:
        current_user (dict): Usuario actual obtenido del token JWT.

    Returns:
        dict: Datos del usuario autenticado.
    """
    return current_user


# * ------ PERSONAL DATA ------
@router.post("/personal-data")
async def create_personal_data(
    data_in: UserPersonalDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.id
    personal_data, error_code = UserService.create_personal_data(db, user_id, data_in)
    if error_code == "PERSONAL_DATA_ALREADY_EXISTS":
        raise HTTPException(status_code=400, detail=error_code)
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=400, detail=error_code)
    if error_code:
        raise HTTPException(status_code=500, detail=error_code)
    return {"message": "Datos personales creados", "data": personal_data}


@router.patch("/personal-data")
async def update_biometric_data(
    data_in: UserPersonalDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = current_user.id
    personal_data, error_code = UserService.update_personal_data(
        db, current_user_id, data_in
    )
    if error_code == "PERSONAL_DATA_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_code)
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_code)
    if error_code:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_code
        )
    return {"message": "Datos personales actualizados", "data": personal_data}


# * ------ MEDICAL DATA ------
@router.post("/medical-data")
async def create_medical_data(
    data_in: UserMedicalDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.id
    medical_data, error_code = UserService.create_medical_data(db, user_id, data_in)
    if error_code == "MEDICAL_DATA_ALREADY_EXISTS":
        raise HTTPException(status_code=400, detail="Los datos médicos ya existen")
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=400, detail="El usuario no existe")
    if error_code:
        raise HTTPException(status_code=500, detail=error_code)
    return {"message": "Datos médicos creados", "data": medical_data}


@router.patch("/medical-data")
def update_medical_data(
    data_in: UserMedicalDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.id
    medical_data, error_code = UserService.update_medical_data(db, user_id, data_in)
    if error_code == "MEDICAL_DATA_NOT_FOUND":
        raise HTTPException(status_code=400, detail="Los datos médicos no existen")
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=400, detail="El usuario no existe")
    if error_code:
        raise HTTPException(status_code=500, detail=error_code)
    return {"message": "Datos médicos actualizados", "data": medical_data}


# * ------ BIO METRIC DATA ------
@router.post("/biometric-data")
def add_biometric_data(
    data_in: UserBiometricDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.id
    biometric_data, error_code = UserService.create_biometric_data(db, user_id, data_in)
    if error_code == "BIO_METRIC_DATA_ALREADY_EXISTS":
        raise HTTPException(status_code=400, detail="Los datos biometricos ya existen")
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=400, detail="El usuario no existe")
    if error_code:
        raise HTTPException(status_code=500, detail=error_code)
    return {"message": "Datos biometricos creados", "data": biometric_data}


@router.patch("/biometric-data")
def update_biometric_data(
    data_in: UserBiometricDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.id
    biometric_data, error_code = UserService.update_biometric_data(db, user_id, data_in)
    if error_code == "BIO_METRIC_DATA_NOT_FOUND":
        raise HTTPException(status_code=400, detail="Los datos biometricos no existen")
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=400, detail="El usuario no existe")
    if error_code:
        raise HTTPException(status_code=500, detail=error_code)
    return {"message": "Datos biometricos actualizados", "data": biometric_data}


# *------- SHOOTER DATA -------


@router.patch("/shooter-nickname")
def update_shooter_nickname(
    db: Session = Depends(get_db),
    nickname: str = Body(..., embed=True, min_length=3, max_length=20),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.id
    service = ShooterService()
    updated_shooter, error_code = service.update_shooter_nickname(db, user_id, nickname)
    if error_code == "SHOOTER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="El tirador no existe")
    if error_code == "NICKNAME_ALREADY_EXISTS":
        raise HTTPException(status_code=400, detail="El apodo ya está en uso")
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="El usuario no existe")
    if error_code:
        raise HTTPException(status_code=500, detail=error_code)
    return {"message": "Apodo actualizado correctamente", "data": updated_shooter}
