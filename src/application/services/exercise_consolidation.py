from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Dict, Tuple
from fastapi import HTTPException
import logging

from src.presentation.schemas.exercise_consolidation import (
    ExerciseConsolidationResult,
    AmmunitionValidationResult,
    ExerciseMetricsUpdate,
)

from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository,
)
from src.infraestructure.database.repositories.target_analysis_repo import (
    TargetAnalysisRepository,
)
from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository,
)

logger = logging.getLogger(__name__)


class ExerciseConsolidationService:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.exercise_repo = PracticeExerciseRepository()
        self.analysis_repo = TargetAnalysisRepository()
        self.session_repo = PracticeSessionRepository()

    def update_exercise_from_analysis(
        self, exercise_id: UUID
    ) -> ExerciseConsolidationResult:
        try:
            # Obtener ejercicio con sus relaciones
            exercise = self.exercise_repo.get_with_relations(
                self.db, exercise_id, ["target_image", "session"]
            )

            if not exercise:
                raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

            if not exercise.target_image_id:
                raise HTTPException(
                    status_code=400,
                    detail="El ejercicio no tiene imagen de blanco asociada",
                )

            # Obtener el análisis más reciente
            analysis = self.analysis_repo.get_by_image_id(
                self.db, exercise.target_image_id
            )

            if not analysis:
                raise HTTPException(
                    status_code=400,
                    detail="No se encontró análisis para la imagen del ejercicio",
                )

            # Validar consistencia de munición
            ammunition_validation = self.validate_ammunition_consistency(
                exercise, analysis
            )

            # ✅ NUEVO: Calcular métricas con puntuación
            exercise_updates = self.calculate_exercise_metrics_with_scoring(
                exercise, analysis, ammunition_validation
            )

            # Actualizar ejercicio en base de datos
            success = self.exercise_repo.update_metrics(
                self.db, exercise_id, exercise_updates.model_dump()
            )

            if not success:
                raise HTTPException(
                    status_code=500, detail="Error actualizando ejercicio"
                )

            # ✅ NUEVO: Recalcular totales de la sesión con puntuación
            self.session_repo.update_totals_with_scoring(self.db, exercise.session_id)

            return ExerciseConsolidationResult(
                exercise_id=exercise_id,
                updated_successfully=True,
                ammunition_used=exercise_updates.ammunition_used,
                hits=exercise_updates.hits,
                accuracy_percentage=exercise_updates.accuracy_percentage,
                # ✅ NUEVOS campos en el resultado
                total_score=exercise_updates.total_score,
                average_score_per_shot=exercise_updates.average_score_per_shot,
                ammunition_validation=ammunition_validation,
                total_impacts_detected=analysis.total_impacts_detected,
                message="Ejercicio actualizado exitosamente con puntuación",
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error actualizando ejercicio {exercise_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"❌ Error interno actualizando ejercicio: {str(e)}",
            )

    def validate_ammunition_consistency(
        self, exercise, analysis
    ) -> AmmunitionValidationResult:
        allocated = exercise.ammunition_allocated or 0
        currently_used = exercise.ammunition_used or 0
        detected_impacts = analysis.total_impacts_detected or 0

        if allocated == detected_impacts:
            recommended_used = detected_impacts
            status = "PERFECT_MATCH"
            warning = None
        elif allocated > detected_impacts:
            # mas municion asignada que impactos detectados - posibles fallos
            recommended_used = detected_impacts
            status = "POTENTIAL_MISSES"
            warning = f"Se asignaron {allocated} municiones, pero solo se detectaron {detected_impacts} impactos. Posibles fallos o impactos no visibles"
        elif allocated < detected_impacts:
            # menos municion asignada que impactos detectados -- error en asignacion
            recommended_used = allocated
            status = "ASSIGNMENT_ERROR"
            warning = f"Se detectaron {detected_impacts} impactos pero solo se asignaron {allocated} municiones. Revisar asignación de munición"
        else:
            # allocated == 0 (no asignado)
            recommended_used = detected_impacts
            status = "NO_ALLOCATION"
            warning = (
                "No hay munición asignada, usando impactos detectados como referencia"
            )

        return AmmunitionValidationResult(
            allocated=allocated,
            currently_used=currently_used,
            detected_impacts=detected_impacts,
            recommended_used=recommended_used,
            status=status,
            warning=warning,
            needs_manual_review=status in ["ASSIGNMENT_ERROR", "POTENTIAL_MISSES"]
            and abs(allocated - detected_impacts) > 2,
        )

    def calculate_exercise_metrics(
        self, exercise, analysis, ammunition_validation
    ) -> ExerciseMetricsUpdate:
        # usar la municion usada que el usuario asigno (no los impactos detectados)
        ammunition_used = exercise.ammunition_used or exercise.ammunition_allocated or 0
        # ammunition_used = ammunition_validation.recommended_used

        # calcular aciertos (impactos dentro del blanco)
        # hits_inside = (analysis.fresh_impacts_inside or 0) + (analysis.covered_impacts_inside or 0)
        hits_inside = analysis.fresh_impacts_inside or 0

        # calcular precision
        accuracy_percentage = (
            (hits_inside / ammunition_used * 100) if ammunition_used > 0 else 0.0
        )

        # mantener tiempo de reaccion si ya existe
        reaction_time = exercise.reaction_time if exercise.reaction_time else None

        return ExerciseMetricsUpdate(
            ammunition_used=ammunition_used,
            hits=hits_inside,
            accuracy_percentage=round(accuracy_percentage, 2),
            reaction_time=reaction_time,
            total_impacts_detected=analysis.total_impacts_detected,
            impacts_outside_target=(analysis.fresh_impacts_outside or 0),
            # + (analysis.covered_impacts_outside or 0),
        )

    def calculate_exercise_metrics_with_scoring(
        self, exercise, analysis, ammunition_validation
    ) -> ExerciseMetricsUpdate:
        """
        ✅ NUEVO: Calcula métricas del ejercicio incluyendo puntuación
        """
        # Cálculos existentes (sin cambios)
        ammunition_used = exercise.ammunition_used or exercise.ammunition_allocated or 0
        hits_inside = analysis.fresh_impacts_inside or 0
        accuracy_percentage = (
            (hits_inside / ammunition_used * 100) if ammunition_used > 0 else 0.0
        )
        reaction_time = exercise.reaction_time if exercise.reaction_time else None

        # ✅ NUEVOS: Cálculos de puntuación
        total_score = getattr(analysis, "total_score", 0)
        average_score_per_shot = getattr(analysis, "average_score_per_shot", 0.0)
        max_score_achieved = getattr(analysis, "max_score_achieved", 0)
        score_distribution = getattr(analysis, "score_distribution", {})
        group_diameter = getattr(analysis, "shooting_group_diameter", None)

        return ExerciseMetricsUpdate(
            # Campos existentes
            ammunition_used=ammunition_used,
            hits=hits_inside,
            accuracy_percentage=round(accuracy_percentage, 2),
            reaction_time=reaction_time,
            total_impacts_detected=analysis.total_impacts_detected,
            impacts_outside_target=(analysis.fresh_impacts_outside or 0),
            # ✅ NUEVOS campos de puntuación
            total_score=total_score,
            average_score_per_shot=round(average_score_per_shot, 2),
            max_score_achieved=max_score_achieved,
            score_distribution=score_distribution,
            group_diameter=group_diameter,
        )

    def get_exercise_consolidation_status(self, exercise_id: UUID) -> Dict:
        try:
            exercise = self.exercise_repo.get_with_relations(
                exercise_id, ["target_image"]
            )

            if not exercise:
                return {"error": "Ejercicio no encontrado"}

            analysis = None
            if exercise.target_image_id:
                analysis = self.analysis_repo.get_by_image_id(
                    self.db, exercise.target_image_id
                )
            return {
                "exercise_id": str(exercise_id),
                "has_image": exercise.target_image_id is not None,
                "has_analysis": analysis is not None,
                "ammunition_allocated": exercise.ammunition_allocated,
                "ammunition_used": exercise.ammunition_used,
                "hits": exercise.hits,
                "accuracy_percentage": exercise.accuracy_percentage,
                "analysis_detected_impacts": (
                    analysis.total_impacts_detected if analysis else None
                ),
                "needs_consolidation": self._needs_consolidation(exercise, analysis),
                "analysis_date": analysis.analysis_timestamp if analysis else None,
            }
        except Exception as e:
            logger.error(f"Error obteniendo estado de consolidación: {str(e)}")
            return {"error": f"Error interno: {str(e)}"}

    def consolidate_all_session_exercises(self, session_id: UUID) -> Dict:
        try:
            # Obtener todos los ejercicios de la sesión
            exercises = self.exercise_repo.get_by_session_id(
                self.db, session_id=session_id
            )

            logger.info(
                f"Consolidando {len(exercises)} ejercicios para la sesión {session_id}"
            )

            results = {
                "session_id": str(session_id),
                "total_exercises": len(exercises),
                "consolidated_count": 0,
                "failed_count": 0,
                "exercise_results": [],
                "session_totals": None,
            }

            for exercise in exercises:
                try:
                    if exercise.target_image_id:
                        result = self.update_exercise_from_analysis(exercise.id)
                        results["exercise_results"].append(
                            {
                                "exercise_id": str(exercise.id),
                                "success": True,
                                "ammunition_used": result.ammunition_used,
                                "hits": result.hits,
                                "accuracy": result.accuracy_percentage,
                            }
                        )
                        results["consolidated_count"] += 1
                    else:
                        results["exercise_results"].append(
                            {
                                "exercise_id": str(exercise.id),
                                "success": False,
                                "reason": "No tiene imagen de blanco",
                            }
                        )
                        results["failed_count"] += 1

                except Exception as e:
                    results["exercise_results"].append(
                        {
                            "exercise_id": str(exercise.id),
                            "success": False,
                            "reason": str(e),
                        }
                    )
                    results["failed_count"] += 1

            # Calcular totales de la sesión
            if results["consolidated_count"] > 0:
                results["session_totals"] = self.session_repo.calculate_totals(
                    self.db, session_id
                )

            return results

        except Exception as e:
            logger.error(
                f"Error consolidando ejercicios de sesión {session_id}: {str(e)}"
            )
            return {"session_id": str(session_id), "error": str(e)}

    def _needs_consolidation(self, exercise, analysis) -> bool:
        if not analysis:
            return False
        # verificar si los datos estan desactualizados
        if exercise.ammunition_used != analysis.total_impacts_detected:
            return True

        expected_hits = analysis.fresh_impacts_inside or 0
        if exercise.hits != expected_hits:
            return True

        return False
