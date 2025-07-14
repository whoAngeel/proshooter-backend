from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional, TYPE_CHECKING, List

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
    password: str = Field(
        ..., min_length=6, description="El password debe tener al menos 6 caracteres"
    )


class UserReadLiteNoPersonalData(BaseModel):
    id: UUID4
    email: EmailStr  # 🔥 No incluye personal_data

    model_config = {"from_attributes": True}


class UserRead(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
    personal_data: Optional["UserPersonalDataRead"] = None
    medical_data: Optional["UserMedicalDataRead"] = None
    biometric_data: Optional["UserBiometricDataRead"] = None

    shooter: Optional["ShooterRead"] = None

    model_config = {"from_attributes": True}


class UserList(BaseModel):
    users: List[UserRead]
    total: int
    page: int
    size: int
    pages: int


class UserFilter(BaseModel):
    email: Optional[str] = (None,)
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None
    skip: int = 0
    limit: int = 100


class UserPersonalDataReadLite(BaseModel):
    user_id: UUID4
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    last_name1: Optional[str] = None
    last_name2: Optional[str] = None
    genre: Optional[str] = None  # M, F, N/A

    model_config = {"from_attributes": True}


class UserReadLite(BaseModel):
    id: UUID4
    email: EmailStr
    role: RoleEnum
    personal_data: Optional[UserPersonalDataReadLite] = None  # Usar comillas

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None

    model_config = {"from_attributes": True}


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
    genre: Optional[str] = "N/A"  # M, F, N/A


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
    genre: Optional[str] = None  # M, F, N/A


class UserPersonalDataCreate(UserPersonalDataBase):
    pass


class UserPersonalDataReadLite(BaseModel):
    user_id: UUID4
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    last_name1: Optional[str] = None
    last_name2: Optional[str] = None
    genre: Optional[str] = None

    model_config = {"from_attributes": True}


class UserPersonalDataRead(UserPersonalDataBase):
    user_id: UUID4

    model_config = {"from_attributes": True}


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
    user_id: UUID4
    model_config = {"from_attributes": True}


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
    user_id: UUID4
    model_config = {"from_attributes": True}


from src.presentation.schemas.shooter_schema import ShooterRead

UserRead.model_rebuild()
UserReadLite.model_rebuild()
