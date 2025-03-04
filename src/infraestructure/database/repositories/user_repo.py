from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import Dict
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from src.infraestructure.database.models.user_model import (
    UserModel,
    UserMedicalDataModel,
    UserBiometricDataModel,
    UserPersonalDataModel,
)
from src.infraestructure.database.models.shooter_model import ShooterModel
from src.presentation.schemas.user_schemas import (
    UserCreate,
    UserPersonalDataCreate,
    UserPersonalDataUpdate,
    UserMedicalDataCreate,
    UserMedicalDataUpdate,
    UserBiometricDataUpdate
)
from src.infraestructure.database.repositories.shooter_stats_repo import ShooterStatsRepository
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from fastapi import HTTPException
class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: UUID):
        return db.get(UserModel, user_id)


    @staticmethod
    def get_by_email(db:Session, email: str):
        return db.execute(select(UserModel).where(UserModel.email==email)).scalar_one_or_none()

    @staticmethod
    def get_all(db:Session):
        return db.execute(select(UserModel)).scalars().all()

    @staticmethod
    def create(db:Session, user_data: UserCreate, hashed_password: str):
        new_user = UserModel(
            email=user_data.email,
            hashed_password=hashed_password,
        )

        db.add(new_user)
        db.flush()
        # db.refresh(new_user)
        return new_user

    @staticmethod
    def toggle_active(db:Session, user_id: UUID):
        user = UserRepository.get_by_id(db, user_id)
        user.is_active = not user.is_active
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db:Session, user: UserModel) -> UserModel:
        db.add(user)
        db.flush()
        db.refresh(user)
        return user


    @staticmethod
    def register(db: Session, user_data: UserCreate, hashed_password: str) -> UserModel:
        try:
            new_user = UserRepository.create(db, user_data, hashed_password)
            db.refresh(new_user)
            ShooterRepository.create(db, new_user.id)
            ShooterStatsRepository.create(db, new_user.id)
            db.commit()
            return new_user
        except IntegrityError as ie:
            db.rollback()
            raise None
        except Exception as e:
            db.rollback()
            raise None

    @staticmethod
    def promote_role(db: Session, user_id: UUID, new_role: str):
        """
        Promueve a un usuario a un nuevo rol siguiendo la jerarquía establecida.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario a promover
            new_role: Nuevo rol deseado

        Returns:
            Tupla (usuario_actualizado, mensaje_error)
        """
        # Obtener el usuario
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None, "USER_NOT_FOUND"

        # Verificar que el usuario esté activo
        if not user.is_active:
            return None, "USER_NOT_ACTIVE"

        # Validar que el nuevo rol sea válido
        valid_roles = ["TIRADOR", "INSTRUCTOR", "JEFE_INSTRUCTORES"]
        if new_role not in valid_roles:
            return None, "INVALID_ROLE"

        # Definir las promociones válidas
        valid_promotions = {
            "TIRADOR": ["INSTRUCTOR"],
            "INSTRUCTOR": ["JEFE_INSTRUCTORES"],
            "JEFE_INSTRUCTORES": []  # No puede ser promovido a un rol superior
        }

        # Verificar que la promoción siga la jerarquía correcta
        if new_role not in valid_promotions.get(user.role, []):
            return None, f"INVALID_PROMOTION:{user.role}>{new_role}"

        try:
            # Iniciar transacción
            db.begin_nested()

            # Actualizar el rol del usuario
            user.role = new_role
            db.add(user)
            db.flush()
            db.refresh(user)

            # Confirmar la transacción
            db.commit()

            return user, None
        except Exception as e:
            # Revertir la transacción en caso de error
            db.rollback()
            print(f"Error al promover rol: {str(e)}")
            return None, "DATABASE_ERROR"

