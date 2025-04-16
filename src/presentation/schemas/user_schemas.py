from pydantic import BaseModel, EmailStr ,Field
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from src.domain.enums.role_enum import RoleEnum
from datetime import datetime, date
# from .shooter_schema import ShooterRead

# if TYPE_CHECKING:
#     from src.presentation.schemas.shooter_schema import ShooterRead

class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.TIRADOR
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="El password debe tener al menos 6 caracteres")

class UserReadLiteNoPersonalData(BaseModel):
    id: UUID
    email: EmailStr  # 🔥 No incluye personal_data

    class Config:
        from_attributes = True

class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    personal_data: Optional["UserPersonalDataRead"] = None
    medical_data: Optional["UserMedicalDataRead"] = None
    biometric_data: Optional["UserBiometricDataRead"] = None

    shooter: Optional["ShooterRead"] = None

    class Config:
        from_attributes = True

class UserReadLiteNoPersonalData(BaseModel):
    id: UUID
    email: EmailStr  # 🔥 No incluye personal_data

    class Config:
        from_attributes = True

class UserReadLite(BaseModel):
    id: UUID
    email: EmailStr
    role: RoleEnum
    personal_data: Optional["UserPersonalDataReadLite"] = None  # 🔥 Relación con datos personales

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

class UserPersonalDataBase(BaseModel):
    first_name: str
    second_name: Optional[str] = None
    last_name1: str
    last_name2: Optional[str] = None
    phone_number: str
    date_of_birth: Optional[date] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

class UserPersonalDataBaseLite(BaseModel):
    first_name: str
    second_name: Optional[str] = None
    last_name1: str
    last_name2: Optional[str] = None




class UserPersonalDataUpdate(UserPersonalDataBase):
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    last_name1: Optional[str] = None
    last_name2: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class UserPersonalDataCreate(UserPersonalDataBase):
    pass

class UserPersonalDataReadLite(BaseModel):
    user_id: UUID
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    last_name1: Optional[str] = None
    last_name2: Optional[str] = None

    class Config:
        from_attributes = True



class UserPersonalDataRead(UserPersonalDataBase):
    user_id: UUID

    class Config:
        from_attributes = True

# ------------ SCHEMAS PARA MEDICAL DATA ------------
class UserMedicalDataBase(BaseModel):
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None

class UserMedicalDataCreate(UserMedicalDataBase):
    pass

class UserMedicalDataUpdate(UserMedicalDataBase):
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None

class UserMedicalDataRead(UserMedicalDataBase):
    user_id: UUID
    class Config:
        from_attributes = True

# ------------ SCHEMAS PARA BIOMETRIC DATA ------------
class UserBiometricDataBase(BaseModel):
    height: Optional[str] = None
    weight: Optional[str] = None
    hand_dominance: Optional[str] = None
    eye_sight: Optional[str] = None
    time_sleep: Optional[str] = None
    blood_pressure: Optional[str] = None
    heart_rate: Optional[str] = None
    respiratory_rate: Optional[str] = None
    # imc: Optional

class UserBiometricDataCreate(UserBiometricDataBase):
    pass

class UserBiometricDataUpdate(UserBiometricDataBase):
    height: Optional[str] = None
    weight: Optional[str] = None
    hand_dominance: Optional[str] = None
    eye_sight: Optional[str] = None
    time_sleep: Optional[str] = None
    blood_pressure: Optional[str] = None
    heart_rate: Optional[str] = None
    respiratory_rate: Optional[str] = None

class UserBiometricDataRead(UserBiometricDataBase):
    user_id: UUID
    class Config:
        from_attributes = True

from src.presentation.schemas.shooter_schema import ShooterRead
UserRead.model_rebuild()
