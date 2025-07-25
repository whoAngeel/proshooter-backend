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
from src.infraestructure.database.repositories.target_analysis_repo import (
    TargetAnalysisRepository,
)
from src.presentation.schemas.user_stats_schema import ShooterStatsUpdate
from typing import Dict


class ShooterStatsService:
    def __init__(self, db: Session):
        self.db = db
        self.stats_repo = ShooterStatsRepository()
        self.session_repo = PracticeSessionRepository()
        self.exercise_repo = PracticeExerciseRepository()
        self.analysis_repo = TargetAnalysisRepository()

    def update_basic_stats_after_session(self, session_id: UUID, shooter_id: UUID):
        """
        Actualiza estadísticas completas del tirador después de finalizar sesión
        Ahora calcula TODOS los campos del modelo
        """
        try:
            # Obtener o crear estadísticas del tirador
            stats = self.stats_repo.get_by_shooter_id(self.db, shooter_id)
            if not stats:
                stats = self.stats_repo.create(self.db, shooter_id)
                if not stats:
                    return False

            # Obtener sesión y ejercicios
            session = self.session_repo.get_by_id(session_id)
            if not session or not session.is_finished:
                return False

            exercises = self.exercise_repo.get_by_session_id(session_id)

            # Calcular todas las estadísticas
            updates = {}

            # 1. ESTADÍSTICAS BÁSICAS
            updates.update(self._calculate_basic_stats(stats, session, exercises))

            # 2. ESTADÍSTICAS POR TIPO DE EJERCICIO
            updates.update(self._calculate_exercise_type_stats(shooter_id, exercises))

            # 3. TIEMPOS PROMEDIO
            updates.update(self._calculate_average_times(stats, exercises))

            # 4. MÉTRICAS AVANZADAS
            updates.update(
                self._calculate_advanced_metrics(shooter_id, session, exercises)
            )

            # 5. TENDENCIAS Y PROMEDIOS
            updates.update(self._calculate_trends_and_averages(shooter_id))

            # 6. ZONAS DE ERROR COMUNES
            updates.update(self._calculate_common_error_zones(exercises))

            # 7. Actualizar en BD
            self.stats_repo.update(self.db, shooter_id, updates)

            return True

        except Exception as e:
            print(f"Error actualizando estadísticas completas: {str(e)}")
            return False

    def _calculate_basic_stats(self, stats, session, exercises) -> Dict:
        """
        Estadísticas básicas: disparos totales, precisión general, contadores
        """
        # Total de disparos (sumar ammunition_used real, no allocated)
        session_shots = sum(ex.ammunition_used or 0 for ex in exercises)

        # Contadores por tipo de ejercicio
        precision_shots, reaction_shots = self._count_shots_by_type(exercises)

        return {
            "total_shots": stats.total_shots + session_shots,
            "presicion_shots": stats.presicion_shots + precision_shots,
            "reaction_shots": stats.reaction_shots + reaction_shots,
            "accuracy": self._calculate_overall_accuracy_from_exercises(
                exercises, stats
            ),
        }

    def _calculate_exercise_type_stats(
        self, shooter_id: UUID, current_exercises
    ) -> Dict:
        """
        Precisión específica por tipo de ejercicio
        """
        # Obtener TODOS los ejercicios históricos del tirador por tipo
        all_sessions = self.session_repo.get_finished_sessions_by_shooter(
            shooter_id, limit=50
        )
        all_exercises = []

        for session in all_sessions:
            session_exercises = self.exercise_repo.get_by_session_id(session.id)
            all_exercises.extend(session_exercises)

        # Clasificar ejercicios por tipo
        precision_exercises = []
        reaction_exercises = []
        movement_exercises = []

        for ex in all_exercises:
            if ex.exercise_type and ex.ammunition_used and ex.ammunition_used > 0:
                exercise_name = ex.exercise_type.name.lower()

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
        """
        Tiempos promedio de desenfunde y recarga
        """
        # Obtener tiempos de reacción de los ejercicios actuales
        reaction_times = [
            ex.reaction_time
            for ex in exercises
            if ex.reaction_time and ex.reaction_time > 0
        ]

        if reaction_times:
            # Promedio móvil simple con tiempos existentes
            current_avg = stats.draw_time_avg or 0
            new_avg = sum(reaction_times) / len(reaction_times)

            if current_avg == 0:
                draw_time_avg = new_avg
            else:
                # Promedio ponderado (70% histórico, 30% nuevo)
                draw_time_avg = (current_avg * 0.7) + (new_avg * 0.3)
        else:
            draw_time_avg = stats.draw_time_avg

        return {
            "draw_time_avg": round(draw_time_avg, 3),
            "reload_time_avg": stats.reload_time_avg,  # Por ahora mantener el actual
        }

    def _calculate_advanced_metrics(self, shooter_id: UUID, session, exercises) -> Dict:
        """
        Métricas avanzadas: hit_factor, effectiveness
        """
        # Hit Factor = Impactos / Tiempo (métrica usada en IPSC)
        total_hits = sum(ex.hits or 0 for ex in exercises)
        total_time = sum(ex.reaction_time or 1 for ex in exercises if ex.reaction_time)

        if total_time > 0:
            hit_factor = total_hits / total_time
        else:
            hit_factor = 0

        # Effectiveness = (Disparos efectivos / Disparos totales) * Factor de precisión
        total_shots = sum(ex.ammunition_used or 0 for ex in exercises)
        if total_shots > 0:
            effectiveness = (total_hits / total_shots) * (
                session.accuracy_percentage / 100
            )
        else:
            effectiveness = 0

        return {
            "average_hit_factor": round(hit_factor, 3),
            "effectiveness": round(effectiveness, 3),
        }

    def _calculate_trends_and_averages(self, shooter_id: UUID) -> Dict:
        """
        Tendencias y promedios de últimas sesiones
        """
        recent_sessions = self.session_repo.get_finished_sessions_by_shooter(
            shooter_id, limit=10
        )

        if len(recent_sessions) < 2:
            return {
                "last_10_sessions_avg": (
                    recent_sessions[0].accuracy_percentage if recent_sessions else 0.0
                ),
                "trend_accuracy": 0.0,
            }
        # Promedio de últimas 10 sesiones
        avg_10_sessions = sum(s.accuracy_percentage for s in recent_sessions) / len(
            recent_sessions
        )

        # Tendencia: comparar últimas 5 vs anteriores 5
        if len(recent_sessions) >= 6:
            last_5 = recent_sessions[:5]
            previous_5 = recent_sessions[5:10]

            avg_last_5 = sum(s.accuracy_percentage for s in last_5) / len(last_5)
            avg_prev_5 = sum(s.accuracy_percentage for s in previous_5) / len(
                previous_5
            )

            trend = avg_last_5 - avg_prev_5  # Positivo = mejorando
        else:
            trend = 0.0

        return {
            "last_10_sessions_avg": round(avg_10_sessions, 2),
            "trend_accuracy": round(trend, 2),
        }

    def _calculate_common_error_zones(self, exercises) -> Dict:
        """
        Analiza patrones de error comunes desde los análisis de imagen
        """
        error_zones = []

        for exercise in exercises:
            if exercise.target_image_id:
                # Obtener análisis de la imagen
                analysis = self.analysis_repo.get_latest_by_image_id(
                    exercise.target_image_id
                )

                if analysis and analysis.impact_coordinates:
                    # Analizar coordenadas de impactos fuera del blanco
                    impacts_outside = [
                        impact
                        for impact in analysis.impact_coordinates
                        if not impact.get("dentro_blanco", True)
                    ]

                    # Clasificar zonas de error (simplificado)
                    for impact in impacts_outside:
                        x, y = impact.get("x", 0), impact.get("y", 0)
                        zone = self._classify_error_zone(x, y)
                        if zone:
                            error_zones.append(zone)

        # Encontrar las zonas más comunes
        if error_zones:
            from collections import Counter

            most_common = Counter(error_zones).most_common(3)
            common_zones = [zone for zone, count in most_common]
            return {"common_error_zones": ", ".join(common_zones)}

        return {"common_error_zones": None}

    def _count_shots_by_type(self, exercises) -> tuple:
        """
        Cuenta disparos por tipo usando ammunition_used (no allocated)
        """
        precision_shots = 0
        reaction_shots = 0

        for exercise in exercises:
            if exercise.exercise_type and exercise.ammunition_used:
                exercise_name = exercise.exercise_type.name.lower()

                if any(
                    word in exercise_name
                    for word in ["precision", "precis", "precisión"]
                ):
                    precision_shots += exercise.ammunition_used
                elif any(
                    word in exercise_name
                    for word in ["reaccion", "reaction", "reacción"]
                ):
                    reaction_shots += exercise.ammunition_used

        return precision_shots, reaction_shots

    def _calculate_overall_accuracy_from_exercises(self, exercises, stats) -> int:
        """
        Calcula precisión general basada en ammunition_used vs hits reales
        """
        session_shots = sum(ex.ammunition_used or 0 for ex in exercises)
        session_hits = sum(ex.hits or 0 for ex in exercises)

        # Combinar con estadísticas históricas
        total_shots = stats.total_shots + session_shots

        if total_shots > 0:
            # Estimar hits históricos desde accuracy actual
            historical_hits = (stats.total_shots * stats.accuracy) // 100
            total_hits = historical_hits + session_hits

            return int((total_hits / total_shots) * 100)

        return stats.accuracy

    def _calculate_type_accuracy(self, exercises_of_type) -> float:
        """
        Calcula precisión promedio para un tipo específico de ejercicio
        """
        if not exercises_of_type:
            return 0.0

        total_shots = sum(ex.ammunition_used or 0 for ex in exercises_of_type)
        total_hits = sum(ex.hits or 0 for ex in exercises_of_type)

        if total_shots > 0:
            return round((total_hits / total_shots) * 100, 2)

        return 0.0

    def _count_shots_by_type(self, exercises) -> tuple:
        """
        Cuenta disparos por tipo de ejercicio basado en el nombre del tipo
        """
        precision_shots = 0
        reaction_shots = 0

        for exercise in exercises:
            if exercise.exercise_type and exercise.ammunition_used:
                exercise_type = exercise.exercise_type.type.lower()

                # Clasificar por nombre del ejercicio (ajustar según tus tipos)
                if exercise_type == "precision":
                    precision_shots += exercise.ammunition_used
                elif exercise_type == "movement":
                    reaction_shots += exercise.ammunition_used
                # Los que no coincidan no se cuentan en categorías específicas

        return precision_shots, reaction_shots

    def get_complete_shooter_stats(self, shooter_id: UUID) -> Dict:
        """
        Obtiene estadísticas completas para dashboard
        """
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
                "exercise_type_accuracy": {
                    "precision": stats.precision_exercise_accuracy,
                    "reaction": stats.reaction_exercise_accuracy,
                    "movement": stats.movement_exercise_accuracy,
                },
                "error_analysis": {"common_error_zones": stats.common_error_zones},
            }

        except Exception as e:
            return {"error": str(e)}

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
