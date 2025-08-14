from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_, and_, desc, case
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import Dict, List, Optional, Any
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from src.domain.enums.role_enum import RoleEnum
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
    UserBiometricDataUpdate,
)
from src.infraestructure.database.repositories.shooter_stats_repo import (
    ShooterStatsRepository,
)
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from fastapi import HTTPException


class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: UUID):
        return db.get(UserModel, user_id)

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.execute(
            select(UserModel).where(UserModel.email == email)
        ).scalar_one_or_none()

    @staticmethod
    def get_all(db: Session):
        return db.execute(select(UserModel)).scalars().all()

    @staticmethod
    def create(db: Session, user_data: UserCreate, hashed_password: str):
        new_user = UserModel(
            email=user_data.email,
            hashed_password=hashed_password,
        )

        db.add(new_user)
        db.flush()
        # db.refresh(new_user)
        return new_user

    @staticmethod
    def toggle_active(db: Session, user_id: UUID):
        user = UserRepository.get_by_id(db, user_id)
        user.is_active = not user.is_active
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: UserModel, update_data: dict = None) -> UserModel:
        # TODO: Implementar lógica de actualización de usuario y ver en que usarlo
        if update_data:
            for key, value in update_data.items():
                setattr(user, key, value)
        db.add(user)
        db.commit()
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

        # Verificar que el nuevo rol sea válido usando el enum
        try:
            new_role_enum = RoleEnum.from_string(new_role)
        except ValueError:
            return None, "INVALID_ROLE"

        # Obtener el rol actual como enum
        current_role_enum = RoleEnum.from_string(user.role)

        # Definir las promociones válidas
        valid_promotions = {
            RoleEnum.TIRADOR: [RoleEnum.INSTRUCTOR],
            RoleEnum.INSTRUCTOR: [RoleEnum.INSTRUCTOR_JEFE],
            RoleEnum.INSTRUCTOR_JEFE: [],  # No puede ser promovido a un rol superior
            RoleEnum.ADMIN: [],  # Los administradores no pueden ser promovidos
        }
        # Verificar que la promoción siga la jerarquía correcta
        if new_role_enum not in valid_promotions.get(current_role_enum, []):
            return None, f"INVALID_PROMOTION:{current_role_enum}>{new_role_enum}"

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

    @staticmethod
    def update_user_password(self, user_id: UUID, new_password_hash: str) -> UserModel:
        stmt = select(UserModel).where(UserModel.id == user_id)
        user = self.db.execute(stmt).scalar_one_or_none()

        if user:
            user.password = new_password_hash
            self.db.commit()
            self.db.refresh(user)

    @staticmethod
    def search_by_combined_criteria(
        db: Session, filter_params: dict, skip: int = 0, limit: int = 100
    ) -> list:
        query = db.query(UserModel).options(joinedload(UserModel.personal_data))

        # Filtros directos
        if filter_params.get("email"):
            query = query.filter(UserModel.email.ilike(f"%{filter_params['email']}%"))
        if filter_params.get("role"):
            query = query.filter(UserModel.role == filter_params["role"])
        if filter_params.get("is_active") is not None:
            query = query.filter(UserModel.is_active == filter_params["is_active"])

        # Búsqueda por nombre/apellido
        if filter_params.get("search"):
            search_term = f"%{filter_params['search']}%"
            query = query.join(
                UserPersonalDataModel, UserModel.id == UserPersonalDataModel.user_id
            ).filter(
                or_(
                    UserPersonalDataModel.first_name.ilike(search_term),
                    UserPersonalDataModel.second_name.ilike(search_term),
                    UserPersonalDataModel.last_name1.ilike(search_term),
                    UserPersonalDataModel.last_name2.ilike(search_term),
                )
            )

        # Ordenar por apellido y nombre
        query = query.join(
            UserPersonalDataModel, UserModel.id == UserPersonalDataModel.user_id
        ).order_by(UserPersonalDataModel.last_name1, UserPersonalDataModel.first_name)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_criteria(db: Session, filter_params: dict) -> int:
        query = db.query(func.count(UserModel.id))

        if filter_params.get("email"):
            query = query.filter(UserModel.email.ilike(f"%{filter_params['email']}%"))
        if filter_params.get("role"):
            query = query.filter(UserModel.role == filter_params["role"])
        if filter_params.get("is_active") is not None:
            query = query.filter(UserModel.is_active == filter_params["is_active"])

        if filter_params.get("search"):
            search_term = f"%{filter_params['search']}%"
            query = query.join(
                UserPersonalDataModel, UserModel.id == UserPersonalDataModel.user_id
            ).filter(
                or_(
                    UserPersonalDataModel.first_name.ilike(search_term),
                    UserPersonalDataModel.second_name.ilike(search_term),
                    UserPersonalDataModel.last_name1.ilike(search_term),
                    UserPersonalDataModel.last_name2.ilike(search_term),
                )
            )

        return query.scalar()


