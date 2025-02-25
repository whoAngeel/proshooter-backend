from sqlalchemy.orm import Session
from passlib.context import CryptContext
from uuid import UUID

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
    UserPersonalDataUpdate
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate):
        existing_user = UserRepository.get_by_email(db, user_data.email)
        if existing_user:
            return None
        hashed_password = pwd_context.hash(user_data.password)
        return UserRepository.create(db, user_data, hashed_password)

    @staticmethod
    def get_user(db:Session, user_id: UUID):
        return UserRepository.get_by_id(db, user_id)

    @staticmethod
    def get_users(db:Session):
        return UserRepository.get_all(db)

    @staticmethod
    def toggle_active(db:Session, user_id: UUID):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None
        return UserRepository.toggle_active(db, user_id)


    @staticmethod
    def create_personal_data(db: Session, user_id: UUID, data_in: UserPersonalDataCreate):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None, "USER_NOT_FOUND"

        existing_data = UserPersonalDataRepository.get_by_user_id(db, user_id)
        if existing_data:
            return None, "PERSONAL_DATA_ALREADY_EXISTS"
        created_data = UserPersonalDataRepository.create(db, user_id, data_in)
        return created_data, None

    @staticmethod
    def update_personal_data(db: Session, user_id: UUID, data_in: UserPersonalDataUpdate):
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
            return None, "PERSONAL_DATA_NOT_FOUND"

        return updated_medical_data, None


    @staticmethod
    def add_biometric_data(db: Session, user_id: UUID, data_in: UserBiometricDataCreate):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None
        biometric_data = UserBiometricDataRepository.create(db, user_id, data_in)
        return biometric_data
