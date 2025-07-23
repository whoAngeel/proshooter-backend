from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Optional, List
from fastapi import HTTPException
from datetime import datetime
from fastapi import Depends


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
            # verificar que la sesion existe y pertenece al tirador
            session = self.session_repo.get_by_id(db=self.db, session_id=session_id)

            if not session:
                raise HTTPException(
                    status_code=404, detail="Sesión de entrenamiento no encontrada"
                )

            if session.shooter_id != shooter_id:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes permiso para finalizar esta sesión",
                )

            if session.is_finished:
                raise HTTPException(
                    status_code=400, detail="La sesión ya ha sido finalizada"
                )

            # 2 validar que la sesion este lista para finalizar
            validation = self.validate_session_for_completion(session_id)
            if not validation.can_finish:
                raise HTTPException(status_code=400, detail=validation.reason)

            # 3 consolidar todos los ejercicios una ultima vez
            consolidation_result = (
                self.consolidation_service.consolidate_all_session_exercises(
                    session_id=session_id
                )
            )

            # 4 calcular estadisticas finales de la sesion
            final_stats = self.session_repo.calculate_totals(self.db, session_id)

            if final_stats.get("error"):
                raise HTTPException(
                    status_code=500,
                    detail=f"Error calculando totales de la sesión: {final_stats['error']}",
                )

            # 5 finalizar la sesion
            success = self.session_repo.finish_session(self.db, session_id)

            if not success:
                raise HTTPException(
                    status_code=500, detail="Error finalizando la sesión"
                )

            # 6 obtener sesion actualizada
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
                message="Sesión finalizada exitosamente. Lista para evaluación.",
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error finalizando la sesión [{session_id}]: {str(e)}",
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
                "validation_message": validation.reason,
            }

        except Exception as e:
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
