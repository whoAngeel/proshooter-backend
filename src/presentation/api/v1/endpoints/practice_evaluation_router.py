from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional
from uuid import UUID

from datetime import datetime

from src.application.services.practice_evaluation_service import (
    PracticeEvaluationService,
)
from src.domain.enums.role_enum import RoleEnum
from src.domain.enums.classification_enum import ShooterLevelEnum
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.practice_evaluation_schema import (
    EvaluationCreateRequest,
    EvaluationCreateResponse,
    EvaluationFormResponse,
    EvaluationResponse,
)


router = APIRouter(
    prefix="/instructor",
    tags=["Evaluaciones por parte del instructor"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/sessions/{session_id}/evaluation-form/", response_model=EvaluationFormResponse
)
async def get_evaluation_form_data(
    session_id: UUID,
    service: PracticeEvaluationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene datos para pre-llenar formulario de evaluación
    - Campos automáticos calculados
    - Zonas problema sugeridas por IA
    - Contexto del tirador
    """
    try:
        if current_user.role not in [
            RoleEnum.INSTRUCTOR,
            RoleEnum.ADMIN,
            RoleEnum.INSTRUCTOR_JEFE,
        ]:
            raise HTTPException(
                status_code=403, detail="Solo instructores pueden evaluar"
            )
        form_data = service.get_evaluation_form_data(session_id, current_user.id)

        return EvaluationFormResponse(success=True, form_data=form_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        return EvaluationFormResponse(success=False, error=str(e))
