from datetime import timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import UUID4

from src.presentation.schemas.auth_schema import Token, LoginRequest
from src.infraestructure.database.repositories.user_repo import UserRepository
from src.infraestructure.auth.jwt_config import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from src.infraestructure.database.session import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str)->bool:
        """
        Verifica si una contraseña sin encriptar coincide con la versión encriptada.

        Args:
            plain_password (str): Contraseña sin encriptar.
            hashed_password (str): Contraseña encriptada.

        Returns:
            bool: True si la contraseña coincide, False en caso contrario.
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str)->str:
        '''
        Genera un hash de la contraseña proporcionada.

        Args:
            password (str): La contraseña a encriptar.

        Returns:
            str: La contraseña encriptada.
        '''
        return pwd_context.hash(password)

    def authenticate_user(self, email: str, password: str)-> Optional[dict]:
        """
        Autentica a un usuario por email y contraseña.

        Args:
            email (str): Email del usuario.
            password (str): Contraseña del usuario.

        Returns:
            Optional[dict]: Datos del usuario si la autenticación es exitosa, None en caso contrario.
        """
        user = UserRepository.get_by_email(self.db, email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }

    def login(self, login_data: LoginRequest)-> dict:
        """
        Realiza el inicio de sesión y genera un token JWT.

        Args:
            login_data (LoginRequest): Datos de inicio de sesión.

        Returns:
            dict: Token de acceso y datos del usuario.

        Raises:
            HTTPException: Si las credenciales son inválidas.
        """
        user = self.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo, Contacte con el administrador",
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user["id"]),
                "role": user["role"],
                "email": user["email"]
                }, expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(user["id"]),
            "email": user["email"],
            "role": user["role"]
        }

    def get_current_user_data(self, user_id: UUID4)->dict:
        """
        Obtiene los datos del usuario actual.

        Args:
            user_id (UUID4): ID del usuario.

        Returns:
            dict: Datos del usuario.

        Raises:
            HTTPException: Si el usuario no existe.
        """
        user = UserRepository.get_by_id(self.db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El usuario no esta activo")

        return user
