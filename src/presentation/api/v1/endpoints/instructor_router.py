from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.infraestructure.auth.jwt_config import get_current_user
from src.application.services.club_instructor import ClubInstructorService
from src.application.services.practice_session_service import PracticeSessionService
from src.presentation.schemas.instructor import (
    AvailableInstructorsResponse,
    InstructorBasicInfo,
    PracticeSessionCreateRequest,
)

router = APIRouter(prefix="/instructors", tags=["Instructores"])


@router.get("/available/", response_model=AvailableInstructorsResponse)
async def get_available_instructors(
    service: ClubInstructorService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    try:
        shooter_id = current_user.id

        instructors = service.get_available_instructors_for_shooter(shooter_id)

        return AvailableInstructorsResponse(
            success=True, instructors=instructors, total_count=len(instructors)
        )
    except HTTPException as e:
        return AvailableInstructorsResponse(
            success=False,
            instructors=[],
            total_count=0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error al obtener instructores disponibles: " + str(e),
        )


@router.get("/club/{club_id}/", response_model=List[InstructorBasicInfo])
async def get_club_instructors(
    club_id: UUID,
    service: ClubInstructorService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtener instructores disponibles en un club específico.
    """
    if current_user.role not in ["INSTRUCTOR_JEFE", "ADMIN"]:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para acceder a esta información"
        )
    instructors = service.get_club_instructors(club_id)

    return instructors


@router.post("/validate-selection/")
async def validate_instructor_selection(
    instructor_id: UUID,
    service: ClubInstructorService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Valida si un instructor puede ser asignado al tirador actual
    """
    try:
        shooter_id = current_user.id
        is_valid, error_msg = service.validate_instructor_selection(
            instructor_id, shooter_id
        )
        if is_valid:
            return {
                "valid": True,
                "message": "Instructor válido para el tirador",
            }
        else:
            return {
                "valid": False,
                "message": error_msg,
            }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error al validar instructor: {str(e)}",
        }
