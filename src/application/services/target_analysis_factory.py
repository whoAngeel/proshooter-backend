from sqlalchemy.orm import Session
from fastapi import Depends
from src.infraestructure.database.session import get_db
from src.application.services.enhanced_target_analysis_service import (
    EnhancedTargetAnalysisService,
)
from src.application.services.target_analysis_service_legacy import (
    LegacyTargetAnalysisService,
)


class TargetAnalysisServiceFactory:
    """Factory para crear diferentes tipos de servicios de análisis"""

    @staticmethod
    def create_enhanced_service(
        db: Session = Depends(get_db),
    ) -> EnhancedTargetAnalysisService:
        """Crea servicio mejorado con puntuación"""
        return EnhancedTargetAnalysisService(db)

    @staticmethod
    def create_legacy_service(
        db: Session = Depends(get_db),
    ) -> LegacyTargetAnalysisService:
        """Crea servicio de compatibilidad legacy"""
        return LegacyTargetAnalysisService(db)

    @staticmethod
    def create_default_service(
        db: Session = Depends(get_db),
    ) -> EnhancedTargetAnalysisService:
        """Crea servicio por defecto (mejorado)"""
        return TargetAnalysisServiceFactory.create_enhanced_service(db)
