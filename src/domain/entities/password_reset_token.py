from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class PasswordResetToken:
    """Entidad que representa un token de recuperación de contraseña"""

    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    used: bool
    created_at: datetime
