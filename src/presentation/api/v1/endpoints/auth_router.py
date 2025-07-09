from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


from src.presentation.schemas.auth_schema import LoginRequest, LoginResponse
from src.application.services.auth_service import AuthService
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.user_schemas import UserRead

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends()
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


@router.post("/login/json", response_model=LoginResponse)
async def login_json(
    login_data: LoginRequest,
    auth_service: AuthService = Depends()
):
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


@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint para obtener los datos del usuario autenticado.

    Args:
        current_user (dict): Usuario actual obtenido del token JWT.

    Returns:
        dict: Datos del usuario autenticado.
    """
    return current_user
