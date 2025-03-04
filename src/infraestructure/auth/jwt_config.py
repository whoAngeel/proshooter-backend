from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4
from sqlalchemy.orm import Session
from src.infraestructure.database.session import get_db

from src.presentation.schemas.user_schemas import UserRead
from src.infraestructure.database.models.user_model import UserModel
from src.application.services.user_service import UserService
from src.infraestructure.config.settings import settings
from src.infraestructure.database.repositories.user_repo import UserRepository

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None)-> str:
    """
    Crea un token JWT con los datos proporcionados.

    Args:
        data (dict): Datos a incluir en el token.
        expires_delta (timedelta, optional): Tiempo de expiración del token.

    Returns:
        str: Token JWT generado.
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))-> UserRead:
    """
    Verifica el token JWT y devuelve el usuario actual.

    Args:
        token (str): Token JWT.
        user_service (UserService): Servicio para obtener el usuario.

    Returns:
        UserRead: Usuario autenticado.

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = UserRepository.get_by_id(db, UUID4(user_id))
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no esta activo"
        )

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    }
