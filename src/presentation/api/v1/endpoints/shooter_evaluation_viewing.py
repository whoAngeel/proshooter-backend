from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from src.infraestructure.database.session import get_db
from src.infraestructure.auth.jwt_config import get_current_user
from src.application.services.shooter_evaluation_viewing import (
    ShooterEvaluationViewingService,
)
from src.presentation.schemas.shooter_evaluation_viewing import *
from enum import Enum
from typing import Optional

router = APIRouter(prefix="/shooter/evaluations", tags=["Shooter Evaluations"])


class SessionEvaluationStatus(str, Enum):
    evaluated = "evaluated"
    pending = "pending"
    no_instructor = "no_instructor"


@router.get("/sessions/", response_model=SessionsWithEvaluationResponse)
async def get_my_sessions_with_evaluations(
    status_filter: Optional[SessionEvaluationStatus] = Query(
        None, description="Filtrar por estado: evaluated, pending, no_instructor"
    ),
    limit: int = Query(20, ge=1, le=50),
    service: ShooterEvaluationViewingService = Depends(),
    current_user=Depends(get_current_user),
):
    """
    📋 Obtiene sesiones del tirador con estado de evaluación

    **Estados:**
    - `evaluated`: Sesión evaluada por instructor
    - `pending`: Sesión con instructor asignado, evaluación pendiente
    - `no_instructor`: Sesión sin instructor (no requiere evaluación)
    """
    try:
        result = service.get_shooter_sessions_with_evaluation_status(
            shooter_id=current_user.id,
            limit=limit,
            status_filter=status_filter.value if status_filter else None,
        )

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{evaluation_id}/", response_model=EvaluationDetailResponse)
async def get_evaluation_detail(
    evaluation_id: UUID,
    service: ShooterEvaluationViewingService = Depends(),
    current_user=Depends(get_current_user),
):
    """
    📊 Obtiene detalle completo de una evaluación específica
    """
    try:
        result = service.get_evaluation_detail(evaluation_id, current_user.id)

        if "error" in result:
            status_code = 404 if "no encontrada" in result["error"] else 403
            raise HTTPException(status_code=status_code, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/", response_model=EvaluationSummaryResponse)
async def get_evaluation_summary(
    service: ShooterEvaluationViewingService = Depends(),
    current_user=Depends(get_current_user),
):
    """
    📈 Resumen de todas las evaluaciones del tirador

    **Incluye:**
    - Promedio general de puntuaciones
    - Tendencia de mejora
    - Distribución por instructor
    - Última evaluación
    """
    try:
        result = service.get_evaluation_summary(current_user.id)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending-count")
async def get_pending_evaluations_count(
    current_user=Depends(get_current_user),
    service: ShooterEvaluationViewingService = Depends(),
):
    """
    🔔 Obtiene número de evaluaciones pendientes (para notificaciones)
    """
    try:
        result = service.get_shooter_sessions_with_evaluation_status(
            shooter_id=current_user.id, status_filter="pending"
        )

        return {
            "pending_count": len(result.get("sessions", [])),
            "has_pending": len(result.get("sessions", [])) > 0,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
