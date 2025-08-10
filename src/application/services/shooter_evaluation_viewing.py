from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from fastapi import Depends
import logging

from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository,
)
from src.infraestructure.database.repositories.practice_evaluation_repo import (
    PracticeEvaluationRepository,
)
from src.infraestructure.database.models.practice_session_model import (
    IndividualPracticeSessionModel,
)
from src.infraestructure.database.models.evaluation_model import PracticeEvaluationModel
from src.infraestructure.database.session import get_db

logger = logging.getLogger(__name__)


class ShooterEvaluationViewingService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.session_repo = PracticeSessionRepository()
        self.evaluation_repo = PracticeEvaluationRepository()

    def get_shooter_sessions_with_evaluation_status(
        self,
        shooter_id: UUID,
        limit: int = 20,
        status_filter: Optional[str] = None,  # evaluated, pending, "no_instructor"
    ) -> Dict[str, Any]:
        try:
            sessions = self.session_repo.get_finished_sessions_by_shooter(
                self.db, shooter_id, limit=limit
            )
            sessions_data = []
            counts = {"evaluated": 0, "pending": 0, "no_instructor": 0}

            for session in sessions:
                evaluation = None
                if session.instructor_id:
                    evaluation = self.evaluation_repo.get_by_session_id(
                        self.db, session.id
                    )

                # Determinar estado
                if not session.instructor_id:
                    status = "no_instructor"
                elif evaluation:
                    status = "evaluated"
                else:
                    status = "pending"

                counts[status] += 1

                # Filtrar si se especifica
                if status_filter and status != status_filter:
                    continue

                session_data = {
                    "session_id": str(session.id),
                    "date": session.date,
                    "location": session.location,
                    "total_shots": session.total_shots_fired,
                    "accuracy": session.accuracy_percentage,
                    "total_score": getattr(session, "total_session_score", 0),
                    "instructor_id": (
                        str(session.instructor_id) if session.instructor_id else None
                    ),
                    "instructor_name": (
                        session.instructor.full_name if session.instructor else None
                    ),
                    "evaluation_status": status,
                    "evaluation_pending": session.evaluation_pending,
                    "exercises_count": len(session.exercises),
                    "finalization_date": session.updated_at,
                }

                # Agregar datos de evaluación si existe
                if evaluation:
                    session_data["evaluation"] = {
                        "id": str(evaluation.id),
                        "final_score": evaluation.final_score,
                        "overall_technique_rating": evaluation.overall_technique_rating,
                        "evaluation_date": evaluation.date,
                        "strengths": evaluation.strengths,
                        "weaknesses": evaluation.weaknesses,
                        "recomendations": evaluation.recomendations,
                        "instructor_notes": evaluation.instructor_notes,
                        "classification": (
                            evaluation.classification.value
                            if evaluation.classification
                            else None
                        ),
                        "primary_issue_zone": evaluation.primary_issue_zone,
                        "secondary_issue_zone": evaluation.secondary_issue_zone,
                        "avg_reaction_time": evaluation.avg_reaction_time,
                        "avg_draw_time": evaluation.avg_draw_time,
                        "avg_reload_time": evaluation.avg_reload_time,
                        "hit_factor": evaluation.hit_factor,
                    }

                sessions_data.append(session_data)

            return {
                "sessions": sessions_data,
                "total_sessions": len(sessions),
                "counts": counts,
                "shooter_id": str(shooter_id),
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo sesiones con evaluaciones: {str(e)}")
            return {"error": str(e)}

    def get_evaluation_detail(
        self, evaluation_id: UUID, shooter_id: UUID
    ) -> Dict[str, Any]:
        """
        Obtiene detalle completo de una evaluación
        """
        try:
            evaluation = self.evaluation_repo.get_by_id(self.db, evaluation_id)
            if not evaluation:
                return {"error": "Evaluación no encontrada"}

            # Verificar que pertenece al shooter
            if evaluation.session.shooter_id != shooter_id:
                return {"error": "No autorizado"}

            session = evaluation.session

            return {
                "evaluation_id": str(evaluation.id),
                "session_info": {
                    "session_id": str(session.id),
                    "date": session.date,
                    "location": session.location,
                    "total_shots": session.total_shots_fired,
                    "accuracy": session.accuracy_percentage,
                    "total_score": getattr(session, "total_session_score", 0),
                    "exercises_count": len(session.exercises),
                },
                "instructor_info": {
                    "instructor_id": str(session.instructor_id),
                    "instructor_name": (
                        session.instructor.full_name if session.instructor else None
                    ),
                    "instructor_email": (
                        session.instructor.email if session.instructor else None
                    ),
                },
                "evaluation_scores": {
                    "final_score": evaluation.final_score,
                    "overall_technique_rating": evaluation.overall_technique_rating,
                    "classification": (
                        evaluation.classification.value
                        if evaluation.classification
                        else None
                    ),
                },
                "feedback": {
                    "strengths": evaluation.strengths,
                    "weaknesses": evaluation.weaknesses,
                    "recomendations": evaluation.recomendations,
                    "instructor_notes": evaluation.instructor_notes,
                },
                "issue_analysis": {
                    "primary_issue_zone": evaluation.primary_issue_zone,
                    "secondary_issue_zone": evaluation.secondary_issue_zone,
                },
                "performance_metrics": {
                    "avg_reaction_time": evaluation.avg_reaction_time,
                    "avg_draw_time": evaluation.avg_draw_time,
                    "avg_reload_time": evaluation.avg_reload_time,
                    "hit_factor": evaluation.hit_factor,
                },
                "evaluation_metadata": {
                    "date": evaluation.date,
                    "created_at": evaluation.created_at,
                    "updated_at": evaluation.updated_at,
                },
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo detalle de evaluación: {str(e)}")
            return {"error": str(e)}

    def get_evaluation_summary(self, shooter_id: UUID) -> Dict[str, Any]:
        """Resumen de evaluation del tirador"""
        try:
            evaluations = (
                self.db.query(PracticeEvaluationModel)
                .join(PracticeEvaluationModel.session)
                .filter(IndividualPracticeSessionModel.shooter_id == shooter_id)
                .order_by(PracticeEvaluationModel.date.desc())
                .all()
            )

            if not evaluations:
                return {
                    "total_evaluations": 0,
                    "average_score": 0.0,
                    "latest_evaluation": None,
                    "score_trend": 0.0,
                    "evaluations_by_instructor": {},
                }

            # Calcular estadísticas
            scores = [e.final_score for e in evaluations if e.final_score]
            avg_score = sum(scores) / len(scores) if scores else 0.0

            # Tendencia (últimas 3 vs anteriores 3)
            score_trend = 0.0
            if len(scores) >= 6:
                recent_avg = sum(scores[:3]) / 3
                previous_avg = sum(scores[3:6]) / 3
                score_trend = recent_avg - previous_avg

            # Agrupar por instructor
            evaluations_by_instructor = {}
            for evaluation in evaluations:
                instructor_name = (
                    evaluation.session.instructor.full_name
                    if evaluation.session.instructor
                    else "Sin instructor"
                )
                if instructor_name not in evaluations_by_instructor:
                    evaluations_by_instructor[instructor_name] = {
                        "count": 0,
                        "avg_score": 0.0,
                        "sessions": [],
                    }

                evaluations_by_instructor[instructor_name]["count"] += 1
                evaluations_by_instructor[instructor_name]["sessions"].append(
                    {
                        "date": evaluation.date,
                        "score": evaluation.final_score,
                        "session_id": str(evaluation.session_id),
                    }
                )

            # Calcular promedios por instructor
            for instructor_data in evaluations_by_instructor.values():
                instructor_scores = [
                    s["score"] for s in instructor_data["sessions"] if s["score"]
                ]
                instructor_data["avg_score"] = (
                    sum(instructor_scores) / len(instructor_scores)
                    if instructor_scores
                    else 0.0
                )

            return {
                "total_evaluations": len(evaluations),
                "average_score": round(avg_score, 2),
                "latest_evaluation": (
                    {
                        "id": str(evaluations[0].id),
                        "date": evaluations[0].date,
                        "score": evaluations[0].final_score,
                        "instructor": (
                            evaluations[0].session.instructor.full_name
                            if evaluations[0].session.instructor
                            else None
                        ),
                    }
                    if evaluations
                    else None
                ),
                "score_trend": round(score_trend, 2),
                "evaluations_by_instructor": evaluations_by_instructor,
                "score_distribution": self._calculate_score_distribution(scores),
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen de evaluaciones: {str(e)}")
            return {"error": str(e)}

    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calcula distribución de puntuaciones por rangos"""
        distribution = {
            "excellent": 0,  # 90-100
            "good": 0,  # 80-89
            "average": 0,  # 70-79
            "below_average": 0,  # <70
        }

        for score in scores:
            if score >= 90:
                distribution["excellent"] += 1
            elif score >= 80:
                distribution["good"] += 1
            elif score >= 70:
                distribution["average"] += 1
            else:
                distribution["below_average"] += 1

        return distribution