class UserPersonalDataRepository:
    @staticmethod
    def create(db:Session, user_id: UUID, personal_data: UserPersonalDataCreate):
        new_personal_data = UserPersonalDataModel(
            first_name=personal_data.first_name,
            second_name=personal_data.second_name,
            last_name1=personal_data.last_name1,
            last_name2=personal_data.last_name2,
            phone_number=personal_data.phone_number,
            date_of_birth=personal_data.date_of_birth,
            city=personal_data.city,
            state=personal_data.state,
            country=personal_data.country,
            user_id=user_id,
        )
        db.add(new_personal_data)
        db.commit()
        db.refresh(new_personal_data)
        return new_personal_data


    @staticmethod
    def update(db: Session, user_id: UUID, data_in: UserPersonalDataUpdate):
        personal_data_db = db.query(UserPersonalDataModel).filter(
            UserPersonalDataModel.user_id == user_id
        ).first()
        if not personal_data_db:
            return None

        # actualizar los campos que no vienen vacios
        if data_in.first_name:
            personal_data_db.first_name = data_in.first_name
        if data_in.second_name:
            personal_data_db.second_name = data_in.second_name
        if data_in.last_name1:
            personal_data_db.last_name1 = data_in.last_name1
        if data_in.last_name2:
            personal_data_db.last_name2 = data_in.last_name2
        if data_in.phone_number:
            personal_data_db.phone_number = data_in.phone_number
        if data_in.date_of_birth:
            personal_data_db.date_of_birth = data_in.date_of_birth
        if data_in.city:
            personal_data_db.city = data_in.city
        if data_in.state:
            personal_data_db.state = data_in.state
        if data_in.country:
            personal_data_db.country = data_in.country

        db.commit()
        db.refresh(personal_data_db)
        return personal_data_db

    @staticmethod
    def get_by_user_id(db:Session, user_id: UUID):
        return db.execute(select(UserPersonalDataModel).where(UserPersonalDataModel.user_id==user_id)).scalar_one_or_none()

class UserMedicalDataRepository:
    @staticmethod
    def create(db:Session, user_id: UUID, medical_data: UserMedicalDataCreate):
        new_medical_data = UserMedicalDataModel(
            blood_type=medical_data.blood_type,
            allergies=medical_data.allergies,
            medical_conditions=medical_data.medical_conditions,
            emergency_contact=medical_data.emergency_contact,
            user_id=user_id,
        )
        db.add(new_medical_data)
        db.commit()
        db.refresh(new_medical_data)
        return new_medical_data

    @staticmethod
    def update(db: Session, user_id: UUID, data_in: UserMedicalDataUpdate):

        medical_data_db = db.query(UserMedicalDataModel).filter(
            UserMedicalDataModel.user_id == user_id
        ).first()
        if not medical_data_db:
            return None

        # actualizar los campos que no vienen vacios
        if data_in.blood_type:
            medical_data_db.blood_type = data_in.blood_type
        if data_in.allergies:
            medical_data_db.allergies = data_in.allergies
        if data_in.medical_conditions:
            medical_data_db.medical_conditions = data_in.medical_conditions
        if data_in.emergency_contact:
            medical_data_db.emergency_contact = data_in.emergency_contact


        db.commit()
        db.refresh(medical_data_db)
        return medical_data_db

    @staticmethod
    def get_by_user_id(db:Session, user_id: UUID):
        return db.execute(select(UserMedicalDataModel).where(UserMedicalDataModel.user_id==user_id)).scalar_one_or_none()


class UserBiometricDataRepository:
    @staticmethod
    def create(db:Session, user_id: UUID, biometric_data: UserCreate):
        new_biometric_data = UserBiometricDataModel(
            height=biometric_data.height,
            weight=biometric_data.weight,
            hand_dominance=biometric_data.hand_dominance,
            eye_sight=biometric_data.eye_sight,
            user_id=user_id,
        )
        db.add(new_biometric_data)
        db.commit()
        db.refresh(new_biometric_data)
        return new_biometric_data

    @staticmethod
    def update(db: Session, user_id: UUID, data_in: UserBiometricDataUpdate):
        biometric_data_db = db.query(UserBiometricDataModel).filter(
            UserBiometricDataModel.user_id == user_id
        ).first()
        if not biometric_data_db:
            return None

        # actualizar los campos que no vienen vacios
        if data_in.height:
            biometric_data_db.height = data_in.height
        if data_in.weight:
            biometric_data_db.weight = data_in.weight
        if data_in.hand_dominance:
            biometric_data_db.hand_dominance = data_in.hand_dominance
        if data_in.eye_sight:
            biometric_data_db.eye_sight = data_in.eye_sight
        if data_in.time_sleep:
            biometric_data_db.time_sleep = data_in.time_sleep
        if data_in.blood_pressure:
            biometric_data_db.blood_pressure = data_in.blood_pressure
        if data_in.heart_rate:
            biometric_data_db.heart_rate = data_in.heart_rate
        if data_in.respiratory_rate:
            biometric_data_db.respiratory_rate = data_in.respiratory_rate

        db.commit()
        db.refresh(biometric_data_db)
        return biometric_data_db

    @staticmethod
    def get_by_user_id(db:Session, user_id: UUID):
        return db.execute(select(UserBiometricDataModel).where(UserBiometricDataModel.user_id==user_id)).scalar_one_or_none()
