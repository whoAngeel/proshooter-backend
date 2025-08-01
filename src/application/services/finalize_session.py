from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Optional, List
from fastapi import HTTPException
from datetime import datetime
from fastapi import Depends
import logging

from src.infraestructure.database.session import get_db

# from src.application.services
from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository as SessionRepository,
)
from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository as ExerciseRepository,
)
from src.application.services.exercise_consolidation import ExerciseConsolidationService
from src.presentation.schemas.sesion_finalization import (
    SessionFinalizationResult,
    SessionValidationResult,
)

logger = logging.getLogger(__name__)


class SessionFinalizationService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.session_repo = SessionRepository()
        self.exercise_repo = ExerciseRepository()
        self.consolidation_service = ExerciseConsolidationService(self.db)

    def finish_session(
        self, session_id: UUID, shooter_id: UUID
    ) -> SessionFinalizationResult:
        try:
            # 1. Verificar sesión
            session = self.session_repo.get_by_id(db=self.db, session_id=session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Sesión no encontrada")

            if session.shooter_id != shooter_id:
                raise HTTPException(status_code=403, detail="Sin permisos")

            if session.is_finished:
                raise HTTPException(status_code=400, detail="Sesión ya finalizada")

            # 2. Validar que esté lista
            validation = self.validate_session_for_completion(session_id)
            if not validation.can_finish:
                raise HTTPException(status_code=400, detail=validation.reason)

            # 3. ✅ CONSOLIDAR con puntuación
            consolidation_result = (
                self.consolidation_service.consolidate_all_session_exercises(session_id)
            )

            # 4. ✅ CALCULAR totales finales CON puntuación
            final_stats = self.session_repo.calculate_totals_with_scoring(
                self.db, session_id
            )

            if final_stats.get("error"):
                raise HTTPException(
                    status_code=500,
                    detail=f"Error calculando totales: {final_stats['error']}",
                )

            # 5. Finalizar sesión
            evaluation_pending = session.instructor_id is not None
            success = self.session_repo.finish_session_with_evaluation_status(
                self.db, session_id, evaluation_pending
            )

            if not success:
                raise HTTPException(status_code=500, detail="Error finalizando")

            # 6. ✅ ACTUALIZAR estadísticas del tirador CON puntuación
            self._update_shooter_stats_with_scoring(session_id, shooter_id)

            # 7. Obtener sesión actualizada
            updated_session = self.session_repo.get_by_id(self.db, session_id)

            return SessionFinalizationResult(
                session_id=session_id,
                finalized_successfully=True,
                total_exercises=consolidation_result["total_exercises"],
                consolidated_exercises=consolidation_result["consolidated_count"],
                failed_exercises=consolidation_result["failed_count"],
                final_stats=final_stats,
                consolidation_warnings=self._extract_warnings(consolidation_result),
                finalization_timestamp=updated_session.updated_at,
                evaluation_pending=updated_session.evaluation_pending,
                has_assigned_instructor=updated_session.instructor_id is not None,
                message=self._get_finalization_message(updated_session),
                # ✅ NUEVOS campos de puntuación en la respuesta
                total_session_score=getattr(updated_session, "total_session_score", 0),
                average_score_per_exercise=getattr(
                    updated_session, "average_score_per_exercise", 0.0
                ),
                best_shot_score=getattr(updated_session, "best_shot_score", 0),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error finalizando sesión {session_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error finalizando sesión: {str(e)}",
            )

    def validate_session_for_completion(
        self, session_id: UUID
    ) -> SessionValidationResult:
        try:
            session = self.session_repo.get_with_exercises(self.db, session_id)
            if not session:
                return SessionValidationResult(
                    can_finish=False,
                    reason="Sesión no encontrada",
                    missing_requirements=["session_exists"],
                )

            if session.is_finished:
                return SessionValidationResult(
                    can_finish=False,
                    reason="La sesión ya ha sido finalizada",
                    missing_requirements=[""],
                )
            # verificar que tenga al menos un ejericicio
            exercises = session.exercises
            if not exercises:
                return SessionValidationResult(
                    can_finish=False,
                    reason="La sesión no tiene ejercicios asociados",
                    missing_requirements=["min_one_exercise"],
                )
            # verificar que al menos un ejercicio tenga la imagen
            exercises_with_image = [ex for ex in exercises if ex.target_image_id]
            if not exercises_with_image:
                return SessionValidationResult(
                    can_finish=False,
                    reason="Ningún ejercicio tiene imagen de blanco",
                    missing_requirements=["min_one_image"],
                )

            # opcional: verificar qeu ejercicios con imagen tenga analisis
            missing_analysis = []
            for exercise in exercises_with_image:
                if exercise.target_image_id:
                    # verificar si tiene analisis usando el repo de analisis
                    from src.infraestructure.database.repositories.target_images_repo import (
                        TargetImagesRepository,
                    )

                    analysis_repo = TargetImagesRepository()
                    has_analysis = analysis_repo.has_analysis(
                        self.db, exercise.target_image_id
                    )

                    if not has_analysis:
                        missing_analysis.append(str(exercise.id))
            if missing_analysis:
                return SessionValidationResult(
                    can_finish=False,
                    reason="Algunos ejercicios tienen imagen sin análisis",
                    missing_requirements=["exercises_need_analysis"],
                    exercises_needing_analysis=missing_analysis,
                )

            # todo esta bien para finalizar
            return SessionValidationResult(
                can_finish=True,
                reason="La sesión está lista para finalizar",
                missing_requirements=[],
                exercises_count=len(exercises),
                exercises_with_image=len(exercises_with_image),
            )
        except Exception as e:
            return SessionValidationResult(
                can_finish=False,
                reason=f"Error validando sesión: {str(e)}",
                missing_requirements=["validation_error"],
            )

    def can_modify_session(self, session_id: UUID) -> bool:
        return self.session_repo.can_modify_session(self.db, session_id)

    def validate_session_for_modification(self, session_id: UUID) -> bool:
        """
        Verifica si la sesión puede ser modificada.
        """
        if not self.can_modify_session(session_id):
            raise HTTPException(
                status_code=403, detail="No puedes modificar esta sesión"
            )

    def get_session_status(self, session_id: UUID) -> Dict:
        """
        Obtiene el estado actual de la sesión.
        """
        try:
            session = self.session_repo.get_with_exercises(self.db, session_id)

            if not session:
                return {"error": "Sesión no encontrada"}

            validation = self.validate_session_for_completion(session_id)

            return {
                "session_id": str(session_id),
                "is_finished": session.is_finished,
                "evaluation_pending": session.evaluation_pending,
                "can_modify": not session.is_finished,
                "can_finish": validation.can_finish,
                "finish_requirements": validation.missing_requirements,
                "exercises_count": len(session.exercises),
                "exercises_with_images": len(
                    [ex for ex in session.exercises if ex.target_image_id]
                ),
                "total_shots": session.total_shots_fired,
                "total_hits": session.total_hits,
                "accuracy": session.accuracy_percentage,
                "total_session_score": getattr(session, "total_session_score", 0),
                "average_score_per_exercise": getattr(
                    session, "average_score_per_exercise", 0.0
                ),
                "average_score_per_shot": getattr(
                    session, "average_score_per_shot", 0.0
                ),
                "best_shot_score": getattr(session, "best_shot_score", 0),
                "validation_message": validation.reason,
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de sesión {session_id}: {e}")
            return {"error": str(e)}

    def reopen_session(self, session_id: UUID, shooter_id) -> Dict:
        """
        Re abre una sesion finalizada (solo si no tiene evaluacion)
        util para casos de emergencia
        """

        try:
            session = self.session_repo.get_by_id(self.db, session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Sesión no encontrada")
            if session.shooter_id != shooter_id:
                raise HTTPException(
                    status_code=403, detail="No tienes permiso para reabrir esta sesión"
                )
            if not session.is_finished:
                raise HTTPException(
                    status_code=400, detail="La sesión no está finalizada"
                )
            # Verificar que no tenga evaluación
            # TODO: Agregar verificación de evaluación cuando esté implementada
            # if session.evaluation:
            #     raise HTTPException(status_code=400, detail="No se puede reabrir una sesión evaluada")
            updated_session = self.session_repo.update_session(
                self.db, session_id, is_finished=False, evaluation_pending=False
            )

            return {
                "success": True,
                "message": "Sesión reabierta exitosamente",
                "session_id": str(updated_session.id),
                "can_modify": True,
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reabriendo la sesión [{session_id}]: {str(e)}",
            )

    def _extract_warnings(self, consolidation_result: Dict) -> list:
        """
        Extrae warnings importantes del resultado de consolidación
        """
        warnings = []

        if consolidation_result.get("failed_count", 0) > 0:
            warnings.append(
                f"{consolidation_result['failed_count']} ejercicios no pudieron consolidarse"
            )

        # Buscar warnings específicos en los resultados de ejercicios
        for exercise_result in consolidation_result.get("exercise_results", []):
            if not exercise_result.get("success") and exercise_result.get("reason"):
                warnings.append(
                    f"Ejercicio {exercise_result.get('exercise_id', 'unknown')}: {exercise_result['reason']}"
                )

        return warnings[:5]

    def _update_basic_shooter_stats(self, session_id: UUID, shooter_id: UUID):
        """
        Actualiza estadisticas basicas del tirador al finalizar sesion
        se ejecuta siempre, tenga o no instructor asignado
        """
        try:
            from src.application.services.shooter_stats import ShooterStatsService

            stats_service = ShooterStatsService(self.db)
            stats_service.update_basic_stats_after_session(
                session_id=session_id, shooter_id=shooter_id
            )

        except Exception as e:
            print(f"⚠️ Error actualizando stats del tirador: {str(e)}")

    def _get_finalization_message(self, session) -> str:
        if session.instructor_id:
            return "Sesión finalizada. La evaluación por parte del instructor está pendiente."
        else:
            return "Sesión finalizada y completada. No requiere evaluación."

    def _calculate_session_score_efficiency(self, session) -> float:
        """Calcula eficiencia de puntuación de la sesión"""
        if session.total_shots_fired == 0:
            return 0.0

        total_score = getattr(session, "total_session_score", 0)
        max_possible = session.total_shots_fired * 10  # 10 puntos máximo por disparo

        return (total_score / max_possible) * 100 if max_possible > 0 else 0.0

    def _update_shooter_stats_with_scoring(self, session_id: UUID, shooter_id: UUID):
        """✅ ACTUALIZADO: Incluye estadísticas de puntuación"""
        try:
            from src.application.services.shooter_stats import ShooterStatsService

            stats_service = ShooterStatsService(self.db)

            # ✅ NUEVO: Método que incluye puntuación
            stats_service.update_stats_with_scoring_after_session(
                session_id=session_id, shooter_id=shooter_id
            )

            logger.info(
                f"✅ Estadísticas con puntuación actualizadas para tirador {shooter_id}"
            )

        except Exception as e:
            logger.error(f"⚠️ Error actualizando stats con puntuación: {str(e)}")
            # Fallback al método básico si falla
            try:
                from src.application.services.shooter_stats import ShooterStatsService

                stats_service = ShooterStatsService(self.db)
                stats_service.update_basic_stats_after_session(
                    session_id=session_id, shooter_id=shooter_id
                )
            except Exception as fallback_error:
                logger.error(f"⚠️ Fallback también falló: {str(fallback_error)}")

    # ✅ NUEVO: Método para obtener resumen completo de puntuación
    def get_session_scoring_summary(self, session_id: UUID) -> Dict:
        """Obtiene resumen completo de puntuación de la sesión"""
        try:
            session = self.session_repo.get_with_exercises(self.db, session_id)
            if not session:
                return {"error": "Sesión no encontrada"}

            exercises_with_scoring = []
            total_exercises_with_scoring = 0

            for exercise in session.exercises:
                if hasattr(exercise, "total_score") and exercise.total_score > 0:
                    total_exercises_with_scoring += 1
                    exercises_with_scoring.append(
                        {
                            "exercise_id": str(exercise.id),
                            "exercise_type": (
                                exercise.exercise_type.name
                                if exercise.exercise_type
                                else "Unknown"
                            ),
                            "total_score": exercise.total_score,
                            "average_score_per_shot": exercise.average_score_per_shot,
                            "max_score_achieved": exercise.max_score_achieved,
                            "ammunition_used": exercise.ammunition_used,
                            "score_efficiency": (
                                (
                                    exercise.total_score
                                    / (exercise.ammunition_used * 10)
                                    * 100
                                )
                                if exercise.ammunition_used > 0
                                else 0.0
                            ),
                            "group_diameter": exercise.group_diameter,
                        }
                    )

            return {
                "session_id": str(session_id),
                "total_exercises": len(session.exercises),
                "exercises_with_scoring": total_exercises_with_scoring,
                "total_session_score": getattr(session, "total_session_score", 0),
                "average_score_per_exercise": getattr(
                    session, "average_score_per_exercise", 0.0
                ),
                "average_score_per_shot": getattr(
                    session, "average_score_per_shot", 0.0
                ),
                "best_shot_score": getattr(session, "best_shot_score", 0),
                "session_score_efficiency": self._calculate_session_score_efficiency(
                    session
                ),
                "exercises_details": exercises_with_scoring,
                "has_complete_scoring": total_exercises_with_scoring
                == len(session.exercises),
            }
        except Exception as e:
            logger.error(f"Error obteniendo resumen de puntuación: {str(e)}")
            return {"error": str(e)}
