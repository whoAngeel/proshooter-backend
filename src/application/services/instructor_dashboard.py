from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from uuid import UUID
from typing import List, Optional, Dict
from fastapi import HTTPException, Depends
from datetime import datetime
import logging
from src.infraestructure.database.session import get_db
from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository,
)
from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository,
)
from src.infraestructure.database.repositories.target_analysis_repo import (
    TargetAnalysisRepository,
)
from src.infraestructure.database.repositories.instructor import InstructorRepository

from src.presentation.schemas.instructor_dashboard import (
    AssignedSessionSummary,
    SessionForEvaluationDetails,
    InstructorDashboardStats,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstructorDashboardService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.session_repo = PracticeSessionRepository()
        self.exercise_repo = PracticeExerciseRepository()
        self.analysis_repo = TargetAnalysisRepository()
        self.instructor_repo = InstructorRepository

    def get_assigned_sessions(
        self, instructor_id: UUID, include_evaluated: bool = False
    ) -> List[AssignedSessionSummary]:
        """
        Obtiene las sesiones asignadas a un instructor, filtrando por si han sido evaluadas o no.
        """
        if not InstructorRepository.validate_instructor_permission(
            self.db, instructor_id
        ):
            raise HTTPException(
                status_code=403, detail="Usuario no es instructor válido."
            )

        sessions = self.session_repo.get_sessions_by_instructor(
            self.db, instructor_id=instructor_id, only_pending=not include_evaluated
        )

        session_summaries = []
        for session in sessions:
            summary = AssignedSessionSummary(
                session_id=session.id,
                shooter_id=session.shooter_id,
                shooter_name=self._get_shooter_name(session.shooter_id),
                date=session.date,
                location=session.location,
                total_shots=session.total_shots_fired,
                total_hits=session.total_hits,
                accuracy_percentage=session.accuracy_percentage,
                exercises_count=(
                    len(session.exercises) if hasattr(session, "exercises") else 0
                ),
                evaluation_pending=session.evaluation_pending,
                days_pending=self._calculate_days_pending(session.date),
            )
            session_summaries.append(summary)

        session_summaries.sort(key=lambda x: x.days_pending, reverse=True)

        return session_summaries

    def get_session_details_for_evaluation(
        self, session_id: UUID, instructor_id: UUID
    ) -> SessionForEvaluationDetails:
        """
        Obtiene detalles completos de una sesión para evaluación
        """
        # Verificar que la sesión esté asignada a este instructor
        session = self.session_repo.get_with_exercises(self.db, session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")

        if session.instructor_id != instructor_id:
            raise HTTPException(
                status_code=403, detail="Sesión no asignada a este instructor"
            )

        if not session.is_finished:
            raise HTTPException(status_code=400, detail="Sesión no finalizada")

        # Obtener ejercicios con análisis
        exercises_details = []
        for exercise in session.exercises:
            exercise_detail = {
                "exercise_id": exercise.id,
                "exercise_type": (
                    exercise.exercise_type.name
                    if exercise.exercise_type
                    else "Sin tipo"
                ),
                "distance": exercise.distance,
                "ammunition_allocated": exercise.ammunition_allocated,
                "ammunition_used": exercise.ammunition_used,
                "hits": exercise.hits,
                "accuracy_percentage": exercise.accuracy_percentage,
                "reaction_time": exercise.reaction_time,
                "has_target_image": exercise.target_image_id is not None,
                "target_image_path": (
                    exercise.target_image.file_path if exercise.target_image else None
                ),
                "analysis_data": None,
            }

            # Agregar datos del análisis si existe
            if exercise.target_image_id:
                analysis = self.analysis_repo.get_by_image_id(
                    self.db, exercise.target_image_id
                )
                if analysis:
                    exercise_detail["analysis_data"] = {
                        "total_impacts": analysis.total_impacts_detected,
                        "fresh_impacts_inside": analysis.fresh_impacts_inside,
                        "fresh_impacts_outside": analysis.fresh_impacts_outside,
                        "accuracy_from_analysis": analysis.accuracy_percentage,
                        "impact_coordinates": analysis.impact_coordinates,
                    }

            exercises_details.append(exercise_detail)

        # Obtener información del tirador
        shooter_info = self._get_shooter_info(session.shooter_id)

        return SessionForEvaluationDetails(
            session_id=session.id,
            shooter_info=shooter_info,
            date=session.date,
            location=session.location,
            total_shots_fired=session.total_shots_fired,
            total_hits=session.total_hits,
            accuracy_percentage=session.accuracy_percentage,
            exercises=exercises_details,
            evaluation_pending=session.evaluation_pending,
            can_evaluate=session.evaluation_pending and session.is_finished,
        )

    def get_instructor_dashboard_stats(
        self, instructor_id: UUID
    ) -> InstructorDashboardStats:
        """Obtiene estadísticas del dashboard del instructor."""
        # sessiones pendientes
        pending_sessions = self.session_repo.get_sessions_by_instructor(
            self.db, instructor_id=instructor_id, only_pending=True
        )

        # sesiones evaluadas (ultimos 30 dias)
        all_assigned = self.session_repo.get_sessions_by_instructor(
            self.db, instructor_id, only_pending=False
        )
        evaluated_sessions = [s for s in all_assigned if not s.evaluation_pending]

        # estadisticas
        pending_count = len(pending_sessions)
        evaluated_count = len(evaluated_sessions)

        # sesiones mas urgentes (mas de 7 dias)
        urgent_sessions = [
            s for s in pending_sessions if self._calculate_days_pending(s.date) > 7
        ]

        # promedio dde precision de sesiones evaluadas
        avg_accuracy = 0.0
        if evaluated_sessions:
            avg_accuracy = sum(s.accuracy_percentage for s in evaluated_sessions) / len(
                evaluated_sessions
            )

        return InstructorDashboardStats(
            pending_evaluations=pending_count,
            evaluated_this_month=evaluated_count,
            urgent_evaluations=len(urgent_sessions),
            average_session_accuracy=round(avg_accuracy, 2),
            total_assigned_sessions=len(all_assigned),
        )

    def search_assigned_sessions(
        self, instructor_id: UUID, filters: Dict
    ) -> List[AssignedSessionSummary]:
        """
        Busca sesiones asignadas con filtros"""

        # base: Sesiones asignadas al instructor
        sessions = self.session_repo.get_sessions_by_instructor(
            self.db, instructor_id, only_pending=False
        )

        # aplicar filtros
        filtered_sessions = sessions

        # filtro por estado de evaluacion
        if filters.get("evaluation_status"):
            if filters["evaluation_status"] == "pending":
                filtered_sessions = [
                    s for s in filtered_sessions if s.evaluation_pending
                ]
            elif filters["evaluation_status"] == "evaluated":
                filtered_sessions = [
                    s for s in filtered_sessions if not s.evaluation_pending
                ]
        # filtro para rango de fechas
        date_from = filters.get("date_from")
        date_to = filters.get("date_to")

        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                return None

        from_date = parse_date(date_from) if date_from else None
        # Si no viene date_to, usa la fecha actual
        to_date = parse_date(date_to) if date_to else datetime.now().date()

        if from_date or to_date:
            filtered_sessions = [
                s
                for s in filtered_sessions
                if (
                    (from_date is None or s.date.date() >= from_date)
                    and (to_date is None or s.date.date() <= to_date)
                )
            ]

        # filtro por precision minima
        if filters.get("min_accuracy"):
            min_acc = float(filters["min_accuracy"])
            filtered_sessions = [
                s for s in filtered_sessions if s.accuracy_percentage >= min_acc
            ]

        # convertir a esquema
        return [self._session_to_summary(s) for s in filtered_sessions]

    def _get_shooter_name(self, shooter_id: UUID) -> str:
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
                return f"{first_name} {second_name} {last_name1} {last_name2}".strip()
            return user.email if user else "Desconocido"
        except Exception as e:
            logger.error(
                f"❌ Error obteniendo nombre del tirador {shooter_id}: {str(e)}"
            )
            return "Desconocido"

    def _get_shooter_info(self, shooter_id: UUID) -> Dict:
        try:
            from src.infraestructure.database.repositories.user_repo import (
                UserRepository,
            )
            from src.infraestructure.database.repositories.shooter_repo import (
                ShooterRepository,
            )

            user = UserRepository.get_by_id(self.db, shooter_id)
            shooter = ShooterRepository.get_by_id(self.db, shooter_id)

            if not user:
                return {"name": "Desconocido", "level": "REGULAR", "nickname": None}

            # obtener estadisticas recientes para contexto
            recent_sessions = self.session_repo.get_finished_sessions_by_shooter(
                self.db, shooter_id, limit=5
            )
            recent_avg = 0.0
            if recent_sessions:
                recent_avg = sum(s.accuracy_percentage for s in recent_sessions) / len(
                    recent_sessions
                )

            return {
                "name": self._get_shooter_name(shooter_id),
                "email": user.email,
                "level": (
                    shooter.level.value if shooter and shooter.level else "REGULAR"
                ),
                "nickname": shooter.nickname if shooter else None,
                "recent_average_accuracy": round(recent_avg, 2),
                "total_sessions_finished": len(recent_sessions),
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo info del tirador {shooter_id}: {str(e)}")
            return {"name": "Desconocido", "level": "REGULAR", "nickname": None}

    def _calculate_days_pending(self, session_date) -> int:
        try:
            from datetime import datetime

            if isinstance(session_date, str):
                session_date = datetime.fromisoformat(
                    session_date.replace("Z", "+00:00")
                )
            delta = datetime.now() - session_date.replace(tzinfo=None)
            return delta.days
        except Exception as e:
            logger.error(f"❌ Error calculando días pendientes: {str(e)}")
            return 0

    def _session_to_summary(self, session) -> AssignedSessionSummary:
        """
        Convierte sesión a resumen para listado
        """
        return AssignedSessionSummary(
            session_id=session.id,
            shooter_id=session.shooter_id,
            shooter_name=self._get_shooter_name(session.shooter_id),
            date=session.date,
            location=session.location,
            total_shots=session.total_shots_fired,
            total_hits=session.total_hits,
            accuracy_percentage=session.accuracy_percentage,
            exercises_count=(
                len(session.exercises) if hasattr(session, "exercises") else 0
            ),
            evaluation_pending=session.evaluation_pending,
            days_pending=self._calculate_days_pending(session.date),
        )
