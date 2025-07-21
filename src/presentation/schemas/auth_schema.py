from pydantic import BaseModel, EmailStr, field_validator, ValidationError
from typing import Optional
from datetime import date, datetime
from src.domain.enums.role_enum import RoleEnum
from enum import Enum


class GenreEnum(str, Enum):
    M = "M"  # Masculino
    F = "F"  # Femenino
    NA = "N/A"  # No especificado
    O = "O"  # Otro
    NB = "NB"  # No binario


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: EmailStr
    role: str


class PersonalData(BaseModel):
    first_name: str
    second_name: Optional[str] = None
    last_name1: str
    last_name2: Optional[str] = None
    phone_number: str
    date_of_birth: Optional[date] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    genre: GenreEnum = GenreEnum.NA  # M, F, N/A

    @field_validator("date_of_birth")
    def validate_date_of_birth(cls, v):
        if v is None:
            return v
        today = date.today()
        if v >= today:
            raise ValueError("La fecha de nacimiento debe ser en el pasado.")
        min_year = today.year - 18
        if v.year > min_year:
            raise ValueError("El usuario debe tener al menos 18 años.")
        return v


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    personal_data: PersonalData
    role: Optional[RoleEnum] = RoleEnum.TIRADOR
