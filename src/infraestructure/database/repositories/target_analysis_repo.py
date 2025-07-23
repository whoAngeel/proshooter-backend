from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, desc
from sqlalchemy.orm import Session, joinedload
from src.infraestructure.database.models.target_analysis_model import (
    TargetAnalysisModel,
)
from src.infraestructure.database.models.target_image_model import TargetImageModel


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

    @staticmethod
    def get_with_image_info(
        db: Session, analysis_id: UUID
    ) -> Optional[TargetAnalysisModel]:
        query = (
            select(TargetAnalysisModel)
            .where(TargetAnalysisModel.id == analysis_id)
            .options(joinedload(TargetAnalysisModel.target_image))
        )
        result = db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def has_analysis(db: Session, target_image_id: UUID) -> bool:
        query = (
            select(TargetAnalysisModel.id)
            .where(TargetAnalysisModel.target_image_id == target_image_id)
            .limit(1)
        )

        result = db.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    def get_analysis_stats_for_session(db: Session, session_id: UUID) -> dict:
        query = """
        SELECT
            COUNT(ta.id) as total_analyses,
            AVG(ta.total_impacts_detected) as avg_impacts,
            AVG(ta.accuracy_percentage) as avg_accuracy,
            SUM(ta.fresh_impacts_inside) as total_hits_inside,
            SUM(ta.fresh_impacts_outside) as total_hits_outside
        FROM target_analyses ta
        JOIN target_images ti ON ta.target_image_id = ti.id
        JOIN practice_exercises pe ON pe.target_image_id = ti.id
        WHERE pe.session_id = :session_id
        """
        result = db.execute(query, {"session_id": str(session_id)})
        row = result.fetchone()
        if row:
            return {
                "total_analyses": row[0] or 0,
                "avg_impacts": float(row[1] or 0),
                "avg_accuracy": float(row[2] or 0),
                "total_hits_inside": row[3] or 0,
                "total_hits_outside": row[4] or 0,
            }

        return {
            "total_analyses": 0,
            "avg_impacts": 0.0,
            "avg_accuracy": 0.0,
            "total_hits_inside": 0,
            "total_hits_outside": 0,
        }
