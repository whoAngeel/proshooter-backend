from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path, status
from sqlalchemy.orm import Session
from uuid import UUID
import json
from typing import List, Optional

from src.application.services.user_service import UserService
from src.application.services.shooter_service import ShooterService
from src.application.services.practice_session_service import PracticeSessionService
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
    nickname: str = Body(..., embed=True, min_length=3, max_length=20),
    shooter_service: ShooterService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.id
    updated_shooter, error_code = shooter_service.update_shooter_nickname(
        user_id, nickname
    )
    if error_code == "SHOOTER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="El tirador no existe")
    if error_code == "NICKNAME_ALREADY_EXISTS":
        raise HTTPException(status_code=400, detail="El apodo ya está en uso")
    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="El usuario no existe")
    if error_code:
        raise HTTPException(status_code=500, detail=error_code)
    return {"message": "Apodo actualizado correctamente", "data": updated_shooter}


from fastapi import File, UploadFile


@router.patch("/shooter-license-file")
async def update_shooter_license_file(
    file: UploadFile = File(...),
    shooter_service: ShooterService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.id

    from src.infraestructure.utils.s3_utils import upload_file_to_s3

    bucket_name = "proshooter"
    try:
        file_url = upload_file_to_s3(
            file,
            bucket_name=bucket_name,
            folder="licenses",
            allowed_types=["image/png", "image/jpeg", "application/pdf"],
        )

        updated_shooter, error_code = shooter_service.update_licence_file(
            user_id, file_url
        )
        if error_code == "SHOOTER_NOT_FOUND":
            raise HTTPException(status_code=404, detail="El tirador no existe")
        if error_code == "INVALID_FILE_URL":
            raise HTTPException(status_code=400, detail="URL del archivo inválida")
        if error_code == "ERROR_UPDATING_LICENSE_FILE":
            raise HTTPException(
                status_code=404, detail="Error al actualizar el archivo de licencia"
            )
        if error_code:
            raise HTTPException(status_code=500, detail=error_code)
        return {
            "message": "Archivo de licencia actualizado correctamente",
            "license_file": file_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


from src.presentation.schemas.practice_session_schema import MyPracticeSessionList


@router.get("/my-sessions/", response_model=MyPracticeSessionList)
async def get_my_sessions(
    is_finished: Optional[bool] = Query(
        None, description="Filtrar por sesiones finalizadas"
    ),
    skip: int = Query(0, ge=0, description="Número de sesiones a omitir"),
    limit: int = Query(
        5, ge=1, le=100, description="Número máximo de sesiones a retornar"
    ),
    practice_session_service: PracticeSessionService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtener las sesiones de práctica del usuario autenticado.
    Args:
        is_finished (bool): Filtrar por sesiones finalizadas.
        practice_session_service (PracticeSessionService): Servicio para manejar sesiones de práctica.
        current_user (dict): Usuario actual obtenido del token JWT.

    Returns:
        dict: Lista de sesiones de práctica del usuario.
    """
    user_id = current_user.id
    try:
        sessions = practice_session_service.get_my_sessions(
            user_id=user_id, is_finished=is_finished, skip=skip, limit=limit
        )
        total = len(sessions)  # Total de la lista mostrada (paginada)
        return {"sessions": sessions, "total": total}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
