from sqlalchemy import Column, String, UUID, Enum, Boolean, DateTime, func, ForeignKey, Date
from sqlalchemy.orm import relationship
from infraestructure.database.session import Base
from domain.enums.role_enum import RoleEnum
class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.TIRADOR)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    personal_data = relationship("UserPersonalData", back_populates="user", uselist=False, cascade="all, delete-orphan")
    medical_data = relationship("UserMedicalData", back_populates="user", uselist=False, cascade="all, delete-orphan")
    biometric_data = relationship("UserBiometricData", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserPersonalDataModel(Base):
    __tablename__ = "user_personal_data"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    fist_name = Column(String, nullable=False)
    second_name = Column(String)
    last_name1 = Column(String, nullable=False)
    last_name2 = Column(String)
    phone_number = Column(String, nullable=False)
    date_of_birth = Column(Date)
    city = Column(String) # TODO: Validar si metemos los datos por separado o como campo de direccion
    state = Column(String)
    country = Column(String)

    user = relationship("User", back_populates="personal_data")


class UserMedicalDataModel(Base):
    __tablename__ = "user_medical_data"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    blood_type = Column(String) # Ejemplo: O+, O-, A+, A-, B+, B-, AB+, AB-
    allergies = Column(String) # Ejemplo: Penicilina
    medical_conditions = Column(String) # Ejemplo: Diabetes, Epilepsia, etc
    # is_disabled = Column(Boolean, default=False)
    emergency_contact = Column(String)

    user = relationship("User", back_populates="medical_data")

class UserBiometricDataModel(Base):
    __tablename__ = "user_biometric_data"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    height = Column(String) # Ejemplo: 1.70
    weight = Column(String) # Ejemplo: 70kg
    hand_dominance = Column(String, nullable=False) # Ejemplo: Derecha, Izquierda, Ambas
    eye_sight = Column(String) # Ej "20/20", "20/30"
    imc = Column(String)

    user = relationship("User", back_populates="biometric_data")
