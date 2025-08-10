from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.reports import ReportRequest, ReportType
from src.application.services.reports import ReportService
from src.domain.enums.role_enum import RoleEnum

router = APIRouter(prefix="/reports", tags=["reports"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


@router.post("/generate/")
async def generate_report(
    report_request: ReportRequest,
    service: ReportService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Generar reporte en PDF para un tirador específico.

    Permisos:
    - El tirador puede generar sus propios reportes
    - Los administradores pueden generar reportes de cualquier tirador
    """
    try:
        pdf_bytes = await service.generate_report(report_request, current_user.id)

        # Generar nombre de archivo
        filename = f"reporte_{report_request.report_type}_{report_request.shooter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generando reporte: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")


@router.get("/available-types/")
async def get_available_report_types():
    """Obtener tipos de reportes disponibles"""
    return {
        "report_types": [
            {
                "type": "session_individual",
                "name": "Reporte de Sesión Individual",
                "description": "Detalle completo de una sesión de práctica específica",
            },
            {
                "type": "monthly_summary",
                "name": "Resumen Mensual",
                "description": "Resumen de actividad y progreso mensual",
            },
            {
                "type": "annual_summary",
                "name": "Resumen Anual",
                "description": "Resumen completo de actividad anual",
            },
            {
                "type": "shooter_profile",
                "name": "Perfil del Tirador",
                "description": "Perfil completo con historial y estadísticas",
            },
        ]
    }


@router.get("/shooter/{shooter_id}/last-sessions")
async def get_shooter_last_sessions(
    shooter_id: str,
    limit: int = 10,
    service: ReportService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """Obtener últimas sesiones de un tirador para preview del reporte"""
    try:
        # Verificar permisos
        if current_user.id != shooter_id and current_user.role != RoleEnum.ADMIN:
            raise HTTPException(
                status_code=403, detail="Sin permisos para ver esta información"
            )

        results = await service.get_shooter_last_sessions(
            current_user=current_user.id, shooter_id=shooter_id, limit=limit
        )
        return {
            "shooter_id": shooter_id,
            "sessions": [dict(row) for row in results],
            "total_sessions": len(results),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" ❌Error obteniendo sesiones: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")


@router.post("/generate/quick")
async def generate_quick_report(
    shooter_id: str,
    report_type: ReportType = ReportType.MONTHLY_SUMMARY,
    days_back: int = 30,
    service: ReportService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Generar reporte rápido con parámetros predefinidos.

    Útil para generar reportes comunes sin especificar todas las fechas.
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        report_request = ReportRequest(
            shooter_id=shooter_id,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            include_images=True,
            include_analysis=True,
        )

        pdf_bytes = await service.generate_report(report_request, current_user.id)

        filename = (
            f"reporte_rapido_{shooter_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando reporte rápido: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
