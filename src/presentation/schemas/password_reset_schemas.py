from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ForgotPasswordRequest(BaseModel):
    """Esquema para solicitar recuperación de contraseña"""

    email: EmailStr = Field(..., description="Email del usuario")


class ForgotPasswordResponse(BaseModel):
    """Respuesta al solicitar recuperación de contraseña"""

    message: str
    success: bool


class ResetPasswordRequest(BaseModel):
    """Esquema para resetear contraseña con token"""

    token: str = Field(..., min_length=32, description="Token de recuperación")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")


class ResetPasswordResponse(BaseModel):
    """Respuesta al resetear contraseña"""

    message: str
    success: bool
