from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
import math

from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.infraestructure.database.repositories.shooting_club_repo import (
    ShootingClubRepository,
)
from src.infraestructure.database.repositories.user_repo import UserRepository
from src.infraestructure.database.repositories.shooter_stats_repo import (
    ShooterStatsRepository,
)
from src.infraestructure.database.session import get_db
from src.domain.enums.classification_enum import ShooterLevelEnum
from src.presentation.schemas.shooter_schema import (
    ShooterCreate,
    ShooterRead,
    ShooterDetail,
    ShooterUpdate,
    ShooterList,
    ShooterFilter,
    ShooterClassificationHistory,
    ShooterPerformanceSummary,
    ShooterComparisonResult,
)


from src.presentation.schemas.shooter_schema import ShooterCreate


class ShooterService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def is_nickname_available(self, nickname: str) -> bool:
        """
        Verifica si el nickname está disponible (no existe en la base de datos).
        """
        if not nickname:
            return False
        shooter = ShooterRepository.get_by_nickname(self.db, nickname)
        return shooter is None

    def get_shooter_by_id(
        self, user_id: UUID
    ) -> Tuple[Optional[ShooterDetail], Optional[str]]:
        try:
            # Obtener el tirador con sus relaciones
            shooter = ShooterRepository.get_by_id(self.db, user_id)
            if not shooter:
                return None, "SHOOTER_NOT_FOUND"

            # Obtener datos adicionales para el detalle
            performance_summary = ShooterRepository.get_performance_summary(
                self.db, user_id
            )

            # Crear el objeto de detalle combinando datos del shooter y performance
            shooter_dict = ShooterRead.model_validate(shooter).model_dump()

            # Añadir información adicional del resumen de rendimiento
            shooter_dict["session_count"] = performance_summary.get("total_sessions", 0)
            shooter_dict["evaluation_count"] = performance_summary.get(
                "evaluations_count", 0
            )
            shooter_dict["recent_progress"] = performance_summary.get(
                "recent_trend", "stable"
            )

            # Añadir nombre del club si existe
            if shooter.club:
                shooter_dict["club_name"] = shooter.club.name

            # Crear y devolver el objeto de detalle
            shooter_detail = ShooterDetail(**shooter_dict)
            return shooter_detail, None
        except Exception as e:
            return None, f"ERROR_GETTING_SHOOTER: {str(e)}"

    def get_all_shooters(self, filter_params: ShooterFilter) -> ShooterList:
        try:
            # Convertir los parámetros de filtro a un diccionario
            filter_dict = filter_params.model_dump(exclude_unset=True)

            # Obtener los tiradores filtrados
            shooters = ShooterRepository.search_by_combined_criteria(
                self.db, filter_dict, filter_params.skip, filter_params.limit
            )

            # Obtener el conteo total para la paginación
            total_count = ShooterRepository.count_by_criteria(self.db, filter_dict)

            # Calcular información de paginación
            page = (filter_params.skip // filter_params.limit) + 1
            pages = (
                math.ceil(total_count / filter_params.limit) if total_count > 0 else 1
            )

            # Convertir los modelos a esquemas
            items = [ShooterRead.model_validate(shooter) for shooter in shooters]

            return ShooterList(
                items=items,
                total=total_count,
                page=page,
                size=filter_params.limit,
                pages=pages,
            )
        except Exception as e:
            # En caso de error, devolver una lista vacía
            return ShooterList(
                items=[], total=0, page=1, size=filter_params.limit, pages=1
            )

    def update_shooter(
        self, user_id: UUID, shooter_data: ShooterUpdate
    ) -> Tuple[Optional[ShooterRead], Optional[str]]:
        try:
            # Verificar que el tirador existe
            existing_shooter = ShooterRepository.get_by_id(self.db, user_id)
            if not existing_shooter:
                return None, "SHOOTER_NOT_FOUND"

            # Verificar que el club existe si se proporciona
            if shooter_data.club_id:
                club = ShootingClubRepository.get_by_id(self.db, shooter_data.club_id)
                if not club:
                    return None, "CLUB_NOT_FOUND"

            # Validar nickname único si se actualiza
            if shooter_data.nickname:
                shooter_with_nick = ShooterRepository.get_by_nickname(
                    self.db, shooter_data.nickname
                )
                if shooter_with_nick and shooter_with_nick.user_id != user_id:
                    return None, "NICKNAME_ALREADY_EXISTS"

            # Convertir los datos a diccionario para actualizar
            shooter_dict = shooter_data.model_dump(
                exclude_unset=True, exclude_none=True
            )

            # Actualizar el tirador
            updated_shooter = ShooterRepository.update(self.db, user_id, shooter_dict)

            if not updated_shooter:
                return None, "ERROR_UPDATING_SHOOTER"

            return ShooterRead.model_validate(updated_shooter), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPDATING_SHOOTER: {str(e)}"

    def update_shooter_classification(
        self, user_id: UUID, new_level: ShooterLevelEnum
    ) -> Tuple[bool, Optional[str]]:
        try:
            # Verificar que el tirador existe
            existing_shooter = ShooterRepository.get_by_id(self.db, user_id)
            if not existing_shooter:
                return False, "SHOOTER_NOT_FOUND"

            # Verificar que el nivel es válido
            if new_level not in ShooterLevelEnum:
                return False, "INVALID_CLASSIFICATION_LEVEL"

            # Actualizar la clasificación
            success = ShooterRepository.update_classification(
                self.db, user_id, new_level
            )

            if not success:
                return False, "ERROR_UPDATING_CLASSIFICATION"

            # Registrar el cambio de clasificación (esto podría incluir más lógica)
            self._log_classification_change(user_id, existing_shooter.level, new_level)

            return True, None
        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_UPDATING_CLASSIFICATION: {str(e)}"

    def assign_shooter_to_club(
        self, user_id: UUID, club_id: UUID
    ) -> Tuple[bool, Optional[str]]:
        try:
            # Verificar que el tirador existe
            shooter = ShooterRepository.get_by_id(self.db, user_id)
            if not shooter:
                return False, "SHOOTER_NOT_FOUND"

            # Verificar que el club existe
            club = ShootingClubRepository.get_by_id(self.db, club_id)
            if not club:
                return False, "CLUB_NOT_FOUND"

            # Asignar el tirador al club
            success = ShooterRepository.assign_to_club(self.db, user_id, club_id)

            if not success:
                return False, "ERROR_ASSIGNING_TO_CLUB"

            return True, None
        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_ASSIGNING_TO_CLUB: {str(e)}"

    def get_shooter_performance(
        self, user_id: UUID
    ) -> Tuple[Optional[ShooterPerformanceSummary], Optional[str]]:
        try:
            # Verificar que el tirador existe
            shooter = ShooterRepository.get_by_id(self.db, user_id)
            if not shooter:
                return None, "SHOOTER_NOT_FOUND"

            # Obtener el resumen de rendimiento
            performance_data = ShooterRepository.get_performance_summary(
                self.db, user_id
            )

            if not performance_data:
                return None, "ERROR_GETTING_PERFORMANCE_DATA"

            # Convertir a esquema
            return (
                ShooterPerformanceSummary(
                    shooter_id=UUID(performance_data["shooter_id"]),
                    user_name=performance_data["user_name"],
                    level=(
                        ShooterLevelEnum[performance_data["level"]]
                        if performance_data["level"]
                        else ShooterLevelEnum.REGULAR
                    ),
                    total_sessions=performance_data["total_sessions"],
                    total_shots=performance_data["total_shots"],
                    accuracy=performance_data["accuracy"],
                    recent_trend=performance_data["recent_trend"],
                    strengths=performance_data["strengths"],
                    weaknesses=performance_data["weaknesses"],
                    recommended_exercises=self._get_recommended_exercises(
                        performance_data
                    ),
                    recent_evaluations=[],  # Simplificado, se podría expandir
                ),
                None,
            )
        except Exception as e:
            return None, f"ERROR_GETTING_PERFORMANCE: {str(e)}"

    def get_classification_history(
        self, user_id: UUID
    ) -> Tuple[Optional[ShooterClassificationHistory], Optional[str]]:
        try:
            # Verificar que el tirador existe
            shooter = ShooterRepository.get_by_id(self.db, user_id)
            if not shooter:
                return None, "SHOOTER_NOT_FOUND"

            # Obtener el historial de clasificaciones
            history_data = ShooterRepository.get_classification_history(
                self.db, user_id
            )

            if not history_data:
                return None, "ERROR_GETTING_CLASSIFICATION_HISTORY"

            # Convertir a esquema
            return (
                ShooterClassificationHistory(
                    shooter_id=UUID(history_data["shooter_id"]),
                    classifications=history_data["classification_history"],
                    current_level=ShooterLevelEnum[history_data["current_level"]],
                    days_at_current_level=history_data["days_at_current_level"],
                    progression_trend=history_data["progression_trend"],
                ),
                None,
            )
        except Exception as e:
            return None, f"ERROR_GETTING_CLASSIFICATION_HISTORY: {str(e)}"

    def compare_shooters(
        self, shooter1_id: UUID, shooter2_id: UUID
    ) -> Tuple[Optional[ShooterComparisonResult], Optional[str]]:
        try:
            # Verificar que ambos tiradores existen
            shooter1 = ShooterRepository.get_by_id(self.db, shooter1_id)
            if not shooter1:
                return None, f"SHOOTER_NOT_FOUND: {shooter1_id}"

            shooter2 = ShooterRepository.get_by_id(self.db, shooter2_id)
            if not shooter2:
                return None, f"SHOOTER_NOT_FOUND: {shooter2_id}"

            # Obtener los datos de comparación
            comparison_data = ShooterRepository.compare_shooters(
                self.db, shooter1_id, shooter2_id
            )

            if not comparison_data:
                return None, "ERROR_COMPARING_SHOOTERS"

            # Convertir a esquema
            return (
                ShooterComparisonResult(
                    shooter1_id=UUID(comparison_data["shooter1_id"]),
                    shooter1_name=comparison_data["shooter1_name"],
                    shooter1_level=ShooterLevelEnum[comparison_data["shooter1_level"]],
                    shooter2_id=UUID(comparison_data["shooter2_id"]),
                    shooter2_name=comparison_data["shooter2_name"],
                    shooter2_level=ShooterLevelEnum[comparison_data["shooter2_level"]],
                    accuracy_difference=comparison_data["accuracy_difference"],
                    reaction_time_difference=comparison_data[
                        "reaction_time_difference"
                    ],
                    strengths_comparison=comparison_data["strengths_comparison"],
                    recommendation=comparison_data["recommendation"],
                ),
                None,
            )
        except Exception as e:
            return None, f"ERROR_COMPARING_SHOOTERS: {str(e)}"

    def get_top_shooters(
        self, limit: int = 10, criteria: str = "accuracy"
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        try:
            # Validar el criterio
            valid_criteria = ["accuracy", "effectiveness", "hit_factor"]
            if criteria not in valid_criteria:
                return (
                    [],
                    f"INVALID_CRITERIA: Must be one of {', '.join(valid_criteria)}",
                )

            # Obtener los mejores tiradores
            top_shooters = ShooterRepository.get_top_shooters(self.db, limit, criteria)

            return top_shooters, None
        except Exception as e:
            return [], f"ERROR_GETTING_TOP_SHOOTERS: {str(e)}"

    def _log_classification_change(
        self, user_id: UUID, old_level: ShooterLevelEnum, new_level: ShooterLevelEnum
    ) -> None:
        """
        Método auxiliar para registrar cambios de clasificación.
        En una implementación real, esto podría escribir en una tabla de historial.
        """
        # Esta es una implementación simplificada
        print(
            f"Cambio de clasificación: Usuario {user_id} cambió de {old_level.value} a {new_level.value}"
        )
        # Aquí se podría implementar lógica para registrar el cambio en una tabla de historial
        pass

    def _get_recommended_exercises(self, performance_data: Dict[str, Any]) -> List[str]:
        """
        Método auxiliar para generar recomendaciones de ejercicios basadas en el rendimiento.
        """
        recommendations = []

        # Simplificado: recomendaciones basadas en precisión
        accuracy = performance_data.get("accuracy", 0)
        if accuracy < 40:
            recommendations.append("Ejercicios de precisión a corta distancia")
            recommendations.append("Práctica de postura y agarre básicos")
        elif accuracy < 70:
            recommendations.append("Ejercicios de precisión a media distancia")
            recommendations.append("Práctica de control de respiración")
        else:
            recommendations.append("Ejercicios de precisión a larga distancia")
            recommendations.append("Práctica de tiro rápido manteniendo precisión")

        # Añadir recomendaciones basadas en debilidades identificadas
        weaknesses = performance_data.get("weaknesses", [])
        for weakness in weaknesses:
            if "postura" in weakness.lower():
                recommendations.append("Ejercicios específicos de postura")
            elif "agarre" in weakness.lower():
                recommendations.append(
                    "Ejercicios de fortalecimiento y estabilidad de agarre"
                )
            elif "gatillo" in weakness.lower() or "disparador" in weakness.lower():
                recommendations.append("Práctica de presión progresiva del disparador")
            elif "visual" in weakness.lower() or "mira" in weakness.lower():
                recommendations.append(
                    "Ejercicios de alineación visual y enfoque en la mira"
                )

        return recommendations[:3]  # Limitamos a 3 recomendaciones para no sobrecargar
