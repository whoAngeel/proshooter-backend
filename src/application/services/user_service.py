from sqlalchemy.orm import Session
from passlib.context import CryptContext
from uuid import UUID
import math

from src.infraestructure.database.repositories.user_repo import (
    UserBiometricDataRepository,
    UserMedicalDataRepository,
    UserRepository,
    UserPersonalDataRepository,
)
from src.presentation.schemas.user_schemas import (
    UserBiometricDataCreate,
    UserCreate,
    UserMedicalDataCreate,
    UserMedicalDataUpdate,
    UserPersonalDataCreate,
    UserPersonalDataUpdate,
    UserFilter,
    UserList,
    UserRead,
)
from fastapi import HTTPException
from src.domain.enums.role_enum import RoleEnum
from src.application.services.shooter_service import ShooterRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate):
        try:
            existing_user = UserRepository.get_by_email(db, user_data.email)
            if existing_user:
                return None, "USER_ALREADY_EXISTS"
            hashed_password = pwd_context.hash(user_data.password)
            user = UserRepository.register(db, user_data, hashed_password)
            return user, None
        except Exception as e:
            return None, f"ERROR_CREATING_USER: {str(e)}"

    @staticmethod
    def get_user(db: Session, user_id: UUID):
        return UserRepository.get_by_id(db, user_id)

    @staticmethod
    def get_all_users(db: Session, filter_params: UserFilter):
        try:
            filter_dict = filter_params.model_dump(exclude_unset=True)

            users = UserRepository.search_by_combined_criteria(
                db, filter_dict, filter_params.skip, filter_params.limit
            )

            total = UserRepository.count_by_criteria(db, filter_dict)

            page = (filter_params.skip // filter_params.limit) + 1
            pages = math.ceil(total / filter_params.limit) if total > 0 else 1

            items = [UserRead.model_validate(user) for user in users]

            return UserList(
                users=items,
                total=total,
                page=page,
                size=filter_params.limit,
                pages=pages,
            )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al obtener los usuarios: {str(e)}"
            )

    @staticmethod
    def get_users(db: Session):
        return UserRepository.get_all(db)

    @staticmethod
    def toggle_active(db: Session, user_id: UUID):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None
        return UserRepository.toggle_active(db, user_id)

    @staticmethod
    def promote_role(db: Session, user_id: UUID, new_role: str):
        """
        Servicio para promover el rol de un usuario.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario a promover
            new_role: Nuevo rol al que se quiere promover

        Returns:
            Tupla (usuario_actualizado, mensaje_error)
        """
        return UserRepository.promote_role(db, user_id, new_role)

    # TODO: validar los requisitos para promover a un tirador

    # Verificar si tiene registro como tirador

    @staticmethod
    def create_personal_data(
        db: Session, user_id: UUID, data_in: UserPersonalDataCreate
    ):
        try:
            user = UserRepository.get_by_id(db, user_id)
            if not user:
                return None, "USER_NOT_FOUND"

            existing_data = UserPersonalDataRepository.get_by_user_id(db, user_id)
            if existing_data:
                return None, "PERSONAL_DATA_ALREADY_EXISTS"

            created_data = UserPersonalDataRepository.create(db, user_id, data_in)
            return created_data, None
        except Exception as e:
            return None, f"ERROR_CREATING_PERSONAL_DATA: {str(e)}"

    @staticmethod
    def update_personal_data(
        db: Session, user_id: UUID, data_in: UserPersonalDataUpdate
    ):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None, "USER_NOT_FOUND"

        updated_data = UserPersonalDataRepository.update(db, user_id, data_in)
        if not updated_data:
            return None, "PERSONAL_DATA_NOT_FOUND"
        return updated_data, None

    @staticmethod
    def create_medical_data(db: Session, user_id: UUID, data_in: UserMedicalDataCreate):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None, "USER_NOT_FOUND"
        existing_data = UserMedicalDataRepository.get_by_user_id(db, user_id)
        if existing_data:
            return None, "MEDICAL_DATA_ALREADY_EXISTS"
        created_data = UserMedicalDataRepository.create(db, user_id, data_in)
        return created_data, None

    @staticmethod
    def update_medical_data(db: Session, user_id: UUID, data_in: UserMedicalDataUpdate):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None, "USER_NOT_FOUND"
        updated_medical_data = UserMedicalDataRepository.update(db, user_id, data_in)
        if not updated_medical_data:
            return None, "MEDICAL_DATA_NOT_FOUND"

        return updated_medical_data, None

    @staticmethod
    def create_biometric_data(
        db: Session, user_id: UUID, data_in: UserBiometricDataCreate
    ):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None, "USER_NOT_FOUND"
        existing_biometric_data = UserBiometricDataRepository.get_by_user_id(
            db, user_id
        )
        if existing_biometric_data:
            return None, "BIO_METRIC_DATA_ALREADY_EXISTS"
        new_biometric_data = UserBiometricDataRepository.create(db, user_id, data_in)
        return new_biometric_data, None

    @staticmethod
    def update_biometric_data(
        db: Session, user_id: UUID, data_in: UserBiometricDataCreate
    ):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None, "USER_NOT_FOUND"
        updated_biometric_data = UserBiometricDataRepository.update(
            db, user_id, data_in
        )
        if not updated_biometric_data:
            return None, "BIO_METRIC_DATA_NOT_FOUND"
        return updated_biometric_data, None
