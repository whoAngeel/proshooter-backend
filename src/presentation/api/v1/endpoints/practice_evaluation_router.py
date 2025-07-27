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
    EvaluationEditRequest,
    EvaluationFormData,
)
from src.infraestructure.database.repositories.practice_evaluation_repo import (
    PracticeEvaluationRepository,
)
from src.infraestructure.database.session import get_db


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


@router.post(
    "/sessions/{session_id}/evaluate/", response_model=EvaluationCreateResponse
)
async def create_evaluation(
    session_id: UUID,
    evaluation_data: EvaluationCreateRequest,
    service: PracticeEvaluationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Crea evaluación completa de la sesión
    - Combina datos automáticos + manuales del instructor
    - Actualiza estadísticas avanzadas del tirador
    - Marca sesión como evaluada
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

        result = service.create_evaluation(session_id, current_user.id, evaluation_data)
        return EvaluationCreateResponse(**result)
    except HTTPException as e:
        return EvaluationCreateResponse(
            success=False, error=str(e), message=str(e.detail)
        )
    except Exception as e:
        return EvaluationCreateResponse(
            success=False, error=str(e), message="Error interno al crear evaluación"
        )


@router.get("/sessions/{session_id}/evaluation/", response_model=EvaluationResponse)
async def get_session_evaluation(
    session_id: UUID,
    service: PracticeEvaluationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene evaluación completa de una sesión
    - Incluye datos automáticos y manuales del instructor
    - Calcula estadísticas avanzadas
    """
    try:
        evaluation = service.get_by_session_id(session_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluación no encontrada")
        if (evaluation.evaluator_id != current_user.id) and current_user.role not in [
            RoleEnum.INSTRUCTOR,
            RoleEnum.ADMIN,
            RoleEnum.INSTRUCTOR_JEFE,
        ]:
            raise HTTPException(
                status_code=403, detail="No tienes permiso para ver esta evaluación"
            )

        evaluation_dict = evaluation.__dict__.copy()
        # Convierte la clasificación corta a valor largo
        evaluation_dict["classification"] = service.get_classification_value(
            evaluation.classification
        )
        return EvaluationResponse(**evaluation_dict)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/my-evaluations/")
async def get_my_evaluations(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    service: PracticeEvaluationService = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene evaluaciones del usuario actual
    """
    try:
        if current_user.role not in [
            RoleEnum.INSTRUCTOR,
            RoleEnum.ADMIN,
            RoleEnum.INSTRUCTOR_JEFE,
        ]:
            raise HTTPException(
                status_code=403, detail="Solo instructores pueden ver sus evaluaciones"
            )

        evaluations = service.get_by_evaluator(
            evaluator_id=current_user.id, limit=limit, skip=skip
        )

        # Utiliza el servicio para obtener el nombre completo del tirador
        evaluation_summaries = []
        for eval in evaluations:
            shooter_name = (
                service.get_shooter_full_name(eval.session.shooter_id)
                if eval.session and eval.session.shooter_id
                else "Desconocido"
            )
            summary = {
                "id": eval.id,
                "session_id": eval.session_id,
                "shooter_name": shooter_name,
                "final_score": eval.final_score,
                "classification": service._determinate_classification(eval.final_score),
                "date": eval.date,
                "has_notes": bool(eval.instructor_notes),
            }
            evaluation_summaries.append(summary)

        return {
            "success": True,
            "evaluations": evaluation_summaries,
            "total_count": len(evaluation_summaries),
            "showing": f"{len(evaluation_summaries)} de {len(evaluations)} evaluaciones",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/sessions/{session_id}/auto-analysis")
async def get_session_auto_analysis(
    session_id: UUID,
    service: PracticeEvaluationService = Depends(),
    current_user=Depends(get_current_user),
):
    """
    Obtiene solo los datos automáticos calculados
    - Para preview antes de evaluar
    - Para verificar cálculos
    """
    try:
        if current_user.role not in ["INSTRUCTOR", "INSTRUCTOR_JEFE"]:
            raise HTTPException(
                status_code=403, detail="Solo instructores pueden acceder"
            )

        # Validar permisos básicos
        service._validate_evaluation_creation(session_id, current_user.id)

        auto_calculated = service.calculate_automatic_fields(session_id)
        suggested_zones = service.suggest_issue_zones(session_id)

        return {
            "success": True,
            "auto_calculated": auto_calculated,
            "suggested_zones": suggested_zones,
            "classification_preview": service._determinate_classification(
                auto_calculated["final_score"]
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.patch("/evaluations/{evaluation_id}/")
async def update_evaluation(
    evaluation_id: UUID,
    update_data: EvaluationEditRequest,
    service: PracticeEvaluationService = Depends(),
    current_user=Depends(get_current_user),
):
    try:
        evaluation = service.get_evaluation_by_id(evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluación no encontrada")
        if evaluation.evaluator_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Solo puedes editar tus propias evaluaciones"
            )

        updated_evaluation = service.update_evaluation(evaluation_id, update_data)
        if not updated_evaluation:
            raise HTTPException(
                status_code=500, detail="No se pudo actualizar la evaluación"
            )

        return {
            "success": True,
            "message": "Evaluación actualizada exitosamente",
            "evaluation_id": str(evaluation_id),
            "updated_fields": [
                k for k, v in update_data.dict().items() if v is not None
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.delete("/evaluations/{evaluation_id}/")
async def delete_evaluation(
    evaluation_id: UUID,
    service: PracticeEvaluationService = Depends(),
    current_user=Depends(get_current_user),
):
    try:
        evaluation = service.get_evaluation_by_id(evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluación no encontrada")
        if (
            evaluation.evaluator_id != current_user.id
            and current_user.role != RoleEnum.INSTRUCTOR_JEFE
        ):
            raise HTTPException(
                status_code=403, detail="Sin permisos para eliminar evaluación"
            )

        success = service.delete_evaluation(evaluation_id)
        if success:
            return {
                "success": True,
                "message": "Evaluación eliminada. Sesión marcada como pendiente nuevamente.",
            }
        else:
            raise HTTPException(status_code=500, detail="Error eliminando evaluación")
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}
