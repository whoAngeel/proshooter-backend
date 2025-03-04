from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from uuid import UUID

from src.application.services.shooter_service import ShooterService
from src.infraestructure.database.session import get_db
from src.presentation.schemas.shooter_schema import ShooterCreate, ShooterRead, ShooterReadLite
from src.application.services.user_service import UserService

router = APIRouter(prefix="/shooters", tags=["shooters"])


@router.get("/", response_model=list[ShooterReadLite])
def get_shooters(db: Session = Depends(get_db)):
    return ShooterService.get_shooters(db)

@router.get("/{shooter_id}", response_model=ShooterReadLite)
def get_shooter_by_id(shooter_id: UUID, db: Session = Depends(get_db)):
    shooter = ShooterService.get_shooter_by_user_id(db, shooter_id)
    if not shooter:
        raise HTTPException(status_code=400, detail="El tirador no existe")
    return shooter

@router.patch("/{shooter_id}/promote", response_model=ShooterReadLite, status_code=201)
def promote_user(
    shooter_id: UUID,
    new_role: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    ):
    # user, error = UserService.promote(db, shooter_id, new_role)
    updated_user, error = UserService.promote_role(db, shooter_id, new_role)

    # Manejar posibles errores
    if error:
        error_messages = {
            "USER_NOT_FOUND": ("Usuario no encontrado", 404),
            "USER_NOT_ACTIVE": ("El usuario no está activo", 400),
            "INVALID_ROLE": ("Rol inválido", 400),
            "DATABASE_ERROR": ("Error en la base de datos", 500)
        }

        if error.startswith("INVALID_PROMOTION:"):
            roles = error.split(":", 1)[1].split(">")
            detail = f"Promoción no válida. Un {roles[0]} no puede ser promovido directamente a {roles[1]}"
            raise HTTPException(status_code=400, detail=detail)
        else:
            detail, status_code = error_messages.get(error, ("Error desconocido", 500))
            raise HTTPException(status_code=status_code, detail=detail)

    shooter = ShooterService.get_shooter_by_user_id(db, shooter_id)
    if not shooter:
        raise HTTPException(status_code=400, detail="El tirador no existe")
    return shooter
