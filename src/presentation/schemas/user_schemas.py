from pydantic import BaseModel, EmailStr ,Field
from typing import Optional
from uuid import UUID
from src.domain.enums.role_enum import RoleEnum
from datetime import datetime, date

class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.TIRADOR
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="El password debe tener al menos 6 caracteres")

class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    personal_data: Optional["UserPersonalDataRead"] = None
    medical_data: Optional["UserMedicalDataRead"] = None
    biometric_data: Optional["UserBiometricDataRead"] = None

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

class UserPersonalDataRead(UserPersonalDataBase):
    id: UUID

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
    id: UUID
    class Config:
        from_attributes = True

# ------------ SCHEMAS PARA BIOMETRIC DATA ------------
class UserBiometricDataBase(BaseModel):
    height: Optional[str] = None
    weight: Optional[str] = None
    hand_dominance: Optional[str] = None
    eye_sight: Optional[str] = None
    # imc: Optional

class UserBiometricDataCreate(UserBiometricDataBase):
    pass

class UserBiometricDataRead(UserBiometricDataBase):
    id: UUID
    class Config:
        from_attributes = True

UserRead.model_rebuild()
