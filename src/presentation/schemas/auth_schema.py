from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from src.domain.enums.role_enum import RoleEnum


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
    genre: Optional[str] = "N/A"  # M, F, N/A


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    personal_data: PersonalData
    role: Optional[RoleEnum] = RoleEnum.TIRADOR
