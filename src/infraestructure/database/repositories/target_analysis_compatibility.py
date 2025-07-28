from typing import Optional
from uuid import UUID
from src.infraestructure.database.models.target_analysis_model import (
    TargetAnalysisModel,
)
from sqlalchemy.orm import Session
from src.infraestructure.database.models.target_image_model import TargetImageModel
from src.infraestructure.database.repositories.target_analysis_repo import (
    TargetAnalysisRepository,
)


class TargetAnalysisRepositoryCompatibility:
    """
    Wrapper que asegura que cualquier código existente siga funcionando
    mientras gradualmente se migra al nuevo sistema
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = TargetAnalysisRepository()

    def create_legacy(self, analysis_data: dict) -> TargetAnalysisModel:
        """Crea análisis usando formato legacy"""
        return TargetAnalysisRepository.create(self.db, analysis_data)

    def create_enhanced(
        self, target_image_id: UUID, basic_data: dict, scoring_data: dict = None
    ) -> TargetAnalysisModel:
        """Crea análisis con datos mejorados"""
        return TargetAnalysisRepository.create_with_scoring(
            self.db, target_image_id, basic_data, scoring_data
        )

    def update_legacy(
        self, analysis_id: UUID, data: dict
    ) -> Optional[TargetAnalysisModel]:
        """Actualiza usando formato legacy"""
        return TargetAnalysisRepository.update(self.db, analysis_id, data)

    def update_only_scoring(
        self, analysis_id: UUID, scoring_data: dict
    ) -> Optional[TargetAnalysisModel]:
        """Actualiza solo datos de puntuación"""
        return TargetAnalysisRepository.update_scoring_data(
            self.db, analysis_id, scoring_data
        )
