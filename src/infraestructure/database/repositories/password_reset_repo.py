from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from src.infraestructure.database.models.password_reset_model import (
    PasswordResetTokenModel,
)
from src.infraestructure.database.models.user_model import UserModel
from src.domain.entities.password_reset_token import PasswordResetToken
from typing import Optional
from datetime import datetime
import uuid


class PasswordResetRepository:
    """Repositorio para manejo de tokens de recuperación de contraseña"""

    def __init__(self, db: Session):
        self.db = db

    def create_reset_token(
        self, user_id: uuid.UUID, token_hash: str, expires_at: datetime
    ) -> PasswordResetToken:
        """Crear un nuevo token de recuperación"""
        reset_token = PasswordResetTokenModel(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at, used=False
        )

        self.db.add(reset_token)
        self.db.commit()
        self.db.refresh(reset_token)

        return PasswordResetToken(
            id=reset_token.id,
            user_id=reset_token.user_id,
            token_hash=reset_token.token_hash,
            expires_at=reset_token.expires_at,
            used=reset_token.used,
            created_at=reset_token.created_at,
        )

    def find_valid_token(self, token_hash: str) -> Optional[PasswordResetTokenModel]:
        """Buscar un token válido (no usado y no expirado)"""
        stmt = select(PasswordResetTokenModel).where(
            and_(
                PasswordResetTokenModel.token_hash == token_hash,
                PasswordResetTokenModel.used == False,
                PasswordResetTokenModel.expires_at > datetime.utcnow(),
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def mark_token_as_used(self, token_id: uuid.UUID) -> None:
        """Marcar token como usado"""
        stmt = select(PasswordResetTokenModel).where(
            PasswordResetTokenModel.id == token_id
        )
        token = self.db.execute(stmt).scalar_one_or_none()

        if token:
            token.used = True
            self.db.commit()

    def invalidate_user_tokens(self, user_id: uuid.UUID) -> None:
        """Invalidar todos los tokens activos de un usuario"""
        stmt = select(PasswordResetTokenModel).where(
            and_(
                PasswordResetTokenModel.user_id == user_id,
                PasswordResetTokenModel.used == False,
            )
        )
        tokens = self.db.execute(stmt).scalars().all()

        for token in tokens:
            token.used = True

        self.db.commit()
