from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import func, or_, desc, and_
from sqlalchemy.orm import Session, joinedload

from src.infraestructure.database.models.practice_exercise_model import (
    PracticeExerciseModel,
)
from src.infraestructure.database.models.evaluation_model import PracticeEvaluationModel
from src.infraestructure.database.models.practice_session_model import (
    IndividualPracticeSessionModel,
)
from src.infraestructure.database.models.shooter_model import ShooterModel
from src.domain.enums.classification_enum import ShooterLevelEnum


class PracticeEvaluationRepository:
    @staticmethod
    def create(db: Session, evaluation_data: dict) -> PracticeEvaluationModel:
        evaluation = PracticeEvaluationModel(**evaluation_data)
        db.add(evaluation)

        # Actualizar el estado de evaluacion pendiente en la session
        session = (
            db.query(IndividualPracticeSessionModel)
            .filter(IndividualPracticeSessionModel.id == evaluation_data["session_id"])
            .first()
        )

        if session:
            session.evaluation_pending = False

        db.commit()
        db.refresh(evaluation)
        return evaluation

    @staticmethod
    def get_by_id(
        db: Session, evaluation_id: UUID
    ) -> Optional[PracticeEvaluationModel]:
        return (
            db.query(PracticeEvaluationModel)
            .options(
                joinedload(PracticeEvaluationModel.session),
                joinedload(PracticeEvaluationModel.evaluator),
            )
            .filter(PracticeEvaluationModel.id == evaluation_id)
            .first()
        )

    @staticmethod
    def get_by_session_id(
        db: Session, session_id: UUID
    ) -> Optional[PracticeEvaluationModel]:
        return (
            db.query(PracticeEvaluationModel)
            .filter(PracticeEvaluationModel.session_id == session_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[PracticeEvaluationModel]:
        return (
            db.query(PracticeEvaluationModel)
            .options(
                joinedload(PracticeEvaluationModel.session),
                joinedload(PracticeEvaluationModel.evaluator),
            )
            .order_by(desc(PracticeEvaluationModel.date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_shooter(
        db: Session, shooter_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeEvaluationModel]:
        return (
            db.query(PracticeEvaluationModel)
            .join(
                IndividualPracticeSessionModel,
                PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id,
            )
            .filter(IndividualPracticeSessionModel.shooter_id == shooter_id)
            .order_by(desc(PracticeEvaluationModel.date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_evaluator(
        db: Session, evaluator_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeEvaluationModel]:
        return (
            db.query(PracticeEvaluationModel)
            .filter(PracticeEvaluationModel.evaluator_id == evaluator_id)
            .order_by(desc(PracticeEvaluationModel.date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(
        db: Session, evaluation_id: UUID, evaluation_data: dict
    ) -> Optional[PracticeEvaluationModel]:
        evaluation = (
            db.query(PracticeEvaluationModel)
            .filter(PracticeEvaluationModel.id == evaluation_id)
            .first()
        )

        if not evaluation:
            return None

        for key, value in evaluation_data.items():
            if hasattr(evaluation, key):
                setattr(evaluation, key, value)

        db.commit()
        db.refresh(evaluation)
        return evaluation

    @staticmethod
    def delete(db: Session, evaluation_id: UUID) -> bool:
        evaluation = (
            db.query(PracticeEvaluationModel)
            .filter(PracticeEvaluationModel.id == evaluation_id)
            .first()
        )

        if not evaluation:
            return False

        # Restaurar el estado de evaluacion pendiente en la session
        session = (
            db.query(IndividualPracticeSessionModel)
            .filter(IndividualPracticeSessionModel.id == evaluation.session_id)
            .first()
        )

        if session:
            session.evaluation_pending = True

        db.delete(evaluation)
        db.commit()
        return True

    @staticmethod
    def get_shooter_evaluation_history(
        db: Session, shooter_id: UUID, limit: int = 10
    ) -> List[PracticeEvaluationModel]:
        # Obtiene las evaluaciones mas recientes de un tirador
        return (
            db.query(PracticeEvaluationModel)
            .join(
                IndividualPracticeSessionModel,
                PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id,
            )
            .filter(IndividualPracticeSessionModel.shooter_id == shooter_id)
            .order_by(desc(PracticeEvaluationModel.date))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_shooter_classification_distribution(
        db: Session, shooter_id: UUID
    ) -> Dict[str, int]:
        # Obtiene la distribucion de clasificaciones del tirador a lo largo del tiempo
        query = (
            db.query(
                PracticeEvaluationModel.classification,
                func.count(PracticeEvaluationModel.id).label("count"),
            )
            .join(
                IndividualPracticeSessionModel,
                PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id,
            )
            .filter(IndividualPracticeSessionModel.shooter_id == shooter_id)
            .group_by(PracticeEvaluationModel.classification)
            .all()
        )

        # dict con todas las clasificaciones posibles
        distribution = {level.name: 0 for level in ShooterLevelEnum}

        # actualizar los conteos reales
        for classification, count in query:
            distribution[classification.name] = count

        return distribution

    @staticmethod
    def get_issue_zones_frequency(db: Session, shooter_id: UUID) -> Dict[str, int]:
        # analiza las zonas problematicas mas frecuentes en als evaluaciones del tirador
        primary_zones = (
            db.query(
                PracticeEvaluationModel.primary_issue_zone,
                func.count(PracticeEvaluationModel.id).label("count"),
            )
            .join(
                IndividualPracticeSessionModel,
                PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id,
            )
            .filter(
                and_(
                    IndividualPracticeSessionModel.shooter_id == shooter_id,
                    PracticeEvaluationModel.primary_issue_zone.isnot(None),
                )
            )
            .group_by(PracticeEvaluationModel.primary_issue_zone)
            .all()
        )

        secondary_zones = (
            db.query(
                PracticeEvaluationModel.secondary_issue_zone,
                func.count(PracticeEvaluationModel.id).label("count"),
            )
            .join(
                IndividualPracticeSessionModel,
                PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id,
            )
            .filter(
                and_(
                    IndividualPracticeSessionModel.shooter_id == shooter_id,
                    PracticeEvaluationModel.secondary_issue_zone.isnot(None),
                )
            )
            .group_by(PracticeEvaluationModel.secondary_issue_zone)
            .all()
        )

        zones_frecuency = {}
        for zone, count in primary_zones:
            zones_frecuency[zone] = count

        for zone, count in secondary_zones:
            if zone in zones_frecuency:
                zones_frecuency[zone] += (
                    count * 0.5
                )  # damos menor peso a zonas secundarias
            else:
                zones_frecuency[zone] = count * 0.5

        return zones_frecuency

    @staticmethod
    def get_average_ratings(db: Session, shooter_id: UUID) -> Dict[str, float]:
        # calcula promedios de las calificaciones especificas (postura, agarre, etc)
        query = (
            db.query(
                func.avg(PracticeEvaluationModel.posture_rating).label("posture"),
                func.avg(PracticeEvaluationModel.grip_rating).label("grip"),
                func.avg(PracticeEvaluationModel.sight_alignment_rating).label(
                    "sight_alignment"
                ),
                func.avg(PracticeEvaluationModel.trigger_control_rating).label(
                    "trigger_control"
                ),
                func.avg(PracticeEvaluationModel.breathing_rating).label("breathing"),
            )
            .join(
                IndividualPracticeSessionModel,
                PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id,
            )
            .filter(IndividualPracticeSessionModel.shooter_id == shooter_id)
            .first()
        )

        ratings = {}

        if query:
            for key, value in query._asdict().items():
                ratings[key] = float(value) if value is not None else None

        return ratings

    @staticmethod
    def check_classification_change_criteria(
        db: Session, shooter_id: UUID, current_level: ShooterLevelEnum
    ) -> Dict[str, Any]:
        # determina si un irador cumple criterios para cambio de clasificacion
        # obtenemos las ultimas 5 evaluaciones
        recent_evaluations = (
            PracticeEvaluationRepository.get_shooter_evaluation_history(
                db, shooter_id, limit=5
            )
        )
        if len(recent_evaluations) < 3:
            return {
                "should_change": False,
                "reason": "Evaluaciones insuficientes (Minimo 3 evaluaciones requeridas)",
                "suggested_level": current_level,
            }

        # determinar nivel promedio de las evaluaciones recientes
        classfications = [eval.classification for eval in recent_evaluations]

        # contamos cuantas evaluaciones estan en cada nivel
        level_counts = {}
        for level in ShooterLevelEnum:
            level_counts[level] = classfications.count(level)

        # determinamos el nivel mas frecuente
        most_common_level = max(level_counts, key=level_counts.get)

        # si el nivel mas comun es diferente al actual y aparece al menos en 3 evaluaciones
        if most_common_level != current_level and level_counts[most_common_level] >= 3:
            return {
                "should_change": True,
                "reason": f"Consistent performance in {most_common_level.name} level in {level_counts[most_common_level]} of last 5 evaluations",
                "suggested_level": most_common_level,
            }

        return {
            "should_change": False,
            "reason": f"La clasificacion actual sigue siendo apropiada",
            "suggested_level": current_level,
        }

    @staticmethod
    def get_recent_evaluations_trend(
        db: Session, shooter_id: UUID, limit: int = 10
    ) -> Dict[str, Any]:
        # analiza la tendencia de las evaluaciones recientes de un tirador
        evaluations = PracticeEvaluationRepository.get_shooter_evaluation_history(
            db, shooter_id, limit=limit
        )
        if not evaluations or len(evaluations) < 2:
            return {"trend": "insufficient_data", "scores": [], "improving": None}

        # extraer puntuaciones en orden cronologico (del masa antiguo al mas reciente)
        scores = [eval.final_score for eval in reversed(evaluations)]

        # calcular tendencia usando regrecion lineal simple
        n = len(scores)
        indices = list(range(n))

        # calcular pendiente
        mean_x = sum(indices) / n
        mean_y = sum(scores) / n

        numerator = sum((indices[i] - mean_x) * (scores[i] - mean_y) for i in range(n))
        denominator = sum((indices[i] - mean_x) ** 2 for i in range(n))

        slope = numerator / denominator if denominator != 0 else 0

        return {
            "trend": (
                "improving" if slope > 0 else "declining" if slope < 0 else "stable"
            ),
            "scores": scores,
            "improving": slope > 0,
            "trend_value": slope,
        }


"""
Gestionar el estado de evaluación pendiente en las sesiones relacionadas.
Obtener el historial de evaluaciones de un tirador para análisis de tendencias.
Analizar la distribución de clasificaciones para un tirador.
Identificar y cuantificar las zonas de problema más frecuentes.
Calcular promedios de calificaciones específicas (postura, agarre, etc.).
Determinar si un tirador cumple con los criterios para un cambio de clasificación.
Analizar tendencias en las evaluaciones recientes.

Los métodos más complejos incluyen algoritmos para:

Calcular distribuciones y frecuencias de zonas problemáticas con ponderación
Determinar si se deben aplicar cambios de clasificación basados en patrones consistentes
Calcular tendencias mediante técnicas simplificadas de regresión lineal
"""
