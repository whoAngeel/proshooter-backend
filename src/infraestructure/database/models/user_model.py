from sqlalchemy import Column, String, UUID, Enum, Boolean, DateTime, func, ForeignKey, Date
from sqlalchemy.orm import relationship
from src.infraestructure.database.session import Base
from src.domain.enums.role_enum import RoleEnum
from uuid import uuid4
class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.TIRADOR)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    personal_data = relationship("UserPersonalDataModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    medical_data = relationship("UserMedicalDataModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    biometric_data = relationship("UserBiometricDataModel", back_populates="user", uselist=False, cascade="all, delete-orphan")

    shooter = relationship("ShooterModel", back_populates="user", uselist=False, cascade="all, delete-orphan", foreign_keys="[ShooterModel.user_id]")


from src.infraestructure.database.models.shooter_model import ShooterModel

class UserPersonalDataModel(Base):
    __tablename__ = "user_personal_data"


    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete="CASCADE"),
        primary_key=True
    )

    first_name = Column(String, nullable=False)
    second_name = Column(String)
    last_name1 = Column(String, nullable=False)
    last_name2 = Column(String)
    phone_number = Column(String, nullable=False)
    date_of_birth = Column(Date)
    city = Column(String) # TODO: Validar si metemos los datos por separado o como campo de direccion
    state = Column(String)
    country = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("UserModel", back_populates="personal_data")



class UserMedicalDataModel(Base):
    __tablename__ = "user_medical_data"

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)

    blood_type = Column(String) # Ejemplo: O+, O-, A+, A-, B+, B-, AB+, AB-
    allergies = Column(String) # Ejemplo: Penicilina
    medical_conditions = Column(String) # Ejemplo: Diabetes, Epilepsia, etc
    # is_disabled = Column(Boolean, default=False)
    emergency_contact = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("UserModel", back_populates="medical_data")

class UserBiometricDataModel(Base):
    __tablename__ = "user_biometric_data"

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)

    height = Column(String) # Ejemplo: 1.70
    weight = Column(String) # Ejemplo: 70kg
    hand_dominance = Column(String, nullable=False) # Ejemplo: Derecha, Izquierda, Ambas
    eye_sight = Column(String) # Ej "20/20", "20/30"
    # imc = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("UserModel", back_populates="biometric_data")
