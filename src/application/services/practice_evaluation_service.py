from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime
import math


from src.infraestructure.database.repositories.practice_evaluation_repo import PracticeEvaluationRepository
from src.infraestructure.database.repositories.practice_session_repo import PracticeSessionRepository
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.infraestructure.database.repositories.shooter_stats_repo import ShooterStatsRepository
from src.infraestructure.database.repositories.user_repo import UserRepository
from src.infraestructure.database.session import get_db
from src.domain.enums.classification_enum import ShooterLevelEnum
from src.domain.enums.role_enum import RoleEnum
from src.presentation.schemas.practice_evaluation_schema import (
    PracticeEvaluationCreate,
    PracticeEvaluationRead,
    PracticeEvaluationDetail,
    PracticeEvaluationUpdate,
    PracticeEvaluationList,
    PracticeEvaluationFilter,
    ShooterEvaluationStatistics,
    RatingAnalysis
)

class PracticeEvaluationService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_evaluation(self, evaluation_data: PracticeEvaluationCreate) -> Tuple[Optional[PracticeEvaluationRead], Optional[str]]:
        try:
            # verficar que la sesion existe
            session = PracticeSessionRepository.get_by_id(self.db, evaluation_data.session_id)
            if not session:
                return None, "PRACTICE_SESSION_NOT_FOUND"

            # verificar que la sesion no tenga una evaluacion
            existing_evaluation = PracticeEvaluationRepository.get_by_session_id(self.db, evaluation_data.session_id)
            if existing_evaluation:
                return None, "SESSION_ALREADY_EVALUATED"
            # verficar que el evaluador exista (si es proporcionado)
            if evaluation_data.evaluator_id:
                evaluator = UserRepository.get_by_id(self.db, evaluation_data.evaluator_id)
                if not evaluator:
                    return None, "EVALUATOR_NOT_FOUND"
                if evaluator.role not in [RoleEnum.INSTRUCTOR, RoleEnum.INSTRUCTOR_JEFE, RoleEnum.ADMIN]:
                    return None, "EVALUATOR_NOT_AUTHORIZED"

            # convertir datos a diccionario
            evaluation_dict = evaluation_data.model_dump()

            new_evaluation = PracticeEvaluationRepository.create(self.db, evaluation_dict)

            self._update_shooter_stats(session.shooter_id, new_evaluation)

            return PracticeEvaluationRead.model_validate(new_evaluation), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_CREATING_EVALUATION: {str(e)}"

    def get_evaluation_by_id(self, evaluation_id: UUID)-> Tuple[Optional[PracticeEvaluationDetail], Optional[str]]:
        evaluation = PracticeEvaluationRepository.get_by_id(self.db, evaluation_id)
        if not evaluation:
            return None, "EVALUATION_NOT_FOUND"

        return PracticeEvaluationDetail.model_validate(evaluation), None

    def get_evaluation_by_session(self, session_id: UUID)-> Tuple[Optional[PracticeEvaluationDetail], Optional[str]]:
        session = PracticeSessionRepository.get_by_id(self.db, session_id)
        if not session:
            return None, "PRACTICE_SESSION_NOT_FOUND"

        evaluation = PracticeEvaluationRepository.get_by_session_id(self.db, session_id)
        if not evaluation:
            return None, "EVALUATION_NOT_FOUND"

        return PracticeEvaluationDetail.model_validate(evaluation), None

    def get_all_evaluations(
        self,
        filter_params: PracticeEvaluationFilter
    )-> PracticeEvaluationList:
        evaluations = []
        total_count = 0

        # aplicar filtros para los parametros proporcionados
        if filter_params.session_id:
            evaluation = PracticeEvaluationRepository.get_by_session_id(self.db, filter_params.session_id)
            evaluations = [evaluation] if evaluation else []
            total_count = 1 if evaluation else 0
        elif filter_params.shooter_id:
            evaluations = PracticeEvaluationRepository.get_by_shooter(
                self.db, filter_params.shooter_id, filter_params.skip, filter_params.limit
            )
            total_count = len(PracticeEvaluationRepository.get_by_shooter(self.db, filter_params.shooter_id))
        elif filter_params.evaluator_id:
            evaluations = PracticeEvaluationRepository.get_by_evaluator(
                self.db, filter_params.evaluator_id, filter_params.skip, filter_params.limit
            )
            total_count = len(PracticeEvaluationRepository.get_by_evaluator(self.db, filter_params.evaluator_id))
        else:
            evaluations = PracticeEvaluationRepository.get_all(self.db, filter_params.skip, filter_params.limit)

            total_query = self.db.query("PracticeEvaluationModel").count()
            total_count = total_query

        page = (filter_params.skip // filter_params.limit) + 1
        pages = math.ceil(total_count / filter_params.limit) if total_count > 0 else 1

        items = [PracticeEvaluationRead.model_validate(eval) for eval in evaluations]

        return PracticeEvaluationList(
            items=items,
            total=total_count,
            page=page,
            size=filter_params.limit,
            pages=pages
        )

    def update_evaluation(self, evaluation_id: UUID, evaluation_data: PracticeEvaluationUpdate)-> Tuple[Optional[PracticeEvaluationRead], Optional[str]]:
        try:
            # verificar que la evaluacion exista
            existing_evaluation = PracticeEvaluationRepository.get_by_id(self.db, evaluation_id)
            if not existing_evaluation:
                return None, "PRACTICE_EVALUATION_NOT_FOUND"

            # verificar que el evaluador existe (si lo proporcionan)
            if evaluation_data.evaluator_id:
                evaluator = UserRepository.get_by_id(self.db, evaluation_data.evaluator_id)
                if not evaluator:
                    return None, "EVALUATOR_NOT_FOUND"
                if evaluator.role not in [RoleEnum.INSTRUCTOR, RoleEnum.INSTRUCTOR_JEFE, RoleEnum.ADMIN]:
                    return None, "EVALUATOR_NOT_AUTHORIZED"

            # convertir datos a dict
            evaluation_dict = evaluation_data.model_dump(exclude_unset=True, exclude=True)

            updated_evaluation = PracticeEvaluationRepository.update(self.db, evaluation_id, evaluation_dict)

            if not updated_evaluation:
                return None, "ERROR_UPDATING_EVALUATION"

            # obtener la session para acceder al tirador
            session = PracticeSessionRepository.get_by_id(self.db, updated_evaluation.session_id)

            # actualizar las estadisticas del tirador si se cambiaron datos relevantes
            relevant_fields = {"final_score", "classification", "primary_issue_zone", "secondary_issue_zone"}
            if any(field in evaluation_dict for field in relevant_fields):
                self._update_shooter_stats(session.shooter_id, updated_evaluation)

            return PracticeEvaluationRead.model_validate(updated_evaluation), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPDATING_EVALUATION: {str(e)}"

    def delete_evaluation(self, evaluation_id: UUID)-> Tuple[bool, Optional[str]]:
        try:
            existing_evaluation = PracticeEvaluationRepository.get_by_id(self.db, evaluation_id)
            if not existing_evaluation:
                return False, "PRACTICE_EVALUATION_NOT_FOUND"

            session = PracticeSessionRepository.get_by_id(self.db, existing_evaluation.session_id)
            shooter_id = session.shooter_id

            success = PracticeEvaluationRepository.delete(self.db, evaluation_id)

            if not success:
                return False, "ERROR_DELETING_EVALUATION"

            # recalcular las estadisticas del tirador
            self._recalculate_shooter_stats(shooter_id)

            return True, None
        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_DELETING_EVALUATION: {str(e)}"

    def get_shooter_evaluation_statistics(self, shooter_id: UUID)-> Tuple[Optional[ShooterEvaluationStatistics], Optional[str]]:
        try:
            # verificar que el tirador exista
            shooter = ShooterRepository.get_by_user_id(self.db, shooter_id)
            if not shooter:
                return None, "SHOOTER_NOT_FOUND"

            # obtener las evaluaciones del tirador
            evaluations = PracticeEvaluationRepository.get_by_shooter(self.db, shooter_id)

            if not evaluations:
                return None, "NO_EVALUATIONS_FOUND"

            # obtener distribucion de clasificaciones
            classification_distribution = PracticeEvaluationRepository.get_shooter_classification_distribution(self.db, shooter_id)

            # zonas de problemas comunes
            issue_zones = PracticeEvaluationRepository.get_issue_zones_frequency(self.db, shooter_id)

            # analizar tendencia reciente
            trend_data = PracticeEvaluationRepository.get_recent_evaluations_trend(self.db, shooter_id)

            #obtener promedios de calificacioens especificas
            average_ratings = PracticeEvaluationRepository.get_average_ratings(self.db, shooter_id)

            # calcular puntuacion promedio
            avg_score = sum(eval.final_score for eval in evaluations) / len(evaluations)

            # verificar si se recomienda cambio de clasificacion
            classification_change = PracticeEvaluationRepository.check_classification_change_criteria(
                self.db, shooter_id, shooter.level
            )

            # obtener evaluaciones recientes para mostrar
            recent_evaluations = PracticeEvaluationRepository.get_shooter_evaluation_history(self.db, shooter_id, 5)

            # Construir el objeto de estadísticas
            statistics = ShooterEvaluationStatistics(
                shooter_id=shooter_id,
                total_evaluations=len(evaluations),
                average_score=avg_score,
                classification_distribution=classification_distribution,
                recent_trend=trend_data["trend"],
                average_ratings=average_ratings,
                common_issue_zones=issue_zones,
                classification_change_recommended=classification_change["should_change"],
                suggested_classification=classification_change["suggested_level"] if classification_change["should_change"] else None,
                latest_evaluations=[PracticeEvaluationRead.model_validate(eval) for eval in recent_evaluations]
            )

            return statistics, None
        except Exception as e:
            return None, f"ERROR_GETTING_STATISTICS: {str(e)}"

    def get_rating_analysis(self, shooter_id: UUID, category: str)-> Tuple[Optional[RatingAnalysis], Optional[str]]:
        try:
            # verficar que el tirador exista
            shooter = ShooterRepository.get_by_user_id(self.db, shooter_id)
            if not shooter:
                return None, "SHOOTER_NOT_FOUND"

            valid_categories = ['posture', "grip", "sight_alignment", "trigger_control", "breathing"]
            if category not in valid_categories:
                return None, f"INVALID_CATEGORY: Must be one of {', '.join(valid_categories)}"

            # obtener las evaluaciones del tirador
            evaluations = PracticeEvaluationRepository.get_by_shooter(self.db, shooter_id)

            if not evaluations:
                return None, "NO_EVALUATIONS_FOUND"

            # mapear el nombre de la categoria al campo correspondiente
            category_field_map = {
                "posture": "posture_rating",
                "grip": "grip_rating",
                "sight_alignment": "sight_alignment_rating",
                "trigger_control": "trigger_control_rating",
                "breathing": "breathing_rating"
            }

            field_name = category_field_map[category]

            # filtrar evaluaciones que tienen un valor para esta categoria
            relevant_evaluations = [eval for eval in evaluations if getattr(eval, field_name) is not None]

            if not relevant_evaluations:
                return None, f"NO_DATA_FOR_CATEGORY: {category}"

            # calcular el promedio
            values = [getattr(eval, field_name) for eval in relevant_evaluations]
            average = sum(values) / len(values)

            # determinar tendencia (simplificado)
            if len(relevant_evaluations) >= 3:
                recent_values = [getattr(eval, field_name) for eval in relevant_evaluations[-3:]]
                if recent_values[-1] > recent_values[0]:
                    trend = "improving"
                elif recent_values[-1] < recent_values[0]:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"

            # Generar sugerencias basadas en el promedio
            # TODO: Generar sugerencias con IA
            suggestions = None
            if average < 5:
                suggestions = f"Focus on improving {category} technique. Consider specific exercises targeting this area."
            elif average < 7:
                suggestions = f"Your {category} technique is adequate but could benefit from refinement."
            else:
                suggestions = f"Your {category} technique is strong. Continue to maintain this aspect."

            return RatingAnalysis(
                category=category,
                average=average,
                trend=trend,
                suggested_improvements=suggestions
            ), None
        except Exception as e:
            return None, f"ERROR_ANALYZING_RATING: {str(e)}"


    def _update_shooter_stats(self, shooter_id: UUID, evaluation) -> None:
        '''
        Actualiza las estadisticas del tirador basandose en la nueva evaluacion.
        Este metodo actualiza varios aspectos de las estadisticas del tirador,
        incluyendo precision media, zonas de error comunes, etc.
        '''

        try:
            # obtener las estadisticas del tirador
            shooter_stats = ShooterStatsRepository.get_by_shooter_id(self.db, shooter_id)

            if not shooter_stats:
                return

            # Obtener session de la evaluacion para acceder a los datos de disparos
            session = PracticeSessionRepository.get_by_id(self.db, evaluation.session_id)

            # actualizar estadisticas basicas
            stats_updates = {}

            # actualizar datos de error comunes
            if evaluation.primary_issue_zone:
                # simplificado, solo tomando la zona primaria actual TODO: revisar esto
                stats_updates["common_primary_zone"] = evaluation.primary_issue_zone

            # actualizar estadisticas de tiempo si estan disponibles
            if evaluation.avg_draw_time is not None:
                # media ponderada para draw_time_avg
                current_avg = shooter_stats.draw_time_avg
                new_value = evaluation.avg_draw_time

                # si el primer valor lo asignamos directamente
                if current_avg == 0:
                    stats_updates["draw_time_avg"] = new_value
                else:
                    # caso contrario, actualizamos con una media ponderada simple
                    # (damos mayor peso al valor historico para estabilidad)
                    stats_updates["draw_time_avg"] = current_avg * 0.8 + new_value * 0.2

            if evaluation.avg_reload_time is not None:
                current_avg = shooter_stats.reload_time_avg
                new_value = evaluation.avg_reload_time

                if current_avg == 0:
                    stats_updates["reload_time_avg"] = new_value
                else:
                    stats_updates["reload_time_avg"] = current_avg * 0.8 + new_value * 0.2

            # actualizar hit factor
            if evaluation.hit_factor is not None:
                current_avg = shooter_stats.average_hit_factor
                new_value = evaluation.hit_factor

                if current_avg == 0:
                    stats_updates["average_hit_factor"] = new_value
                else:
                    stats_updates["average_hit_factor"] = current_avg * 0.8 + new_value * 0.2

            # actualizar la efectividad basada en la evaluacion actual
            stats_updates["effectivenes"] = evaluation.final_score

            # actulizar estadisticas de tendencia
            trend_data = PracticeEvaluationRepository.get_recent_evaluations_trend(self.db, shooter_id)
            if "trend_value" in trend_data:
                stats_updates["trend_accuracy"] = trend_data["trend_value"]

            # calcular promedio de ultimas 10 sesiones
            recent_evaluations = PracticeEvaluationRepository.get_shooter_evaluation_history(self.db, shooter_id, 10)
            if recent_evaluations:
                avg_score = sum(eval.final_score for eval in recent_evaluations) / len(recent_evaluations)
                stats_updates["last_10_sessions_avg"] = avg_score

            # actualizar precision global basado en los datos de la sesion
            if session.total_shots_fired > 0:
                # actualizamos el total de disparos en las estadisticas
                new_total = shooter_stats.total_shots + session.total_shots_fired
                stats_updates["total_shots"] = new_total

                # calculamos la nueva precision global
                current_hits = shooter_stats.accuracy * shooter_stats.total_shots / 100
                new_hits = current_hits + session.total_hits
                new_accuracy = (new_hits / new_total) * 100
                stats_updates["accuracy"] = new_accuracy

            # actualizamos las estadisticas del tirador
            ShooterStatsRepository.update(self.db, shooter_id, stats_updates)

            # verificar si debemos actualizar la clasificacion del tirador
            self._check_and_update_classification(shooter_id)
        except Exception as e:
            print(f"❌❌⚠️⚠️Error updating shooter stats: {str(e)}")


    def _check_and_update_classification(self, shooter_id: UUID)-> None:
        '''
        Verifica si es necesario actualizar la clasificacion del tirador
        basandose en su historial reciente de evaluaciones
        '''

        try:
            shooter= ShooterRepository.get_by_user_id(self.db, shooter_id)

            if not shooter:
                return
            # verificar criterios para cambio de clasificacion
            classification_change = PracticeEvaluationRepository.check_classification_change_criteria(
                self.db, shooter_id, shooter.level
            )

            # si se recomienda un cambio actualizamos la clasificacion
            if classification_change["should_change"]:
                ShooterStatsRepository.update_classification(
                    self.db, shooter_id, classification_change["suggested_level"]
                )
        except Exception as e:
            print(f"❌❌⚠️⚠️Error checking shooter classification: {str(e)}")

    def _recalculate_shooter_stats(self, shooter_id: UUID) -> None:
        '''
        Recalcula completamente las estadisticas de un tirador basandose en todas sus sesiones y evaluaciones historicas
        '''
        try:
            # obtener todas las sesiones del tirador
            sessions = PracticeSessionRepository.get_by_shooter(self.db, shooter_id)

            # obtener todas las  evaluaciones del tirador
            evaluations = PracticeEvaluationRepository.get_by_shooter(self.db, shooter_id)

            if not sessions or not evaluations:
                return

            # inicializar contadores
            total_shots = 0
            total_hits = 0

            # acumular los disparos y aciertos de todas las sesiones
            for session in sessions:
                total_shots += session.total_shots_fired
                total_hits += session.total_hits

            # calcular precision global
            accuracy = (total_hits / total_shots) * 100 if total_shots > 0 else 0

            # calcular promedios de tiempos
            draw_times = [eval.avg_draw_time for eval in evaluations if eval.avg_draw_time is not None]
            reload_times = [eval.avg_reload_time for eval in evaluations if eval.avg_reload_time is not None]
            hit_factors = [eval.hit_factor for eval in evaluations if eval.hit_factor is not None]


            draw_time_avg = sum(draw_times) / len(draw_times) if draw_times else 0
            reload_time_avg = sum(reload_times) / len(reload_times) if reload_times else 0
            hit_factors_avg = sum(hit_factors) / len(hit_factors) if hit_factors else 0

            # obtener la ultima evaluacion para efectividad
            latest_eval = evaluations[0] if evaluations else None
            effectiveness = latest_eval.final_score if latest_eval else 0

            # analizar tendencias
            trend_data = PracticeEvaluationRepository.get_recent_evaluations_trend(
                self.db, shooter_id
            )
            trend_accuracy = trend_data.get("trend_value", 0)

            #calcular promedio de ultimas 10 sesiones
            recent_evaluations = evaluations[:10] if len(evaluations) >= 10 else evaluations
            last_10_avg = sum(eval.final_score for eval in recent_evaluations) / len(recent_evaluations) if recent_evaluations else 0

            issue_zones = PracticeEvaluationRepository.get_issue_zones_frequency(self.db, shooter_id)
            common_zone = max(issue_zones, key=issue_zones.get) if issue_zones else None

            stats_updates = {
                "total_shots": total_shots,
                "accuracy": accuracy,
                "draw_time_avg": draw_time_avg,
                "reload_time_avg": reload_time_avg,
                "average_hit_factor": hit_factors_avg,
                "effectiveness": effectiveness,
                "trend_accuracy": trend_accuracy,
                "last_10_sessions_avg": last_10_avg,
                "common_error_zones": common_zone
            }

            ShooterStatsRepository.update(self.db, shooter_id, stats_updates)
            self._check_and_update_classification(shooter_id)
        except Exception as e:
            print(f"❌❌⚠️⚠️Error recalculating shooter stats: {str(e)}")
