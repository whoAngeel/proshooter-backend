from pydantic import BaseModel, EmailStr ,Field
from typing import Optional
from uuid import UUID
from src.domain.enums.role_enum import RoleEnum
from datetime import datetime, date
from .user_schemas import UserRead


class ShooterRead(BaseModel):
    user_id: UUID
    user: Optional["UserReadLite"] = None  # Forward reference

    class Config:
        from_attributes = True

from src.presentation.schemas.user_schemas import UserReadLite
ShooterRead.model_rebuild()
