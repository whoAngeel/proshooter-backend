from sqlalchemy.orm import Session
from uuid import UUID
from src.infraestructure.database.repositories.shooter_stats_repo import (
    ShooterStatsRepository,
)
from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository,
)
from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository,
)

from src.presentation.schemas.user_stats_schema import ShooterStatsUpdate
from typing import Dict


class ShooterStatsService:
    def __init__(self, db: Session):
        self.db = db
        self.stats_repo = ShooterStatsRepository()
        self.session_repo = PracticeSessionRepository()
        self.exercise_repo = PracticeExerciseRepository()

    def update_basic_stats_after_session(self, session_id: UUID, shooter_id: UUID):
        """
        Actualiza estadisticas basicas del tirador despues de finalizar sesion.
        Se ejecuta siempore, indempendientemente de si tiene instructor o no
        """

        try:
            stats = self.stats_repo.get_by_shooter_id(self.db, shooter_id)
            if not stats:
                stats = self.stats_repo.create(self.db, shooter_id)
                if not stats:
                    return False
            # obtener sesion finalizada
            session = self.session_repo.get_by_id(self.db, session_id)
            if not session or not session.is_finished:
                return False

            # obtener ejercicios de la sesion para analisis por tipo
            exercises = self.exercise_repo.get_by_session_id(session_id)

            # calcular nuevos valores
            updates = {}

            # total de disparos
            updates["total_shots"] = stats.total_shots + session.total_shots_fired

            # 2. Contadores por tipo de ejercicio
            precision_shots, reaction_shots = self._count_shots_by_type(exercises)
            updates["presicion_shots"] = stats.presicion_shots + precision_shots
            updates["reaction_shots"] = stats.reaction_shots + reaction_shots

            # 3. Recalcular precisión general (promedio de todas las sesiones)
            updates["accuracy"] = self._calculate_overall_accuracy(shooter_id)

            # 4. Promedio de últimas 10 sesiones
            updates["last_10_sessions_avg"] = self._calculate_last_10_sessions_avg(
                shooter_id
            )

            # 5. Actualizar en BD
            self.stats_repo.update(self.db, shooter_id, updates)

            return True
        except Exception as e:
            print(f"❌ Error al actualizar estadísticas básicas: {str(e)}")
            return False

    def _count_shots_by_type(self, exercises) -> tuple:
        """
        Cuenta disparos por tipo de ejercicio basado en el nombre del tipo
        """
        precision_shots = 0
        reaction_shots = 0

        for exercise in exercises:
            if exercise.exercise_type and exercise.ammunition_used:
                exercise_name = exercise.exercise_type.name.lower()
                exercise_description = (
                    exercise.exercise_type.description.lower()
                    if exercise.exercise_type.description
                    else ""
                )

                # Clasificar por nombre del ejercicio (ajustar según tus tipos)
                if (
                    "precision" in exercise_name
                    or "precis" in exercise_name
                    or "precis" in exercise_description
                    or "precision" in exercise_description
                ):
                    precision_shots += exercise.ammunition_used
                elif (
                    "reacci" in exercise_name
                    or "reaction" in exercise_name
                    or "react" in exercise_description
                    or "reacci" in exercise_description
                ):
                    reaction_shots += exercise.ammunition_used
                # Los que no coincidan no se cuentan en categorías específicas

        return precision_shots, reaction_shots

    def _calculate_overall_accuracy(self, shooter_id: UUID) -> int:
        """
        Calcula la precisión general del tirador como un porcentaje
        """
        try:
            finished_sessions = self.session_repo.get_finished_sessions_by_shooter(
                self.db, shooter_id
            )
            # TODO: Despues de 100 sesiones hay que revisar esto
            if not finished_sessions:
                return 0

            # calcular promedio ponderado por disparo
            total_shots = sum(s.total_shots_fired for s in finished_sessions)
            total_hits = sum(s.total_hits for s in finished_sessions)

            if total_shots > 0:
                return int((total_hits / total_shots) * 100)

            return 0
        except Exception as e:
            print(f"❌ Error al calcular precisión general: {str(e)}")
            return 0

    def _calculate_last_10_sessions_avg(self, shooter_id: UUID) -> float:
        try:
            recent_sessions = self.session_repo.get_finished_sessions_by_shooter(
                shooter_id, limit=10
            )

            if not recent_sessions:
                return 0.0

            # Promedio simple de accuracy_percentage
            total_accuracy = sum(s.accuracy_percentage for s in recent_sessions)
            return round(total_accuracy / len(recent_sessions), 2)

        except Exception as e:
            print(f"❌ Error al calcular promedio de últimas 10 sesiones: {str(e)}")
            return 0.0

    def get_shooter_basic_stats(self, shooter_id: UUID) -> Dict:
        """
        Obtiene estadísticas básicas para mostrar en dashboard
        """
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
            print(f"Error obteniendo estadísticas: {str(e)}")
            return {"error": str(e)}
