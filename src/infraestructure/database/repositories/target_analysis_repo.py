from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from src.infraestructure.database.models.target_analysis_model import (
    TargetAnalysisModel,
)


class TargetAnalysisRepository:
    @staticmethod
    def create(db: Session, analysis_data: dict) -> TargetAnalysisModel:
        analysis = TargetAnalysisModel(**analysis_data)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def get_by_id(db: Session, analysis_id: UUID) -> Optional[TargetAnalysisModel]:
        return db.query(TargetAnalysisModel).filter_by(id=analysis_id).first()

    @staticmethod
    def get_by_image_id(db: Session, image_id: UUID) -> List[TargetAnalysisModel]:
        return db.query(TargetAnalysisModel).filter_by(target_image_id=image_id).all()

    @staticmethod
    def update(
        db: Session, analysis_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[TargetAnalysisModel]:
        analysis = db.query(TargetAnalysisModel).filter_by(id=analysis_id).first()
        if not analysis:
            return None
        for key, value in update_data.items():
            setattr(analysis, key, value)
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def delete(db: Session, analysis_id: UUID) -> bool:
        analysis = db.query(TargetAnalysisModel).filter_by(id=analysis_id).first()
        if not analysis:
            return False
