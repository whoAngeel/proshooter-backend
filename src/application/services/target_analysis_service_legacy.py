from typing import Optional, Tuple
from uuid import UUID
from fastapi import Depends
from sqlalchemy.orm import Session
from src.application.services.enhanced_target_analysis_service import (
    EnhancedTargetAnalysisService,
)

# from  import ExerciseAnalysisResponse
from src.presentation.schemas.target_analysis_schema import ExerciseAnalysisResponse
from src.infraestructure.database.session import get_db


class LegacyTargetAnalysisService:
    """
    Wrapper que asegura compatibilidad total con el servicio original
    Redirige todas las llamadas al servicio mejorado
    """

    def __init__(self, db: Session = Depends(get_db)):
        self.enhanced_service = EnhancedTargetAnalysisService(db)

    def analyze_excersise_image(
        self,
        exercise_id: UUID,
        confidence_threshold: float = 0.25,
        force_reanalysis: bool = False,
    ) -> Tuple[Optional[ExerciseAnalysisResponse], Optional[str]]:
        """Mantiene la firma exacta del servicio original"""
        return self.enhanced_service.analyze_excersise_image(
            exercise_id, confidence_threshold, force_reanalysis
        )

    def get_exercise_analysis(
        self, exercise_id: UUID
    ) -> Tuple[Optional[ExerciseAnalysisResponse], Optional[str]]:
        """Mantiene compatibilidad"""
        return self.enhanced_service.get_exercise_analysis(exercise_id)
