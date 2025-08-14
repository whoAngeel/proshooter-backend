from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import logging

from src.presentation.schemas.auth_schema import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
)
from src.application.services.auth_service import AuthService
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.user_schemas import UserRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
):
    """
    Endpoint para iniciar sesión y obtener un token JWT.

    Args:
        form_data (OAuth2PasswordRequestForm): Formulario de inicio de sesión.
        auth_service (AuthService): Servicio de autenticación.

    Returns:
        LoginResponse: Token de acceso y datos básicos del usuario.

    Raises:
        HTTPException: Si las credenciales son inválidas.
    """
    login_request = LoginRequest(email=form_data.email, password=form_data.password)
    login_response = auth_service.login(login_request)

    return LoginResponse(**login_response)


@router.post("/login/json/", response_model=LoginResponse)
async def login_json(login_data: LoginRequest, auth_service: AuthService = Depends()):
    """
    Endpoint alternativo para iniciar sesión usando JSON en lugar de form-data.

    Args:
        login_data (LoginRequest): Datos de inicio de sesión en formato JSON.
        auth_service (AuthService): Servicio de autenticación.

    Returns:
        LoginResponse: Token de acceso y datos básicos del usuario.

    Raises:
        HTTPException: Si las credenciales son inválidas.
    """
    login_response = auth_service.login(login_data)

    return LoginResponse(**login_response)


@router.get("/me/", response_model=UserRead)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Endpoint para obtener los datos del usuario autenticado.

    Args:
        current_user (dict): Usuario actual obtenido del token JWT.

    Returns:
        dict: Datos del usuario autenticado.
    """
    return current_user


@router.post("/register/", response_model=LoginResponse)
async def register_user(
    register_data: RegisterRequest, auth_service: AuthService = Depends()
):
    response = auth_service.register(register_data)
    return LoginResponse(**response)


from src.presentation.schemas.password_reset_schemas import *
from src.application.services.reset_password_service import PasswordResetServcie


@router.post("/forgot-password/", response_model=ForgotPasswordResponse)
async def forgotPassword(
    request: ForgotPasswordRequest,
    password_reset_service: PasswordResetServcie = Depends(),
):
    try:
        result = await password_reset_service.request_password_reset(request.email)
        return ForgotPasswordResponse(
            message=result["message"], success=result["success"]
        )
    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {e}")
        return ForgotPasswordResponse(
            message="Error al procesar la solicitud", success=False
        )


@router.post("/reset-password/", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    service: PasswordResetServcie = Depends(),
):
    try:
        result = await service.reset_password(request.token, request.new_password)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"],
            )
        return ResetPasswordResponse(
            message=result["message"], success=result["success"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {e}")
        return ResetPasswordResponse(
            message="Error al procesar la solicitud", success=False
        )
