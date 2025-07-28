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
        # return db.query(TargetAnalysisModel).filter_by(target_image_id=image_id).all()
        query = (
            select(TargetAnalysisModel)
            .where(TargetAnalysisModel.target_image_id == image_id)
            .order_by(desc(TargetAnalysisModel.analysis_timestamp))
        )
        result = db.execute(query)
        return result.scalars().first()

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

    @staticmethod
    def create_with_scoring(
        db: Session,
        target_image_id: UUID,
        analysis_data: Dict[str, Any],
        scoring_data: Optional[Dict[str, Any]] = None,
    ) -> TargetAnalysisModel:
        """
        Crea un análisis de blanco con datos de puntuación opcionales.

        Args:
            db (Session): Sesión de base de datos.
            target_image_id (UUID): ID de la imagen del blanco.
            analysis_data (Dict[str, Any]): Datos del análisis.
            scoring_data (Optional[Dict[str, Any]]): Datos de puntuación.

        Returns:
            TargetAnalysisModel: El modelo de análisis creado.
        """
        combined_data = {
            "target_image_id": target_image_id,
            **analysis_data,
        }

        # agregar datos de puntuacion si estan disponibles
        if scoring_data:
            combined_data.update(
                {
                    "total_score": scoring_data.get("total_score", 0),
                    "average_score_per_shot": scoring_data.get(
                        "average_score_per_shot", 0.0
                    ),
                    "max_score_achieved": scoring_data.get("max_score_achieved", 0),
                    "score_distribution": scoring_data.get("score_distribution", {}),
                    "shooting_group_diameter": scoring_data.get(
                        "shooting_group_diameter"
                    ),
                    "group_center_x": scoring_data.get("group_center_x"),
                    "group_center_y": scoring_data.get("group_center_y"),
                }
            )
        return TargetAnalysisRepository.create(db, combined_data)

    @staticmethod
    def update_scoring_data(
        db: Session, analysis_id: UUID, scoring_data: Dict[str, Any]
    ) -> Optional[TargetAnalysisModel]:
        """
        Actualiza los datos de puntuación de un análisis existente.

        Args:
            db (Session): Sesión de base de datos.
            analysis_id (UUID): ID del análisis a actualizar.
            scoring_data (Dict[str, Any]): Datos de puntuación a actualizar.

        Returns:
            Optional[TargetAnalysisModel]: El modelo actualizado o None si no se encontró.
        """
        # Preparar datos de actualización solo para campos de puntuación
        update_data = {}

        if "total_score" in scoring_data:
            update_data["total_score"] = scoring_data["total_score"]
        if "average_score_per_shot" in scoring_data:
            update_data["average_score_per_shot"] = scoring_data[
                "average_score_per_shot"
            ]
        if "max_score_achieved" in scoring_data:
            update_data["max_score_achieved"] = scoring_data["max_score_achieved"]
        if "score_distribution" in scoring_data:
            update_data["score_distribution"] = scoring_data["score_distribution"]
        if "shooting_group_diameter" in scoring_data:
            update_data["shooting_group_diameter"] = scoring_data[
                "shooting_group_diameter"
            ]
        if "group_center_x" in scoring_data:
            update_data["group_center_x"] = scoring_data["group_center_x"]
        if "group_center_y" in scoring_data:
            update_data["group_center_y"] = scoring_data["group_center_y"]

        # Usar método update existente
        return TargetAnalysisRepository.update(db, analysis_id, update_data)

    @staticmethod
    def get_analyses_with_scoring(
        db: Session, target_image_id: UUID
    ) -> List[TargetAnalysisModel]:
        """
        Obtiene todos los análisis de un blanco con datos de puntuación.

        Args:
            db (Session): Sesión de base de datos.
            target_image_id (UUID): ID de la imagen del blanco.

        Returns:
            List[TargetAnalysisModel]: Lista de análisis con datos de puntuación.
        """
        query = (
            select(TargetAnalysisModel).where(
                TargetAnalysisModel.target_image_id == target_image_id
            ),
            TargetAnalysisModel.total_score > 0,
        )  # filtrar solo los que tienen puntuacion
        result = db.execute(query)
        return result.scalars().all()

    @staticmethod
    def get_scoring_stats_for_session(db: Session, session_id: UUID) -> Dict[str, Any]:
        """
        Obtiene estadísticas de puntuación para una sesión completa
        Complementa el método existente get_analysis_stats_for_session
        """
        query = """
        SELECT
            COUNT(ta.id) as total_analyses_with_scoring,
            SUM(ta.total_score) as total_session_score,
            AVG(ta.total_score) as avg_score_per_exercise,
            AVG(ta.average_score_per_shot) as avg_score_per_shot,
            MAX(ta.max_score_achieved) as best_shot_in_session,
            AVG(ta.shooting_group_diameter) as avg_group_diameter
        FROM target_analyses ta
        JOIN target_images ti ON ta.target_image_id = ti.id
        JOIN practice_exercises pe ON pe.target_image_id = ti.id
        WHERE pe.session_id = :session_id
        AND ta.total_score > 0  -- Solo análisis con puntuación
        """

        result = db.execute(query, {"session_id": str(session_id)})
        row = result.fetchone()

        if row and row[0] > 0:  # Si hay análisis con puntuación
            return {
                "total_analyses_with_scoring": row[0] or 0,
                "total_session_score": row[1] or 0,
                "avg_score_per_exercise": float(row[2] or 0),
                "avg_score_per_shot": float(row[3] or 0),
                "best_shot_in_session": row[4] or 0,
                "avg_group_diameter": float(row[5] or 0) if row[5] else None,
                "has_scoring_data": True,
            }

        return {
            "total_analyses_with_scoring": 0,
            "total_session_score": 0,
            "avg_score_per_exercise": 0.0,
            "avg_score_per_shot": 0.0,
            "best_shot_in_session": 0,
            "avg_group_diameter": None,
            "has_scoring_data": False,
        }

    @staticmethod
    def get_shooter_scoring_evolution(
        db: Session, shooter_id: UUID, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la evolución de puntuación de un tirador
        """
        query = """
        SELECT
            ta.analysis_timestamp,
            ta.total_score,
            ta.average_score_per_shot,
            ta.accuracy_percentage,
            ta.shooting_group_diameter,
            pe.exercise_type,
            ps.session_date
        FROM target_analyses ta
        JOIN target_images ti ON ta.target_image_id = ti.id
        JOIN practice_exercises pe ON pe.target_image_id = ti.id
        JOIN practice_sessions ps ON pe.session_id = ps.id
        WHERE ps.shooter_id = :shooter_id
        AND ta.total_score > 0
        ORDER BY ta.analysis_timestamp DESC
        LIMIT :limit
        """

        result = db.execute(query, {"shooter_id": str(shooter_id), "limit": limit})

        evolution = []
        for row in result.fetchall():
            evolution.append(
                {
                    "analysis_timestamp": row[0],
                    "total_score": row[1],
                    "average_score_per_shot": row[2],
                    "accuracy_percentage": row[3],
                    "group_diameter": row[4],
                    "exercise_type": row[5],
                    "session_date": row[6],
                }
            )

        return evolution

    @staticmethod
    def check_has_scoring_data(db: Session, analysis_id: UUID) -> bool:
        """
        Verifica si un análisis específico tiene datos de puntuación
        """
        query = select(TargetAnalysisModel.total_score).where(
            TargetAnalysisModel.id == analysis_id
        )
        result = db.execute(query)
        score = result.scalar_one_or_none()
        return score is not None and score > 0
