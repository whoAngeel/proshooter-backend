from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import func, or_, and_, desc, case
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta

from src.infraestructure.database.models.user_model import UserModel

from src.domain.enums.role_enum import RoleEnum

from src.infraestructure.database.models.shooter_model import ShooterModel
from src.infraestructure.database.models.shooter_stats_model import ShooterStatsModel
from src.infraestructure.database.models.practice_session_model import (
    IndividualPracticeSessionModel,
)
from src.infraestructure.database.models.evaluation_model import PracticeEvaluationModel
from src.infraestructure.database.models.user_model import (
    UserModel,
    UserPersonalDataModel,
)
from src.infraestructure.database.models.shooting_club_model import ShootingClubModel
from src.domain.enums.classification_enum import ShooterLevelEnum


class ShooterRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[ShooterModel]:
        # Cargamos el tirador con sus relaciones principales para evitar múltiples consultas
        return (
            db.query(ShooterModel)
            .options(
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                joinedload(ShooterModel.stats),
                joinedload(ShooterModel.club),
            )
            .filter(ShooterModel.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ShooterModel]:
        return (
            db.query(ShooterModel)
            .options(
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                joinedload(ShooterModel.stats),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_club(
        db: Session, club_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[ShooterModel]:
        # Obtenemos los tiradores de un club específico
        return (
            db.query(ShooterModel)
            .options(
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                joinedload(ShooterModel.stats),
            )
            .filter(ShooterModel.club_id == club_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_level(
        db: Session, level: ShooterLevelEnum, skip: int = 0, limit: int = 100
    ) -> List[ShooterModel]:
        # Obtenemos los tiradores de un nivel específico
        return (
            db.query(ShooterModel)
            .options(
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                joinedload(ShooterModel.stats),
            )
            .filter(ShooterModel.level == level)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def search_by_name(
        db: Session, name: str, skip: int = 0, limit: int = 100
    ) -> List[ShooterModel]:
        # Buscamos tiradores por nombre (nombre o apellido)
        search_term = f"%{name}%"

        return (
            db.query(ShooterModel)
            .join(UserModel, ShooterModel.user_id == UserModel.id)
            .join(UserPersonalDataModel, UserModel.id == UserPersonalDataModel.user_id)
            .options(
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                joinedload(ShooterModel.stats),
            )
            .filter(
                or_(
                    UserPersonalDataModel.first_name.ilike(search_term),
                    UserPersonalDataModel.second_name.ilike(search_term),
                    UserPersonalDataModel.last_name1.ilike(search_term),
                    UserPersonalDataModel.last_name2.ilike(search_term),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_accuracy_range(
        db: Session,
        min_accuracy: float,
        max_accuracy: float,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ShooterModel]:
        # Buscamos tiradores por rango de precisión en sus estadísticas
        return (
            db.query(ShooterModel)
            .join(
                ShooterStatsModel, ShooterModel.user_id == ShooterStatsModel.shooter_id
            )
            .options(
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                joinedload(ShooterModel.stats),
            )
            .filter(ShooterStatsModel.accuracy.between(min_accuracy, max_accuracy))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def search_by_combined_criteria(
        db: Session, filter_params: dict, skip: int = 0, limit: int = 100
    ) -> List[ShooterModel]:
        # Método para búsqueda combinada con múltiples criterios
        query = db.query(ShooterModel).options(
            joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
            joinedload(ShooterModel.stats),
        )

        # Aplicamos los filtros según los parámetros proporcionados
        if filter_params.get("level"):
            query = query.filter(ShooterModel.level == filter_params["level"])

        if filter_params.get("club_id"):
            query = query.filter(ShooterModel.club_id == filter_params["club_id"])

        if filter_params.get("search"):
            search_term = f"%{filter_params['search']}%"
            query = (
                query.join(UserModel, ShooterModel.user_id == UserModel.id)
                .join(
                    UserPersonalDataModel, UserModel.id == UserPersonalDataModel.user_id
                )
                .filter(
                    or_(
                        UserPersonalDataModel.first_name.ilike(search_term),
                        UserPersonalDataModel.second_name.ilike(search_term),
                        UserPersonalDataModel.last_name1.ilike(search_term),
                        UserPersonalDataModel.last_name2.ilike(search_term),
                    )
                )
            )

        if (
            filter_params.get("min_accuracy") is not None
            and filter_params.get("max_accuracy") is not None
        ):
            query = query.join(
                ShooterStatsModel, ShooterModel.user_id == ShooterStatsModel.shooter_id
            ).filter(
                ShooterStatsModel.accuracy.between(
                    filter_params["min_accuracy"], filter_params["max_accuracy"]
                )
            )

        # Ordenar por nombre para tener un orden consistente
        query = (
            query.join(UserModel, ShooterModel.user_id == UserModel.id)
            .join(UserPersonalDataModel, UserModel.id == UserPersonalDataModel.user_id)
            .order_by(
                UserPersonalDataModel.last_name1, UserPersonalDataModel.first_name
            )
        )

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_criteria(db: Session, filter_params: dict) -> int:
        # Método para contar tiradores según criterios (para paginación)
        query = db.query(func.count(ShooterModel.user_id))

        # Replicamos la lógica de filtrado de search_by_combined_criteria
        if filter_params.get("level"):
            query = query.filter(ShooterModel.level == filter_params["level"])

        if filter_params.get("club_id"):
            query = query.filter(ShooterModel.club_id == filter_params["club_id"])

        if filter_params.get("search"):
            search_term = f"%{filter_params['search']}%"
            query = (
                query.join(UserModel, ShooterModel.user_id == UserModel.id)
                .join(
                    UserPersonalDataModel, UserModel.id == UserPersonalDataModel.user_id
                )
                .filter(
                    or_(
                        UserPersonalDataModel.first_name.ilike(search_term),
                        UserPersonalDataModel.second_name.ilike(search_term),
                        UserPersonalDataModel.last_name1.ilike(search_term),
                        UserPersonalDataModel.last_name2.ilike(search_term),
                    )
                )
            )

        if (
            filter_params.get("min_accuracy") is not None
            and filter_params.get("max_accuracy") is not None
        ):
            query = query.join(
                ShooterStatsModel, ShooterModel.user_id == ShooterStatsModel.shooter_id
            ).filter(
                ShooterStatsModel.accuracy.between(
                    filter_params["min_accuracy"], filter_params["max_accuracy"]
                )
            )

        return query.scalar()

    @staticmethod
    def update(
        db: Session, user_id: UUID, shooter_data: dict
    ) -> Optional[ShooterModel]:
        # Actualizamos los datos de un tirador
        shooter = db.query(ShooterModel).filter(ShooterModel.user_id == user_id).first()

        if not shooter:
            return None

        # Actualizamos solo los campos proporcionados
        for key, value in shooter_data.items():
            if hasattr(shooter, key):
                setattr(shooter, key, value)

        db.commit()
        db.refresh(shooter)

        return shooter

    @staticmethod
    def update_classification(
        db: Session, user_id: UUID, new_level: ShooterLevelEnum
    ) -> bool:
        # Método específico para actualizar la clasificación de un tirador
        shooter = db.query(ShooterModel).filter(ShooterModel.user_id == user_id).first()

        if not shooter:
            return False

        # Si el nivel es el mismo, no hacemos nada
        if shooter.level == new_level:
            return True

        # Actualizamos el nivel
        shooter.level = new_level

        # Aquí podríamos registrar el cambio en un historial si existiera esa tabla

        db.commit()

        return True

    @staticmethod
    def assign_to_club(db: Session, user_id: UUID, club_id: UUID) -> bool:
        # Método para asignar un tirador a un club
        shooter = db.query(ShooterModel).filter(ShooterModel.user_id == user_id).first()

        if not shooter:
            return False

        # Verificar que el club existe
        club = (
            db.query(ShootingClubModel).filter(ShootingClubModel.id == club_id).first()
        )

        if not club:
            return False

        # Asignar el tirador al club
        shooter.club_id = club_id
        db.commit()

        return True

    @staticmethod
    def get_performance_summary(db: Session, user_id: UUID) -> Dict[str, Any]:
        # Obtiene un resumen del rendimiento del tirador
        shooter = (
            db.query(ShooterModel)
            .options(
                joinedload(ShooterModel.stats),
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
            )
            .filter(ShooterModel.user_id == user_id)
            .first()
        )

        if not shooter:
            return {}

        # Contamos las sesiones del tirador
        session_count = (
            db.query(func.count(IndividualPracticeSessionModel.id))
            .filter(IndividualPracticeSessionModel.shooter_id == user_id)
            .scalar()
        )

        # Obtenemos las últimas evaluaciones
        recent_evaluations = (
            db.query(PracticeEvaluationModel)
            .join(
                IndividualPracticeSessionModel,
                PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id,
            )
            .filter(IndividualPracticeSessionModel.shooter_id == user_id)
            .order_by(desc(PracticeEvaluationModel.date))
            .limit(5)
            .all()
        )

        # Analizamos la tendencia reciente
        trend = "stable"
        if len(recent_evaluations) >= 3:
            first_score = recent_evaluations[-1].final_score
            last_score = recent_evaluations[0].final_score

            if last_score > first_score + 5:  # Mejora significativa
                trend = "improving"
            elif last_score < first_score - 5:  # Deterioro significativo
                trend = "declining"

        # Obtenemos fortalezas y debilidades (simplificado)
        strengths = []
        weaknesses = []

        if recent_evaluations:
            # Extraemos strengths y weaknesses del último comentario de evaluación
            latest_eval = recent_evaluations[0]
            if latest_eval.strengths:
                strengths = [s.strip() for s in latest_eval.strengths.split(",")]
            if latest_eval.weaknesses:
                weaknesses = [w.strip() for w in latest_eval.weaknesses.split(",")]

        # Construimos el resumen
        user_name = ""
        if shooter.user and shooter.user.personal_data:
            personal_data = shooter.user.personal_data
            user_name = f"{personal_data.first_name} {personal_data.last_name1}"

        return {
            "shooter_id": str(user_id),
            "user_name": user_name,
            "level": shooter.level.value if shooter.level else None,
            "total_sessions": session_count,
            "total_shots": shooter.stats.total_shots if shooter.stats else 0,
            "accuracy": shooter.stats.accuracy if shooter.stats else 0,
            "recent_trend": trend,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "evaluations_count": len(recent_evaluations),
            "last_evaluation_date": (
                recent_evaluations[0].date if recent_evaluations else None
            ),
        }

    @staticmethod
    def get_classification_history(db: Session, user_id: UUID) -> Dict[str, Any]:
        # Este método asumiría la existencia de una tabla de historial de clasificaciones
        # En ausencia de ella, proporcionamos una simulación basada en datos disponibles

        shooter = db.query(ShooterModel).filter(ShooterModel.user_id == user_id).first()

        if not shooter:
            return {}

        # Obtener evaluaciones ordenadas por fecha para simular historial
        evaluations = (
            db.query(PracticeEvaluationModel)
            .join(
                IndividualPracticeSessionModel,
                PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id,
            )
            .filter(IndividualPracticeSessionModel.shooter_id == user_id)
            .order_by(PracticeEvaluationModel.date)
            .all()
        )

        # Simulamos un historial basado en las evaluaciones
        classification_history = []
        current_level = None
        last_change_date = None

        for index, eval in enumerate(evaluations):
            if index == 0 or eval.classification != current_level:
                if current_level:  # Solo añadimos cambios, no el nivel inicial
                    classification_history.append(
                        {
                            "date": eval.date,
                            "from_level": current_level.value,
                            "to_level": eval.classification.value,
                            "evaluation_id": str(eval.id),
                        }
                    )

                current_level = eval.classification
                last_change_date = eval.date

        # Calculamos días en el nivel actual
        days_at_current_level = 0
        if last_change_date:
            days_at_current_level = (datetime.now() - last_change_date).days

        # Determinamos la tendencia de progresión
        progression_trend = "stable"
        if classification_history:
            initial_level = ShooterLevelEnum.REGULAR  # Nivel inicial por defecto
            latest_level = shooter.level

            # Definimos un mapeo numérico para comparar niveles
            level_values = {
                ShooterLevelEnum.REGULAR: 1,
                ShooterLevelEnum.MEDIUM: 2,
                ShooterLevelEnum.TRUSTWORTHY: 3,
                ShooterLevelEnum.EXPERT: 4,
            }

            if level_values[latest_level] > level_values[initial_level]:
                progression_trend = "ascending"
            elif level_values[latest_level] < level_values[initial_level]:
                progression_trend = "descending"

        return {
            "shooter_id": str(user_id),
            "classification_history": classification_history,
            "current_level": shooter.level.value,
            "days_at_current_level": days_at_current_level,
            "progression_trend": progression_trend,
        }

    @staticmethod
    def compare_shooters(
        db: Session, shooter1_id: UUID, shooter2_id: UUID
    ) -> Dict[str, Any]:
        # Método para comparar dos tiradores
        shooter1 = (
            db.query(ShooterModel)
            .options(
                joinedload(ShooterModel.stats),
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
            )
            .filter(ShooterModel.user_id == shooter1_id)
            .first()
        )

        shooter2 = (
            db.query(ShooterModel)
            .options(
                joinedload(ShooterModel.stats),
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
            )
            .filter(ShooterModel.user_id == shooter2_id)
            .first()
        )

        if not shooter1 or not shooter2:
            return {}

        # Obtener nombres
        shooter1_name = ""
        if shooter1.user and shooter1.user.personal_data:
            data = shooter1.user.personal_data
            shooter1_name = f"{data.first_name} {data.last_name1}"

        shooter2_name = ""
        if shooter2.user and shooter2.user.personal_data:
            data = shooter2.user.personal_data
            shooter2_name = f"{data.first_name} {data.last_name1}"

        # Calcular diferencias
        accuracy_diff = 0
        if shooter1.stats and shooter2.stats:
            accuracy_diff = shooter1.stats.accuracy - shooter2.stats.accuracy

        reaction_time_diff = 0
        if shooter1.stats and shooter2.stats:
            # Usamos reload_time_avg como aproximación
            reaction_time_diff = (
                shooter1.stats.reload_time_avg - shooter2.stats.reload_time_avg
            )

        # Comparamos fortalezas (simplificado, asumiendo algunos atributos)
        strengths_comparison = {}
        if shooter1.stats and shooter2.stats:
            stats1 = shooter1.stats
            stats2 = shooter2.stats

            strengths_comparison = {
                "accuracy": {
                    f"{shooter1_name}": stats1.accuracy,
                    f"{shooter2_name}": stats2.accuracy,
                    "difference": stats1.accuracy - stats2.accuracy,
                },
                "precision_shots": {
                    f"{shooter1_name}": stats1.presicion_shots,
                    f"{shooter2_name}": stats2.presicion_shots,
                    "difference": stats1.presicion_shots - stats2.presicion_shots,
                },
                "reaction_shots": {
                    f"{shooter1_name}": stats1.reaction_shots,
                    f"{shooter2_name}": stats2.reaction_shots,
                    "difference": stats1.reaction_shots - stats2.reaction_shots,
                },
                "effectiveness": {
                    f"{shooter1_name}": stats1.effectiveness,
                    f"{shooter2_name}": stats2.effectiveness,
                    "difference": stats1.effectiveness - stats2.effectiveness,
                },
            }

        # Generamos una recomendación simple
        recommendation = ""
        if accuracy_diff > 5:
            recommendation = f"{shooter2_name} podría mejorar su precisión estudiando la técnica de {shooter1_name}."
        elif accuracy_diff < -5:
            recommendation = f"{shooter1_name} podría mejorar su precisión estudiando la técnica de {shooter2_name}."
        else:
            recommendation = f"Ambos tiradores tienen niveles similares de precisión."

        return {
            "shooter1_id": str(shooter1_id),
            "shooter1_name": shooter1_name,
            "shooter1_level": shooter1.level.value,
            "shooter2_id": str(shooter2_id),
            "shooter2_name": shooter2_name,
            "shooter2_level": shooter2.level.value,
            "accuracy_difference": accuracy_diff,
            "reaction_time_difference": reaction_time_diff,
            "strengths_comparison": strengths_comparison,
            "recommendation": recommendation,
        }

    @staticmethod
    def get_top_shooters(
        db: Session, limit: int = 10, by_criteria: str = "accuracy"
    ) -> List[Dict[str, Any]]:
        # Método para obtener los mejores tiradores según un criterio
        query = (
            db.query(ShooterModel)
            .join(
                ShooterStatsModel, ShooterModel.user_id == ShooterStatsModel.shooter_id
            )
            .join(UserModel, ShooterModel.user_id == UserModel.id)
            .join(UserPersonalDataModel, UserModel.id == UserPersonalDataModel.user_id)
        )

        # Aplicamos orden según el criterio
        if by_criteria == "accuracy":
            query = query.order_by(desc(ShooterStatsModel.accuracy))
        elif by_criteria == "effectiveness":
            query = query.order_by(desc(ShooterStatsModel.effectiveness))
        elif by_criteria == "hit_factor":
            query = query.order_by(desc(ShooterStatsModel.average_hit_factor))

        shooters = query.limit(limit).all()

        # Preparamos la respuesta con datos relevantes
        result = []
        for shooter in shooters:
            name = ""
            if shooter.user and shooter.user.personal_data:
                data = shooter.user.personal_data
                name = f"{data.first_name} {data.last_name1}"

            value = 0
            if shooter.stats:
                if by_criteria == "accuracy":
                    value = shooter.stats.accuracy
                elif by_criteria == "effectiveness":
                    value = shooter.stats.effectiveness
                elif by_criteria == "hit_factor":
                    value = shooter.stats.average_hit_factor

            result.append(
                {
                    "shooter_id": str(shooter.user_id),
                    "name": name,
                    "level": shooter.level.value,
                    "value": value,
                    "criteria": by_criteria,
                }
            )

        return result

    @staticmethod
    def create(db: Session, user_id: UUID):
        shooter = ShooterModel(user_id=user_id)
        db.add(shooter)
        db.flush()
        # db.refresh(shooter)
        return shooter

    @staticmethod
    def create_shooter_stats(db: Session, shooter_id: UUID):
        shooter = ShooterRepository.get_by_user_id(db, shooter_id)
        if not shooter:
            return None

        new_shooter_stats = ShooterStatsModel(user_id=shooter_id)

        db.add(new_shooter_stats)
        db.commit()
        db.refresh(new_shooter_stats)
        return new_shooter_stats
