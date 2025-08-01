from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict
from uuid import UUID
import logging

from src.infraestructure.database.repositories.shooter_stats_repo import (
    ShooterStatsRepository,
)
from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository,
)
from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository,
)
from src.infraestructure.database.repositories.target_analysis_repo import (
    TargetAnalysisRepository,
)
from src.infraestructure.database.repositories.practice_evaluation_repo import (
    PracticeEvaluationRepository,
)
from src.domain.enums.classification_enum import ShooterLevelEnum
from src.infraestructure.database.models.shooter_stats_model import ShooterStatsModel
from src.infraestructure.database.models.practice_session_model import (
    IndividualPracticeSessionModel,
)
from src.infraestructure.database.models.practice_exercise_model import (
    PracticeExerciseModel,
)

logger = logging.getLogger(__name__)


class ShooterStatsService:
    def __init__(self, db: Session):
        self.db = db
        self.stats_repo = ShooterStatsRepository()
        self.session_repo = PracticeSessionRepository()
        self.exercise_repo = PracticeExerciseRepository()
        self.analysis_repo = TargetAnalysisRepository()
        self.evaluation_repo = PracticeEvaluationRepository()

    def update_stats_with_scoring_after_session(
        self, session_id: UUID, shooter_id: UUID
    ) -> bool:
        """
        ✅ MÉTODO PRINCIPAL: Actualiza estadísticas completas con puntuación
        """
        try:
            # 1. Obtener sesión
            session = self.session_repo.get_by_id(self.db, session_id)
            if not session:
                logger.error(f"Sesión {session_id} no encontrada")
                return False

            # 2. Obtener ejercicios
            exercises = self.exercise_repo.get_by_session_id(self.db, session_id)

            # 3. Obtener o crear estadísticas del tirador
            shooter_stats = (
                self.db.query(ShooterStatsModel)
                .filter_by(shooter_id=shooter_id)
                .first()
            )
            if not shooter_stats:
                shooter_stats = ShooterStatsModel(shooter_id=shooter_id)
                self.db.add(shooter_stats)

            # 4. Calcular todas las estadísticas
            basic_stats = self._calculate_basic_stats_from_session(session, exercises)
            scoring_stats = self._calculate_scoring_stats_from_session(
                session, exercises
            )
            historical_stats = self._calculate_historical_scoring_stats(shooter_id)
            exercise_type_stats = self._calculate_exercise_type_scoring_stats(
                shooter_id
            )

            # Combinar estadísticas históricas con las de tipo
            all_stats = {**historical_stats, **exercise_type_stats}

            # 5. Actualizar modelo
            self._update_shooter_stats_model(
                shooter_stats, basic_stats, scoring_stats, all_stats
            )

            self.db.commit()
            logger.info(
                f"✅ Stats con puntuación actualizadas para tirador {shooter_id}"
            )
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error actualizando stats con puntuación: {str(e)}")
            return False

    def update_basic_stats_after_session(
        self, session_id: UUID, shooter_id: UUID
    ) -> bool:
        """
        ✅ MÉTODO BÁSICO: Para compatibilidad hacia atrás (sin puntuación)
        """
        try:
            stats = self.stats_repo.get_by_shooter_id(self.db, shooter_id)
            if not stats:
                stats = self.stats_repo.create(self.db, shooter_id)
                if not stats:
                    return False

            session = self.session_repo.get_by_id(self.db, session_id)
            if not session or not session.is_finished:
                return False

            exercises = self.exercise_repo.get_by_session_id(self.db, session_id)

            # Calcular estadísticas básicas
            updates = {}
            updates.update(self._calculate_basic_stats(stats, session, exercises))
            updates.update(
                self._calculate_exercise_type_accuracy_stats(shooter_id, exercises)
            )
            updates.update(self._calculate_average_times(stats, exercises))
            updates.update(
                self._calculate_advanced_metrics(shooter_id, session, exercises)
            )
            updates.update(self._calculate_trends_and_averages(shooter_id))

            # Actualizar en BD
            self.stats_repo.update(self.db, shooter_id, updates)
            logger.info(
                f"✅ Estadísticas básicas actualizadas para tirador {shooter_id}"
            )
            return True

        except Exception as e:
            logger.error(f"⚠️ Error actualizando estadísticas básicas: {str(e)}")
            return False

    # ✅ MÉTODOS DE CÁLCULO DE PUNTUACIÓN (PRINCIPALES)
    def _calculate_scoring_stats_from_session(self, session, exercises: List) -> Dict:
        """Calcula estadísticas de puntuación de la sesión actual"""
        exercises_with_scoring = [
            ex
            for ex in exercises
            if hasattr(ex, "total_score") and getattr(ex, "total_score", 0) > 0
        ]

        if not exercises_with_scoring:
            return {
                "session_total_score": 0,
                "session_avg_score": 0.0,
                "session_best_shot": 0,
                "session_score_efficiency": 0.0,
                "exercises_with_scoring": 0,
            }

        total_score = sum(
            getattr(ex, "total_score", 0) for ex in exercises_with_scoring
        )
        total_shots = sum(ex.ammunition_used for ex in exercises_with_scoring)
        avg_score_per_shot = total_score / total_shots if total_shots > 0 else 0.0
        best_shot = max(
            getattr(ex, "max_score_achieved", 0) for ex in exercises_with_scoring
        )

        max_possible = total_shots * 10
        score_efficiency = (
            (total_score / max_possible * 100) if max_possible > 0 else 0.0
        )

        return {
            "session_total_score": total_score,
            "session_avg_score": avg_score_per_shot,
            "session_best_shot": best_shot,
            "session_score_efficiency": score_efficiency,
            "exercises_with_scoring": len(exercises_with_scoring),
        }

    def _calculate_historical_scoring_stats(self, shooter_id: UUID) -> Dict:
        """Calcula estadísticas históricas de puntuación del tirador"""
        try:
            recent_sessions = (
                self.db.query(IndividualPracticeSessionModel)
                .filter_by(shooter_id=shooter_id, is_finished=True)
                .filter(IndividualPracticeSessionModel.total_session_score > 0)
                .order_by(IndividualPracticeSessionModel.date.desc())
                .limit(10)
                .all()
            )

            if not recent_sessions:
                return {
                    "avg_score": 0.0,
                    "best_session_score": 0,
                    "best_shot_ever": 0,
                    "score_trend": 0.0,
                    "sessions_with_scoring": 0,
                }

            total_scores = [s.total_session_score for s in recent_sessions]
            avg_scores = [
                s.average_score_per_shot
                for s in recent_sessions
                if s.average_score_per_shot > 0
            ]
            best_shots = [
                s.best_shot_score for s in recent_sessions if s.best_shot_score > 0
            ]

            avg_score = sum(avg_scores) / len(avg_scores) if avg_scores else 0.0
            best_session_score = max(total_scores) if total_scores else 0
            best_shot_ever = max(best_shots) if best_shots else 0
            score_trend = self._calculate_score_trend(avg_scores)

            return {
                "avg_score": avg_score,
                "best_session_score": best_session_score,
                "best_shot_ever": best_shot_ever,
                "score_trend": score_trend,
                "sessions_with_scoring": len(recent_sessions),
            }

        except Exception as e:
            logger.error(f"Error calculando stats históricos: {str(e)}")
            return {
                "avg_score": 0.0,
                "best_session_score": 0,
                "best_shot_ever": 0,
                "score_trend": 0.0,
                "sessions_with_scoring": 0,
            }

    def _calculate_exercise_type_scoring_stats(self, shooter_id: UUID) -> Dict:
        """✅ CORREGIDO: Calcula promedios de puntuación por tipo de ejercicio"""
        try:
            exercises_with_scoring = (
                self.db.query(PracticeExerciseModel)
                .join(PracticeExerciseModel.session)
                .join(PracticeExerciseModel.exercise_type)
                .filter(
                    IndividualPracticeSessionModel.shooter_id == shooter_id,
                    IndividualPracticeSessionModel.is_finished == True,
                    PracticeExerciseModel.total_score > 0,
                )
                .all()
            )

            logger.info(
                f"🔍 Encontrados {len(exercises_with_scoring)} ejercicios con puntuación"
            )

            if not exercises_with_scoring:
                return {
                    "precision_exercise_avg_score": 0.0,
                    "reaction_exercise_avg_score": 0.0,
                    "movement_exercise_avg_score": 0.0,
                }

            # Agrupar por tipo
            precision_scores = []
            reaction_scores = []
            movement_scores = []

            for ex in exercises_with_scoring:
                if ex.exercise_type and ex.average_score_per_shot > 0:
                    exercise_type = ex.exercise_type.type.lower()
                    score = ex.average_score_per_shot

                    if exercise_type == "precision":
                        precision_scores.append(score)
                    elif exercise_type == "reaction":
                        reaction_scores.append(score)
                    elif exercise_type == "movement":
                        movement_scores.append(score)

            logger.info(
                f"📊 Precision: {len(precision_scores)}, Reaction: {len(reaction_scores)}, Movement: {len(movement_scores)}"
            )

            return {
                "precision_exercise_avg_score": (
                    round(sum(precision_scores) / len(precision_scores), 2)
                    if precision_scores
                    else 0.0
                ),
                "reaction_exercise_avg_score": (
                    round(sum(reaction_scores) / len(reaction_scores), 2)
                    if reaction_scores
                    else 0.0
                ),
                "movement_exercise_avg_score": (
                    round(sum(movement_scores) / len(movement_scores), 2)
                    if movement_scores
                    else 0.0
                ),
            }

        except Exception as e:
            logger.error(f"❌ Error calculando promedios por tipo: {str(e)}")
            return {
                "precision_exercise_avg_score": 0.0,
                "reaction_exercise_avg_score": 0.0,
                "movement_exercise_avg_score": 0.0,
            }

    def _calculate_score_trend(self, avg_scores: List[float]) -> float:
        """Calcula tendencia de puntuación (positiva = mejorando)"""
        if len(avg_scores) < 6:
            return 0.0

        recent_avg = sum(avg_scores[:3]) / 3
        previous_avg = sum(avg_scores[3:6]) / 3
        return recent_avg - previous_avg

    def _update_shooter_stats_model(
        self,
        shooter_stats,
        basic_stats: Dict,
        scoring_stats: Dict,
        all_stats: Dict,
    ):
        """✅ CORREGIDO: Actualiza TODOS los campos del modelo"""

        # Estadísticas básicas
        shooter_stats.total_shots = basic_stats.get(
            "total_shots", shooter_stats.total_shots
        )
        shooter_stats.accuracy = int(
            basic_stats.get("accuracy", shooter_stats.accuracy)
        )

        # ✅ CORREGIR: Estadísticas de puntuación general
        if hasattr(shooter_stats, "average_score"):
            shooter_stats.average_score = all_stats.get("avg_score", 0.0)
            shooter_stats.best_score_session = all_stats.get("best_session_score", 0)
            shooter_stats.best_shot_ever = all_stats.get("best_shot_ever", 0)
            shooter_stats.score_trend = all_stats.get("score_trend", 0.0)

            # ✅ AGREGAR: Promedios por tipo de ejercicio
            shooter_stats.precision_exercise_avg_score = all_stats.get(
                "precision_exercise_avg_score", 0.0
            )
            shooter_stats.reaction_exercise_avg_score = all_stats.get(
                "reaction_exercise_avg_score", 0.0
            )
            shooter_stats.movement_exercise_avg_score = all_stats.get(
                "movement_exercise_avg_score", 0.0
            )

        shooter_stats.updated_at = datetime.now()

    # ✅ MÉTODOS BÁSICOS (SIN PUNTUACIÓN) - MANTENIDOS PARA COMPATIBILIDAD
    def _calculate_basic_stats_from_session(self, session, exercises: List) -> Dict:
        """Calcula estadísticas básicas de la sesión"""
        total_shots = sum(ex.ammunition_used for ex in exercises)
        total_hits = sum(ex.hits for ex in exercises)
        accuracy = (total_hits / total_shots * 100) if total_shots > 0 else 0.0

        return {
            "total_shots": total_shots,
            "total_hits": total_hits,
            "accuracy": accuracy,
        }

    def _calculate_basic_stats(self, stats, session, exercises) -> Dict:
        """Estadísticas básicas: disparos totales, precisión general"""
        session_shots = sum(ex.ammunition_used or 0 for ex in exercises)
        precision_shots, reaction_shots = self._count_shots_by_type(exercises)

        return {
            "total_shots": stats.total_shots + session_shots,
            "presicion_shots": stats.presicion_shots + precision_shots,
            "reaction_shots": stats.reaction_shots + reaction_shots,
            "accuracy": self._calculate_overall_accuracy_from_exercises(
                exercises, stats
            ),
        }

    def _calculate_exercise_type_accuracy_stats(
        self, shooter_id: UUID, current_exercises
    ) -> Dict:
        """Precisión específica por tipo de ejercicio (sin puntuación)"""
        all_sessions = self.session_repo.get_finished_sessions_by_shooter(
            self.db, shooter_id=shooter_id, limit=50
        )
        all_exercises = []

        for session in all_sessions:
            session_exercises = self.exercise_repo.get_by_session_id(
                self.db, session.id
            )
            all_exercises.extend(session_exercises)

        precision_exercises = []
        reaction_exercises = []
        movement_exercises = []

        for ex in all_exercises:
            if ex.exercise_type and ex.ammunition_used and ex.ammunition_used > 0:
                if ex.exercise_type.type == "precision":
                    precision_exercises.append(ex)
                elif ex.exercise_type.type == "reaction":
                    reaction_exercises.append(ex)
                elif ex.exercise_type.type == "movement":
                    movement_exercises.append(ex)

        return {
            "precision_exercise_accuracy": self._calculate_type_accuracy(
                precision_exercises
            ),
            "reaction_exercise_accuracy": self._calculate_type_accuracy(
                reaction_exercises
            ),
            "movement_exercise_accuracy": self._calculate_type_accuracy(
                movement_exercises
            ),
        }

    def _calculate_average_times(self, stats, exercises) -> Dict:
        """Tiempos promedio de desenfunde"""
        reaction_times = [
            ex.reaction_time
            for ex in exercises
            if ex.reaction_time and ex.reaction_time > 0
        ]

        if reaction_times:
            current_avg = stats.draw_time_avg or 0
            new_avg = sum(reaction_times) / len(reaction_times)

            if current_avg == 0:
                draw_time_avg = new_avg
            else:
                draw_time_avg = (current_avg * 0.7) + (new_avg * 0.3)
        else:
            draw_time_avg = stats.draw_time_avg

        return {
            "draw_time_avg": round(draw_time_avg, 3),
            "reload_time_avg": stats.reload_time_avg,
        }

    def _calculate_advanced_metrics(self, shooter_id: UUID, session, exercises) -> Dict:
        """Métricas avanzadas: hit_factor, effectiveness"""
        total_hits = sum(ex.hits or 0 for ex in exercises)
        total_time = sum(ex.reaction_time or 1 for ex in exercises if ex.reaction_time)

        hit_factor = total_hits / total_time if total_time > 0 else 0

        total_shots = sum(ex.ammunition_used or 0 for ex in exercises)
        effectiveness = (
            (total_hits / total_shots) * (session.accuracy_percentage / 100)
            if total_shots > 0
            else 0
        )

        return {
            "average_hit_factor": round(hit_factor, 3),
            "effectiveness": round(effectiveness, 3),
        }

    def _calculate_trends_and_averages(self, shooter_id: UUID) -> Dict:
        """Tendencias y promedios de últimas sesiones"""
        recent_sessions = self.session_repo.get_finished_sessions_by_shooter(
            self.db, shooter_id, limit=10
        )

        if len(recent_sessions) < 2:
            return {
                "last_10_sessions_avg": (
                    recent_sessions[0].accuracy_percentage if recent_sessions else 0.0
                ),
                "trend_accuracy": 0.0,
            }

        avg_10_sessions = sum(s.accuracy_percentage for s in recent_sessions) / len(
            recent_sessions
        )

        trend = 0.0
        if len(recent_sessions) >= 6:
            last_5 = recent_sessions[:5]
            previous_5 = recent_sessions[5:10]
            avg_last_5 = sum(s.accuracy_percentage for s in last_5) / len(last_5)
            avg_prev_5 = sum(s.accuracy_percentage for s in previous_5) / len(
                previous_5
            )
            trend = avg_last_5 - avg_prev_5
        logger.info(
            f"🔄 Tendencia de precisión calculada: {trend} (últimas 10 sesiones: {avg_10_sessions})"
        )
        return {
            "last_10_sessions_avg": round(avg_10_sessions, 2),
            "trend_accuracy": round(trend, 2),
        }

    # ✅ MÉTODOS AUXILIARES
    def _calculate_overall_accuracy_from_exercises(self, exercises, stats) -> int:
        """Calcula precisión general basada en ammunition_used vs hits reales"""
        session_shots = sum(ex.ammunition_used or 0 for ex in exercises)
        session_hits = sum(ex.hits or 0 for ex in exercises)
        total_shots = stats.total_shots + session_shots

        if total_shots > 0:
            historical_hits = (stats.total_shots * stats.accuracy) // 100
            total_hits = historical_hits + session_hits
            return int((total_hits / total_shots) * 100)

        return stats.accuracy

    def _calculate_type_accuracy(self, exercises_of_type) -> float:
        """Calcula precisión promedio para un tipo específico de ejercicio"""
        if not exercises_of_type:
            return 0.0

        total_shots = sum(ex.ammunition_used or 0 for ex in exercises_of_type)
        total_hits = sum(ex.hits or 0 for ex in exercises_of_type)

        return round((total_hits / total_shots) * 100, 2) if total_shots > 0 else 0.0

    def _count_shots_by_type(self, exercises) -> tuple:
        """Cuenta disparos por tipo de ejercicio"""
        precision_shots = 0
        reaction_shots = 0

        for exercise in exercises:
            if exercise.exercise_type and exercise.ammunition_used:
                exercise_type = exercise.exercise_type.type.lower()
                if exercise_type == "precision":
                    precision_shots += exercise.ammunition_used
                elif exercise_type in ["movement", "reaction"]:
                    reaction_shots += exercise.ammunition_used

        return precision_shots, reaction_shots

    # ✅ MÉTODOS DE CONSULTA
    def get_complete_shooter_stats(self, shooter_id: UUID) -> Dict:
        """Obtiene estadísticas completas para dashboard"""
        try:
            stats = self.stats_repo.get_by_shooter_id(self.db, shooter_id)
            if not stats:
                return {"error": "Estadísticas no encontradas"}

            return {
                "basic_stats": {
                    "total_shots": stats.total_shots,
                    "accuracy": stats.accuracy,
                    "precision_shots": stats.presicion_shots,
                    "reaction_shots": stats.reaction_shots,
                },
                "scoring_stats": {
                    "average_score": getattr(stats, "average_score", 0.0),
                    "best_session_score": getattr(stats, "best_score_session", 0),
                    "best_shot_ever": getattr(stats, "best_shot_ever", 0),
                    "score_trend": getattr(stats, "score_trend", 0.0),
                    "precision_exercise_avg_score": getattr(
                        stats, "precision_exercise_avg_score", 0.0
                    ),
                    "reaction_exercise_avg_score": getattr(
                        stats, "reaction_exercise_avg_score", 0.0
                    ),
                    "movement_exercise_avg_score": getattr(
                        stats, "movement_exercise_avg_score", 0.0
                    ),
                },
                "averages": {
                    "last_10_sessions_avg": stats.last_10_sessions_avg,
                    "draw_time_avg": stats.draw_time_avg,
                    "reload_time_avg": stats.reload_time_avg,
                },
                "advanced_metrics": {
                    "average_hit_factor": stats.average_hit_factor,
                    "effectiveness": stats.effectiveness,
                    "trend_accuracy": stats.trend_accuracy,
                },
            }

        except Exception as e:
            return {"error": str(e)}

    def get_shooter_basic_stats(self, shooter_id: UUID) -> Dict:
        """Obtiene estadísticas básicas para dashboard"""
        try:
            stats = self.stats_repo.get_by_shooter_id(self.db, shooter_id)
            if not stats:
                return {
                    "total_shots": 0,
                    "accuracy": 0,
                    "last_10_sessions_avg": 0.0,
                    "precision_shots": 0,
                    "reaction_shots": 0,
                }

            return {
                "total_shots": stats.total_shots,
                "accuracy": stats.accuracy,
                "last_10_sessions_avg": stats.last_10_sessions_avg,
                "precision_shots": stats.presicion_shots,
                "reaction_shots": stats.reaction_shots,
                "trend_accuracy": stats.trend_accuracy,
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {"error": str(e)}
