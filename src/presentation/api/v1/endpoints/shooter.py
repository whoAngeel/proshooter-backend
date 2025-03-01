from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.application.services.shooter_service import ShooterService
from src.infraestructure.database.session import get_db
from src.presentation.schemas.shooter_schema import ShooterCreate, ShooterRead, ShooterReadLite

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
