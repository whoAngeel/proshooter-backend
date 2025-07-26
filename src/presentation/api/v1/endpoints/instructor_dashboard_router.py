from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from src.presentation.schemas.instructor_dashboard import (
    InstructorDashboardResponse,
    AssignedSessionsResponse,
    SessionDetailsResponse,
    SessionSearchFilters,
    AssignedSessionSummary,
)
from src.domain.enums.role_enum import RoleEnum
from src.application.services.instructor_dashboard import InstructorDashboardService
from src.infraestructure.auth.jwt_config import get_current_user

router = APIRouter(prefix="/instructor", tags=["Dashboard para instructores"])


@router.get("/dashboard/", response_model=InstructorDashboardResponse)
async def get_instructor_dashboard(
    service: InstructorDashboardService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Dashboard principal del instructor

    - Resumen de estadisticas
    - Sesiones pendientes urgentes
    - Sesiones recientes
    """
    try:
        if current_user.role not in [
            RoleEnum.INSTRUCTOR,
            RoleEnum.INSTRUCTOR_JEFE,
            RoleEnum.ADMIN,
        ]:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        instructor_id = current_user.id

        # stats
        stats = service.get_instructor_dashboard_stats(instructor_id)

        # recent_sessions
        recent_sessions = service.get_assigned_sessions(
            instructor_id, include_evaluated=True
        )

        # urgent_sessions
        urgent_sessions = [
            s for s in recent_sessions if s.evaluation_pending and s.days_pending > 7
        ]

        return InstructorDashboardResponse(
            success=True,
            stats=stats,
            urgent_sessions=urgent_sessions,
            recent_sessions=recent_sessions,
        )
    except HTTPException:
        raise
    except Exception as e:
        return InstructorDashboardResponse(success=False, error=str(e))


@router.get("/assigned-sessions/")
async def get_assigned_sessions(
    included_evaluated: bool = Query(False, description="Incluir sesiones evaluadas"),
    limit: int = Query(20, ge=1, le=100, description="Límite de sesiones a retornar"),
    offset: int = Query(0, ge=0, description="Número de sesiones a omitir"),
    service: InstructorDashboardService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    try:
        if current_user.role not in [
            RoleEnum.INSTRUCTOR,
            RoleEnum.INSTRUCTOR_JEFE,
            RoleEnum.ADMIN,
        ]:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        instructor_id = current_user.id

        all_sessions = service.get_assigned_sessions(
            instructor_id, include_evaluated=included_evaluated
        )

        # aplicar paginacion
        paginated_sessions = all_sessions[offset : offset + limit]

        pending_count = len([s for s in all_sessions if s.evaluation_pending])
        evaluated_count = len([s for s in all_sessions if not s.evaluation_pending])

        return AssignedSessionsResponse(
            success=True,
            sessions=paginated_sessions,
            total_count=len(all_sessions),
            pending_count=pending_count,
            evaluated_count=evaluated_count,
        )
    except HTTPException:
        raise
    except Exception as e:
        return AssignedSessionsResponse(
            success=False, error=str(e), sessions=[], total_count=0
        )


@router.get("/sessions/{session_id}/details/", response_model=SessionDetailsResponse)
async def get_session_details(
    session_id: UUID = Path(..., description="ID de la sesión"),
    service: InstructorDashboardService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Detalles completos de una sesión para evaluación
    - Información del tirador
    - Lista de ejercicios con resultados
    - Imágenes de blancos y análisis
    - Datos para formulario de evaluación"""
    try:
        if current_user.role not in [
            RoleEnum.INSTRUCTOR,
            RoleEnum.INSTRUCTOR_JEFE,
            RoleEnum.ADMIN,
        ]:
            raise HTTPException(
                status_code=403, detail="Solo instructores pueden acceder."
            )
        instructor_id = current_user.id

        session_details = service.get_session_details_for_evaluation(
            session_id, instructor_id
        )

        return SessionDetailsResponse(success=True, session_details=session_details)

    except HTTPException:
        raise
    except Exception as e:
        return SessionDetailsResponse(success=False, error=str(e))


@router.get("/sessions/search/")
async def search_assigned_sessions(
    evaluation_status: Optional[str] = Query(
        None, description="pending, evaluated, all"
    ),
    date_from: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    min_accuracy: Optional[float] = Query(None),
    shooter_name: Optional[str] = Query(None, description="Nombre del tirador"),
    limit: int = Query(20, ge=1, le=100, description="Límite de sesiones a retornar"),
    offset: int = Query(0, ge=0, description="Número de sesiones a omitir"),
    service: InstructorDashboardService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Búsqueda avanzada de sesiones asignadas
    - Filtros múltiples
    - Búsqueda por nombre de tirador
    - Rango de fechas
    """
    try:
        if current_user.role not in [
            RoleEnum.INSTRUCTOR,
            RoleEnum.INSTRUCTOR_JEFE,
            RoleEnum.ADMIN,
        ]:
            raise HTTPException(
                status_code=403, detail="Solo instructores pueden acceder."
            )
        instructor_id = current_user.id
        # construir filtros
        filters = {
            "evaluation-status": evaluation_status,
            "date_from": date_from,
            "date_to": date_to,
            "min_accuracy": min_accuracy,
            "shooter_name": shooter_name,
        }

        filters = {k: v for k, v in filters.items() if v is not None}

        filtered_sessions = service.search_assigned_sessions(instructor_id, filters)

        paginated_sessions = filtered_sessions[offset : offset + limit]

        return {
            "success": True,
            "sessions": paginated_sessions,
            "total_found": len(filtered_sessions),
            "showing": len(paginated_sessions),
            "filters_applied": filters,
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sessions": [],
            "total_found": 0,
            "showing": 0,
            "filters_applied": {},
        }


@router.get("/stats/")
async def get_instructor_stats(
    service: InstructorDashboardService = Depends(),
    current_user=Depends(get_current_user),
):
    """
    Estadísticas detalladas del instructor
    """
    try:
        if current_user.role not in [RoleEnum.INSTRUCTOR, RoleEnum.INSTRUCTOR_JEFE]:
            raise HTTPException(
                status_code=403, detail="Solo instructores pueden acceder"
            )

        instructor_id = current_user.id

        stats = service.get_instructor_dashboard_stats(instructor_id)

        return {"success": True, "stats": stats, "instructor_id": str(instructor_id)}

    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/sessions/urgent/")
async def get_urgent_sessions(
    service: InstructorDashboardService = Depends(),
    current_user=Depends(get_current_user),
):
    """
    Obtiene solo sesiones urgentes (>7 días pendientes)
    """
    try:
        if current_user.role not in [RoleEnum.INSTRUCTOR, RoleEnum.INSTRUCTOR_JEFE]:
            raise HTTPException(
                status_code=403, detail="Solo instructores pueden acceder"
            )

        instructor_id = current_user.id

        all_sessions = service.get_assigned_sessions(
            instructor_id, include_evaluated=False
        )
        urgent_sessions = [s for s in all_sessions if s.days_pending > 7]

        return {
            "success": True,
            "urgent_sessions": urgent_sessions,
            "count": len(urgent_sessions),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