class UserPersonalDataRepository:
    @staticmethod
    def create(db: Session, user_id: UUID, personal_data: UserPersonalDataCreate):
        data_dict = personal_data.model_dump()
        data_dict["user_id"] = user_id
        new_personal_data = UserPersonalDataModel(**data_dict)
        db.add(new_personal_data)
        db.commit()
        db.refresh(new_personal_data)
        return new_personal_data

    @staticmethod
    def update(db: Session, user_id: UUID, data_in: UserPersonalDataUpdate):
        personal_data_db = (
            db.query(UserPersonalDataModel)
            .filter(UserPersonalDataModel.user_id == user_id)
            .first()
        )
        if not personal_data_db:
            return None
        update_dict = data_in.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(personal_data_db, key, value)

        db.commit()
        db.refresh(personal_data_db)
        return personal_data_db

    @staticmethod
    def get_by_user_id(db: Session, user_id: UUID):
        return db.execute(
            select(UserPersonalDataModel).where(
                UserPersonalDataModel.user_id == user_id
            )
        ).scalar_one_or_none()


class UserMedicalDataRepository:
    @staticmethod
    def create(db: Session, user_id: UUID, medical_data: UserMedicalDataCreate):
        # new_medical_data = UserMedicalDataModel(
        #     blood_type=medical_data.blood_type,
        #     allergies=medical_data.allergies,
        #     medical_conditions=medical_data.medical_conditions,
        #     emergency_contact=medical_data.emergency_contact,
        #     user_id=user_id,
        # )
        medical_data_dict = medical_data.model_dump()
        medical_data_dict["user_id"] = user_id
        new_medical_data = UserMedicalDataModel(**medical_data_dict)

        db.add(new_medical_data)
        db.commit()
        db.refresh(new_medical_data)
        return new_medical_data

    @staticmethod
    def update(db: Session, user_id: UUID, data_in: UserMedicalDataUpdate):

        medical_data_db = (
            db.query(UserMedicalDataModel)
            .filter(UserMedicalDataModel.user_id == user_id)
            .first()
        )
        if not medical_data_db:
            return None

        # actualizar los campos que no vienen vacios
        update_dict = data_in.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(medical_data_db, key, value)

        db.commit()
        db.refresh(medical_data_db)
        return medical_data_db

    @staticmethod
    def get_by_user_id(db: Session, user_id: UUID):
        return db.execute(
            select(UserMedicalDataModel).where(UserMedicalDataModel.user_id == user_id)
        ).scalar_one_or_none()


class UserBiometricDataRepository:
    @staticmethod
    def create(db: Session, user_id: UUID, biometric_data: UserCreate):
        # new_biometric_data = UserBiometricDataModel(
        #     height=biometric_data.height,
        #     weight=biometric_data.weight,
        #     hand_dominance=biometric_data.hand_dominance,
        #     eye_sight=biometric_data.eye_sight,
        #     user_id=user_id,
        # )
        data_dict = biometric_data.model_dump()
        data_dict[user_id] = user_id
        new_biometric_data = UserBiometricDataModel(**data_dict)
        db.add(new_biometric_data)
        db.commit()
        db.refresh(new_biometric_data)
        return new_biometric_data

    @staticmethod
    def update(db: Session, user_id: UUID, data_in: UserBiometricDataUpdate):
        biometric_data_db = (
            db.query(UserBiometricDataModel)
            .filter(UserBiometricDataModel.user_id == user_id)
            .first()
        )
        if not biometric_data_db:
            return None

        update_dict = data_in.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(biometric_data_db, key, value)

        db.commit()
        db.refresh(biometric_data_db)
        return biometric_data_db

    @staticmethod
    def get_by_user_id(db: Session, user_id: UUID):
        return db.execute(
            select(UserBiometricDataModel).where(
                UserBiometricDataModel.user_id == user_id
            )
        ).scalar_one_or_none()
