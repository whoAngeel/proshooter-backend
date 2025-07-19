from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body

from src.application.services.target_analysis_service import TargetAnalysisService
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.target_analysis_schema import (
    ExerciseAnalysisResponse,
    ExerciseAnalysisRequest,
)

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}},
)


@router.post("/exercise/{exercise_id}/analyze", response_model=ExerciseAnalysisResponse)
async def analyze_exercise_image(
    exercise_id: UUID = Path(..., description="ID del ejercicio a analizar"),
    request: ExerciseAnalysisRequest = Body(..., description="Parámetros de análisis"),
    servcie: TargetAnalysisService = Depends(),
    current_user=Depends(get_current_user),
):
    """
    Analiza la imagen de un ejercicio y devuelve los resultados del análisis.
    """
    result, error = servcie.analyze_excersise_image(
        exercise_id=exercise_id,
        confidence_threshold=request.confidence_threshold,
        force_reanalysis=request.force_reanalysis,
    )

    if error:
        raise HTTPException(status_code=400, detail=error)
    return result


# @router.get(
#     "/exercises/{exercise_id}/analysis", response_model=ExerciseAnalysisResponse
# )
# async def get_exercise_analysis(
#     exercise_id: UUID,
#     service: TargetAnalysisService = Depends(),
#     current_user=Depends(get_current_user),
# ):
#     """
#     Obtiene el análisis más reciente de un ejercicio
#     """

#     result, error = service.

#     if error:
#         raise HTTPException(status_code=404, detail=error)

#     return result
