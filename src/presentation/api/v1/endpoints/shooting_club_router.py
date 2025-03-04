from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from application.services.shooting_club_service import ShootingClubService


router = APIRouter(prefix="/shooting_clubs", tags=["shooting_clubs"])

@router.post()
