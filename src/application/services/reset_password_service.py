from src.infraestructure.database.repositories.password_reset_repo import (
    PasswordResetRepository,
)
from src.infraestructure.database.repositories.user_repo import UserRepository
from src.application.services.resend_email_service import ResendEmailService
from src.infraestructure.auth.password_utils import hash_password, verify_password
from src.infraestructure.database.session import get_db
from src.infraestructure.config.settings import settings
from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import Depends
from sqlalchemy.orm import Session
import secrets
import hashlib
import logging

logger = logging.getLogger(__name__)


class PasswordResetService:

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.reset_repo = PasswordResetRepository(self.db)
        self.user_repo = UserRepository()
        self.email_service = ResendEmailService(self.db)
        self.frontend_url = settings.FRONTEND_URL
        self.token_expiry_minutes = settings.RESET_TOKEN_EXPIRE_MINUTES

    def _generate_reset_token(self) -> Tuple[str, str]:
        token = secrets.token_urlsafe(48)

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        return token, token_hash

    async def request_password_reset(self, email: str) -> dict:
        """Solicitar recuperacion de contrasena"""
        try:
            user = self.user_repo.get_by_email(self.db, email)
            if not user:
                return {
                    "success": True,
                    "message": "Si el email existe en nuestro sistema, recibirás un enlace de recuperación.",
                }
            self.reset_repo.invalidate_user_tokens(user.id)

            # generar nuevo token
            token, hash_token = self._generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(
                minutes=self.token_expiry_minutes
            )

            # guardar token en bd
            self.reset_repo.create_reset_token(
                user_id=user.id, token_hash=hash_token, expires_at=expires_at
            )

            # enviar email
            email_sent = self.email_service.send_password_reset_email(
                recipient_email=email, reset_token=token, frontend_url=self.frontend_url
            )

            if not email_sent:
                logger.error(
                    f" ❌ Error al enviar el email de recuperación de contraseña a {email}"
                )
                return {
                    "success": False,
                    "message": "Error al enviar el email de recuperación de contraseña.",
                }
            logger.info(f" ✅ Email de recuperación de contraseña enviado a {email}")
            return {
                "success": True,
                "message": "Si el email existe en nuestro sistema, recibirás un enlace de recuperación.",
            }
        except Exception as e:
            logger.error(
                f"❌ Error al procesar la solicitud de recuperación de contraseña: {e}"
            )
            return {
                "success": False,
                "message": "Error al procesar la solicitud de recuperación de contraseña.",
            }

    async def reset_password(self, token: str, new_password: str) -> dict:
        """Restablecer la contraseña del usuario"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            # Buscar el token
            reset_token = self.reset_repo.find_valid_token(token_hash)
            if not reset_token:
                return {
                    "success": False,
                    "message": "Token de recuperación inválido o expirado.",
                }

            # Buscar el usuario
            user = self.user_repo.get_by_id(self.db, reset_token.user_id)
            if not user:
                return {"success": False, "message": "Usuario no encontrado."}

            # Actualizar la contraseña
            hashed_password = hash_password(new_password)
            self.user_repo.update_user_password(self.db, user.id, hashed_password)

            self.reset_repo.mark_token_as_used(reset_token.id)

            self.email_service.send_password_changed_notification(user.email)

            logger.info(f" ✅ Contraseña restablecida para el usuario {user.email}")

            return {"success": True, "message": "Contraseña restablecida con éxito."}
        except Exception as e:
            logger.error(
                f"❌ Error al procesar la solicitud de restablecimiento de contraseña: {e}"
            )
            return {
                "success": False,
                "message": "Error al procesar la solicitud de restablecimiento de contraseña.",
            }
