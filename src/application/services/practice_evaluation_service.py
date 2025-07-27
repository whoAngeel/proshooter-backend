from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime
import math
import logging

from src.infraestructure.database.repositories.practice_evaluation_repo import (
    PracticeEvaluationRepository,
)
from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository,
)
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.infraestructure.database.repositories.shooter_stats_repo import (
    ShooterStatsRepository,
)
from src.infraestructure.database.repositories.user_repo import UserRepository
from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository,
)
from src.infraestructure.database.repositories.target_analysis_repo import (
    TargetAnalysisRepository,
)
from src.infraestructure.database.models.evaluation_model import PracticeEvaluationModel
from src.application.services.shooter_stats import ShooterStatsService
from src.infraestructure.database.session import get_db
from src.domain.enums.classification_enum import ShooterLevelEnum
from src.domain.enums.role_enum import RoleEnum
from src.presentation.schemas.practice_evaluation_schema import (
    EvaluationEditRequest,
    EvaluationCreateRequest,
    EvaluationFormData,
)

logger = logging.getLogger(__name__)


class PracticeEvaluationService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.evaluation_repo = PracticeEvaluationRepository
        self.session_repo = PracticeSessionRepository
        self.exercise_repo = PracticeExerciseRepository
        self.analysis_repo = TargetAnalysisRepository
        self.stats_service = ShooterStatsService(self.db)

    def get_evaluation_by_id(
        self, evaluation_id: UUID
    ) -> Optional[PracticeEvaluationModel]:
        """Obtiene una evaluación por su ID"""
        return self.evaluation_repo.get_by_id(self.db, evaluation_id)

    def get_by_evaluator(
        self, evaluator_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeEvaluationModel]:
        """Obtiene evaluaciones por ID de evaluador"""
        return self.evaluation_repo.get_by_evaluator(self.db, evaluator_id, skip, limit)

    def create_evaluation(
        self,
        session_id: UUID,
        instructor_id: UUID,
        evaluation_data: EvaluationCreateRequest,
    ) -> Dict:
        try:
            # validar permisos y estado de la sesion
            self._validate_evaluation_creation(session_id, instructor_id)

            # calcular campos automaticos
            auto_calculated = self.calculate_automatic_fields(session_id)

            # sugerir zonas de problema desde analisis ia
            suggested_zones = self.suggest_issue_zones(session_id)

            # combinar datos automaticos y manuales
            evaluation_dict = {
                "session_id": session_id,
                "evaluator_id": instructor_id,
                "date": datetime.now(),
                "classification": self._determinate_classification(
                    auto_calculated["final_score"]
                ),
                # Campos automáticos
                "final_score": auto_calculated["final_score"],
                "avg_reaction_time": auto_calculated["avg_reaction_time"],
                "avg_draw_time": auto_calculated["avg_draw_time"],
                "hit_factor": auto_calculated["hit_factor"],
                # Campos manuales del instructor
                "strengths": evaluation_data.strengths,
                "weaknesses": evaluation_data.weaknesses,
                "recomendations": evaluation_data.recomendations,
                "overall_technique_rating": evaluation_data.overall_technique_rating,
                "instructor_notes": evaluation_data.instructor_notes,
                # Zonas de problema (sugeridas por IA, editables por instructor)
                "primary_issue_zone": evaluation_data.primary_issue_zone
                or suggested_zones.get("primary"),
                "secondary_issue_zone": evaluation_data.secondary_issue_zone
                or suggested_zones.get("secondary"),
            }

            # crear evaluacion en bd
            evaluation = self.evaluation_repo.create(self.db, evaluation_dict)

            # actualizar estadisticas avanzadas del tirador
            self._update_advanced_shooter_stats(session_id, evaluation.id)

            return {
                "success": True,
                "evaluation_id": str(evaluation.id),
                "final_score": evaluation.final_score,
                "classification": self._determinate_classification(
                    evaluation.final_score
                ),
                "message": "Evaluación creada exitosamente",
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"❌Error creating evaluation: {e}")
            raise HTTPException(status_code=500, detail="Error al crear la evaluación")

    def calculate_automatic_fields(self, session_id: UUID) -> Dict:
        """calcula datos automaticos basados en los datos de la sesion

        Args:
            session_id (UUID): _description_

        Returns:
            Dict: _description_
        """
        try:
            session = self.session_repo.get_with_exercises(self.db, session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Sesión no encontrada")
            exercises = session.exercises

            # 1 final score basado en la precision + factores adicionales
            base_score = session.accuracy_percentage or 0.0

            # bonificaciones por volumen y consistencia
            if session.total_shots_fired >= 50:
                base_score += 5.0
            elif session.total_shots_fired >= 30:
                base_score += 2.0

            # penalizaacion por gran disparidad entre ejercicios
            if exercises:
                accuracies = [
                    ex.accuracy_percentage for ex in exercises if ex.accuracy_percentage
                ]
                if accuracies and len(accuracies) > 1:
                    accuracy_variance = max(accuracies) - min(accuracies)
                    if accuracy_variance > 30:  # mas de 30% de diferencia
                        base_score -= 5.0

            final_score = min(max(base_score, 0.0), 100.0)  # entre 0 y 100

            # tiempos
            reaction_times = [
                ex.reaction_time
                for ex in exercises
                if ex.reaction_time and ex.reaction_time > 0
            ]
            avg_reaction_time = (
                sum(reaction_times) / len(reaction_times) if reaction_times else None
            )

            # 3. Hit Factor (Hits/Tiempo) - métrica IPSC
            total_hits = session.total_hits or 0
            total_time = sum(reaction_times) if reaction_times else 0
            hit_factor = total_hits / total_time if total_time > 0 else None

            return {
                "final_score": round(final_score, 2),
                "avg_reaction_time": (
                    round(avg_reaction_time, 3) if avg_reaction_time else None
                ),
                "avg_draw_time": (
                    round(avg_reaction_time, 3) if avg_reaction_time else None
                ),  # Por ahora igual
                "hit_factor": round(hit_factor, 3) if hit_factor else None,
            }

        except Exception as e:
            # Valores por defecto si falla el cálculo
            return {
                "final_score": 0.0,
                "avg_reaction_time": None,
                "avg_draw_time": None,
                "hit_factor": None,
            }

    def suggest_issue_zones(self, session_id: UUID) -> Dict:
        """
        sugiere zonas problematicas basadas en analisis de IA de las imagenes
        """

        try:
            exercises = self.exercise_repo.get_by_session_id(self.db, session_id)

            zone_counts = {}

            for exercise in exercises:
                if exercise.target_image_id:
                    analysis = self.analysis_repo.get_by_image_id(
                        self.db, exercise.target_image_id
                    )

                    if analysis and analysis.impact_coordinates:
                        # analizar impactos fuera del blanco
                        impacts_outside = [
                            impact
                            for impact in analysis.impact_coordinates
                            if not impact.get("dentro_blanco", True)
                        ]
                        for impact in impacts_outside:
                            zone = self._classify_impact_zone(
                                impact.get("x", 0), impact.get("y", 0)
                            )
                            if zone:
                                zone_counts[zone] = zone_counts.get(zone, 0) + 1
            # obtener las 2 zonas mas problematicas
            if zone_counts:
                sorted_zones = sorted(
                    zone_counts.items(), key=lambda x: x[1], reverse=True
                )
                return {
                    "primary": sorted_zones[0][0] if len(sorted_zones) > 0 else None,
                    "secondary": sorted_zones[1][0] if len(sorted_zones) > 1 else None,
                }
            return {"primary": None, "secondary": None}
        except Exception as e:
            logger.error(f"❌Error sugiriendo zonas de problema: {e}")
            return {"primary": None, "secondary": None}

    def get_evaluation_form_data(
        self, session_id: UUID, instructor_id: UUID
    ) -> EvaluationFormData:
        """
        Obtiene datos para pre-llenar el formulario de evaluación
        """
        try:
            # Validar permisos
            self._validate_evaluation_creation(session_id, instructor_id)

            # Calcular campos automáticos
            auto_calculated = self.calculate_automatic_fields(session_id)

            # Sugerir zonas de problema
            suggested_zones = self.suggest_issue_zones(session_id)

            # Obtener contexto del tirador
            session = self.session_repo.get_with_exercises(self.db, session_id)
            shooter_context = self._get_shooter_context(session.shooter_id)

            return EvaluationFormData(
                session_id=session_id,
                auto_calculated=auto_calculated,
                suggested_zones=suggested_zones,
                shooter_context=shooter_context,
                classification_suggestion=self._determinate_classification(
                    auto_calculated["final_score"]
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌Error obteniendo datos del formulario: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error obteniendo datos del formulario: {str(e)}",
            )

    def _validate_evaluation_creation(self, session_id: UUID, instructor_id: UUID):
        """
        Valida que se pueda crear la evaluación
        """
        # Verificar que la sesión existe
        session = self.session_repo.get_by_id(self.db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")

        # Verificar que está asignada al instructor
        if session.instructor_id != instructor_id:
            raise HTTPException(
                status_code=403, detail="Sesión no asignada a este instructor"
            )

        # Verificar que está finalizada
        if not session.is_finished:
            raise HTTPException(
                status_code=400, detail="La sesión debe estar finalizada"
            )

        # Verificar que no tiene evaluación previa
        existing_evaluation = self.evaluation_repo.get_by_session_id(
            self.db, session_id
        )
        if existing_evaluation:
            raise HTTPException(status_code=400, detail="La sesión ya tiene evaluación")

    def _update_advanced_shooter_stats(self, session_id: UUID, evaluation_id: UUID):
        """
        Actualiza estadísticas avanzadas del tirador después de evaluación
        """
        try:
            session = self.session_repo.get_by_id(self.db, session_id)
            if session:
                # Llamar al servicio de estadísticas para actualización post-evaluación
                # TODO
                self.stats_service.update_advanced_stats_after_evaluation(
                    session.shooter_id, evaluation_id
                )
        except Exception as e:
            # Log error pero no fallar la evaluación por esto
            print(f"⚠️ Error actualizando estadísticas avanzadas: {str(e)}")

    def _determinate_classification(self, final_score: float) -> str:
        """
        Determina la clasificación del tirador basado en el puntaje final
        """
        if final_score >= 90:
            return ShooterLevelEnum.EXPERTO.name
        elif final_score >= 75:
            return ShooterLevelEnum.CONFIABLE.name
        elif final_score >= 50:
            return ShooterLevelEnum.MEDIO.name
        else:
            return ShooterLevelEnum.REGULAR.name

    def _classify_impact_zone(self, x: float, y: float) -> Optional[str]:
        """
        Clasifica la zona del impacto basado en coordenadas
        """
        # Definir zonas basadas en coordenadas (ejemplo simplificado)
        # Asumimos un blanco de 100x100 con centro en (50, 50)
        # Simplificado - puedes hacer más complejo según tus blancos
        if abs(x) > abs(y):
            if x > 0:
                return "Lateral Derecho"
            else:
                return "Lateral Izquierdo"
        else:
            if y > 0:
                return "Superior"
            else:
                return "Inferior"

    def _get_shooter_context(self, shooter_id: UUID) -> Dict:
        """
        Obtiene contexto del tirador para la evaluación
        """
        try:
            # Obtener estadísticas actuales
            stats = self.stats_service.get_complete_shooter_stats(shooter_id)

            # Obtener evaluaciones recientes
            recent_evaluations = self.evaluation_repo.get_shooter_evaluation_history(
                self.db, shooter_id, limit=3
            )

            return {
                "current_stats": stats,
                "recent_evaluations_count": len(recent_evaluations),
                "last_classification": (
                    recent_evaluations[0].classification if recent_evaluations else None
                ),
                "improvement_trend": len(recent_evaluations) >= 2,
            }
        except Exception as e:
            logger.error(f"❌Error obteniendo contexto del tirador: {e}")
            return {"current_stats": {}, "recent_evaluations_count": 0}

    def update_evaluation(
        self, evaluation_id: UUID, update_data: EvaluationEditRequest
    ) -> Optional["PracticeEvaluationModel"]:
        """Actualiza una evaluación existente"""
        # Convierte el esquema a dict y filtra campos no nulos
        update_dict = {
            k: v for k, v in update_data.model_dump().items() if v is not None
        }
        return self.evaluation_repo.update(self.db, evaluation_id, update_dict)

    def delete_evaluation(self, evaluation_id: UUID) -> bool:
        """Elimina una evaluación existente"""
        return self.evaluation_repo.delete(self.db, evaluation_id)

    def get_shooter_full_name(self, shooter_id: UUID) -> str:
        """
        Devuelve el nombre completo del tirador dado su ID.
        """
        try:
            from src.infraestructure.database.repositories.user_repo import (
                UserRepository,
            )

            user = UserRepository.get_by_id(self.db, shooter_id)
            if user and user.personal_data:
                first_name = user.personal_data.first_name or ""
                second_name = user.personal_data.second_name or ""
                last_name1 = user.personal_data.last_name1 or ""
                last_name2 = user.personal_data.last_name2 or ""
                full_name = (
                    f"{first_name} {second_name} {last_name1} {last_name2}".strip()
                )
                return " ".join(full_name.split())
            return user.email if user else "Desconocido"
        except Exception:
            return "Desconocido"

    def get_classification_value(self, classification_key: str) -> str:
        """
        Convierte la clave corta de clasificación al valor largo.
        Ejemplo: 'MEDIO' -> 'Tirador Medio'
        """
        try:
            return ShooterLevelEnum[classification_key].value
        except Exception:
            return classification_key  # fallback si no existe

    def get_by_session_id(self, session_id: UUID) -> Optional[PracticeEvaluationModel]:
        """Obtiene una evaluación por ID de sesión"""
        return self.evaluation_repo.get_by_session_id(self.db, session_id)
