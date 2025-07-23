from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, between, desc, select, update
from datetime import datetime, timedelta, timezone
from logging import getLogger
from src.infraestructure.database.models.practice_exercise_model import (
    PracticeExerciseModel,
)
from src.infraestructure.database.models.practice_session_model import (
    IndividualPracticeSessionModel,
)
from src.infraestructure.database.models.exercise_type_model import ExerciseTypeModel
from src.infraestructure.database.models.target_model import TargetModel
from src.infraestructure.database.models.weapon_model import WeaponModel
from src.infraestructure.database.models.ammunition_model import AmmunitionModel
from src.infraestructure.database.models.target_analysis_model import (
    TargetAnalysisModel,
)
from src.infraestructure.database.models.target_image_model import TargetImageModel


logger = getLogger(__name__)


class PracticeExerciseRepository:
    @staticmethod
    def create(db: Session, exercise_data: dict) -> PracticeExerciseModel:
        # calculamos el porcentaje de precision si hay disparos
        if (
            exercise_data.get("ammunition_used", 0) > 0
            and "accuracy_percentage" not in exercise_data
        ):
            exercise_data["accuracy_percentage"] = (
                exercise_data.get("hits", 0) / exercise_data["ammunition_used"]
            ) * 100

        exercise = PracticeExerciseModel(**exercise_data)
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        return exercise

    @staticmethod
    def get_by_id(db: Session, exercise_id: UUID) -> Optional[PracticeExerciseModel]:
        return (
            db.query(PracticeExerciseModel)
            .options(
                joinedload(PracticeExerciseModel.exercise_type),
                joinedload(PracticeExerciseModel.target),
                joinedload(PracticeExerciseModel.weapon),
                joinedload(PracticeExerciseModel.ammunition),
                joinedload(PracticeExerciseModel.session),
                joinedload(PracticeExerciseModel.target_image).joinedload(
                    TargetImageModel.analyses
                ),
            )
            .filter(PracticeExerciseModel.id == exercise_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[PracticeExerciseModel]:
        return (
            db.query(PracticeExerciseModel)
            .options(
                joinedload(PracticeExerciseModel.exercise_type),
                joinedload(PracticeExerciseModel.session),
            )
            .order_by(desc(PracticeExerciseModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_session(db: Session, session_id: UUID) -> List[PracticeExerciseModel]:
        return (
            db.query(PracticeExerciseModel)
            .options(
                joinedload(PracticeExerciseModel.exercise_type),
                joinedload(PracticeExerciseModel.target),
                joinedload(PracticeExerciseModel.weapon),
                joinedload(PracticeExerciseModel.ammunition),
            )
            .filter(PracticeExerciseModel.session_id == session_id)
            .order_by(PracticeExerciseModel.created_at)
            .all()
        )

    @staticmethod
    def get_by_shooter(
        db: Session, shooter_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeExerciseModel]:
        return (
            db.query(PracticeExerciseModel)
            .join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            )
            .options(
                joinedload(PracticeExerciseModel.exercise_type),
                joinedload(PracticeExerciseModel.session),
            )
            .filter(IndividualPracticeSessionModel.shooter_id == shooter_id)
            .order_by(desc(IndividualPracticeSessionModel.date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_exercise_type(
        db: Session, exercise_type_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeExerciseModel]:
        return (
            db.query(PracticeExerciseModel)
            .options(joinedload(PracticeExerciseModel.session))
            .filter(PracticeExerciseModel.exercise_type_id == exercise_type_id)
            .order_by(desc(PracticeExerciseModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_weapon(
        db: Session, weapon_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeExerciseModel]:
        return (
            db.query(PracticeExerciseModel)
            .options(
                joinedload(PracticeExerciseModel.session),
                joinedload(PracticeExerciseModel.exercise_type),
            )
            .filter(PracticeExerciseModel.weapon_id == weapon_id)
            .order_by(desc(PracticeExerciseModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_ammunition(
        db: Session, ammunition_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeExerciseModel]:
        return (
            db.query(PracticeExerciseModel)
            .options(
                joinedload(PracticeExerciseModel.session),
                joinedload(PracticeExerciseModel.exercise_type),
            )
            .filter(PracticeExerciseModel.ammunition_id == ammunition_id)
            .order_by(desc(PracticeExerciseModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_target(
        db: Session, target_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeExerciseModel]:
        return (
            db.query(PracticeExerciseModel)
            .options(
                joinedload(PracticeExerciseModel.session),
                joinedload(PracticeExerciseModel.exercise_type),
            )
            .filter(PracticeExerciseModel.target_id == target_id)
            .order_by(desc(PracticeExerciseModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_distance(
        db: Session, distance: str, skip: int = 0, limit: int = 100
    ) -> List[PracticeExerciseModel]:
        return (
            db.query(PracticeExerciseModel)
            .options(
                joinedload(PracticeExerciseModel.session),
                joinedload(PracticeExerciseModel.exercise_type),
            )
            .filter(PracticeExerciseModel.distance == distance)
            .order_by(desc(PracticeExerciseModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def search_by_combined_criteria(
        db: Session, filter_params: dict, skip: int = 0, limit: int = 100
    ) -> List[PracticeExerciseModel]:
        query = db.query(PracticeExerciseModel).options(
            joinedload(PracticeExerciseModel.exercise_type),
            joinedload(PracticeExerciseModel.session),
        )

        # aplicamos cada filtro si esta presente
        if filter_params.get("session_id"):
            query = query.filter(
                PracticeExerciseModel.session_id == filter_params["session_id"]
            )

        if filter_params.get("shooter_id"):
            query = query.join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            ).filter(
                IndividualPracticeSessionModel.shooter_id == filter_params["shooter_id"]
            )

        if filter_params.get("exercise_type_id"):
            query = query.filter(
                PracticeExerciseModel.exercise_type_id
                == filter_params["exercise_type_id"]
            )

        if filter_params.get("target_id"):
            query = query.filter(
                PracticeExerciseModel.target_id == filter_params["target_id"]
            )

        if filter_params.get("weapon_id"):
            query = query.filter(
                PracticeExerciseModel.weapon_id == filter_params["weapon_id"]
            )
        if filter_params.get("ammunition_id"):
            query = query.filter(
                PracticeExerciseModel.ammunition_id == filter_params["ammunition_id"]
            )

        if filter_params.get("distance"):
            query = query.filter(
                PracticeExerciseModel.distance.ilike(f"%{filter_params['distance']}%")
            )

        if (
            filter_params.get("min_accuracy") is not None
            and filter_params.get("max_accuracy") is not None
        ):
            query = query.filter(
                between(
                    PracticeExerciseModel.accuracy_percentage,
                    filter_params["min_accuracy"],
                    filter_params["max_accuracy"],
                )
            )

        if filter_params.get("start_date") and filter_params.get("end_date"):
            query = query.join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            ).filter(
                between(
                    IndividualPracticeSessionModel.date,
                    filter_params["start_date"],
                    filter_params["end_date"],
                )
            )
        if filter_params.get("search"):
            search_term = f"%{filter_params['search']}%"

            query = (
                query.join(
                    ExerciseTypeModel,
                    PracticeExerciseModel.exercise_type_id == ExerciseTypeModel.id,
                )
                .join(
                    IndividualPracticeSessionModel,
                    PracticeExerciseModel.session_id
                    == IndividualPracticeSessionModel.id,
                )
                .filter(
                    or_(
                        ExerciseTypeModel.name.ilike(search_term),
                        IndividualPracticeSessionModel.location.ilike(search_term),
                        PracticeExerciseModel.distance.ilike(search_term),
                        PracticeExerciseModel.firing_cadence.ilike(search_term),
                    )
                )
            )

        return (
            query.order_by(desc(PracticeExerciseModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def count_by_criteria(db: Session, filter_params: dict) -> int:
        query = db.query(func.count(PracticeExerciseModel.id))

        # aplicamos cada filtro si esta presente
        if filter_params.get("session_id"):
            query = query.filter(
                PracticeExerciseModel.session_id == filter_params["session_id"]
            )

        if filter_params.get("shooter_id"):
            query = query.join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            ).filter(
                IndividualPracticeSessionModel.shooter_id == filter_params["shooter_id"]
            )

        if filter_params.get("exercise_type_id"):
            query = query.filter(
                PracticeExerciseModel.exercise_type_id
                == filter_params["exercise_type_id"]
            )

        if filter_params.get("target_id"):
            query = query.filter(
                PracticeExerciseModel.target_id == filter_params["target_id"]
            )

        if filter_params.get("weapon_id"):
            query = query.filter(
                PracticeExerciseModel.weapon_id == filter_params["weapon_id"]
            )
        if filter_params.get("ammunition_id"):
            query = query.filter(
                PracticeExerciseModel.ammunition_id == filter_params["ammunition_id"]
            )

        if filter_params.get("distance"):
            query = query.filter(
                PracticeExerciseModel.distance.ilike(f"%{filter_params['distance']}%")
            )

        if (
            filter_params.get("min_accuracy") is not None
            and filter_params.get("max_accuracy") is not None
        ):
            query = query.filter(
                between(
                    PracticeExerciseModel.accuracy_percentage,
                    filter_params["min_accuracy"],
                    filter_params["max_accuracy"],
                )
            )

        if filter_params.get("start_date") and filter_params.get("end_date"):
            query = query.join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            ).filter(
                between(
                    IndividualPracticeSessionModel.date,
                    filter_params["start_date"],
                    filter_params["end_date"],
                )
            )
        if filter_params.get("search"):
            search_term = f"%{filter_params['search']}%"

            query = (
                query.join(
                    ExerciseTypeModel,
                    PracticeExerciseModel.exercise_type_id == ExerciseTypeModel.id,
                )
                .join(
                    IndividualPracticeSessionModel,
                    PracticeExerciseModel.session_id
                    == IndividualPracticeSessionModel.id,
                )
                .filter(
                    or_(
                        ExerciseTypeModel.name.ilike(search_term),
                        IndividualPracticeSessionModel.location.ilike(search_term),
                        PracticeExerciseModel.distance.ilike(search_term),
                        PracticeExerciseModel.firing_cadence.ilike(search_term),
                    )
                )
            )

        return query.scalar()

    @staticmethod
    def update(
        db: Session, exercise_id: UUID, exercise_data: dict
    ) -> Optional[PracticeExerciseModel]:
        exercise = (
            db.query(PracticeExerciseModel)
            .filter(PracticeExerciseModel.id == exercise_id)
            .first()
        )

        if not exercise:
            return None

        # actualizamos solo los campos proporcionados
        for key, value in exercise_data.items():
            if hasattr(exercise, key):
                setattr(exercise, key, value)

        if "ammunition_used" in exercise_data or "hits" in exercise_data:
            ammo_used = exercise.ammunition_used
            hits = exercise.hits
            if ammo_used > 0:
                exercise.accuracy_percentage = (hits / ammo_used) * 100

        db.commit()
        db.refresh(exercise)
        return exercise

    @staticmethod
    def delete(db: Session, exercise_id: UUID) -> bool:
        exercise = (
            db.query(PracticeExerciseModel)
            .filter(PracticeExerciseModel.id == exercise_id)
            .first()
        )

        if not exercise:
            return False

        db.delete(exercise)
        db.commit()
        return True

    @staticmethod
    def get_statistics(
        db: Session, shooter_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        query = db.query(
            func.count(PracticeExerciseModel.id).label("total_exercises"),
            func.avg(PracticeExerciseModel.accuracy_percentage).label("avg_accuracy"),
            func.sum(PracticeExerciseModel.ammunition_used).label(
                "total_ammunition_used"
            ),
            func.sum(PracticeExerciseModel.hits).label("total_hits"),
            func.avg(PracticeExerciseModel.reaction_time).label("avg_reaction_time"),
        )

        if shooter_id:
            query = query.join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            ).filter(IndividualPracticeSessionModel.shooter_id == shooter_id)

        stats = query.first()

        distance_stats = db.query(
            PracticeExerciseModel.distance,
            func.count(PracticeExerciseModel.id).label("count"),
            func.avg(PracticeExerciseModel.accuracy_percentage).label("avg_accuracy"),
        )

        if shooter_id:
            distance_stats = distance_stats.join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            ).filter(IndividualPracticeSessionModel.shooter_id == shooter_id)

        distance_stats = (
            distance_stats.group_by(PracticeExerciseModel.distance)
            .order_by(desc("count"))
            .all()
        )

        # obtener estadisticas por tipo de ejercicio
        exercise_type_stats = db.query(
            ExerciseTypeModel.name,
            func.count(PracticeExerciseModel.id).label("count"),
            func.avg(PracticeExerciseModel.accuracy_percentage).label("avg_accuracy"),
        ).join(
            ExerciseTypeModel,
            PracticeExerciseModel.exercise_type_id == ExerciseTypeModel.id,
        )

        if shooter_id:
            exercise_type_stats = exercise_type_stats.join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            ).filter(IndividualPracticeSessionModel.shooter_id == shooter_id)

        exercise_type_stats = (
            exercise_type_stats.group_by(ExerciseTypeModel.name)
            .order_by(desc("count"))
            .all()
        )

        # obtener estadisticas por arma
        weapon_stats = db.query(
            WeaponModel.name,
            func.count(PracticeExerciseModel.id).label("count"),
            func.avg(PracticeExerciseModel.accuracy_percentage).label("avg_accuracy"),
        ).join(WeaponModel, PracticeExerciseModel.weapon_id == WeaponModel.id)

        if shooter_id:
            weapon_stats = weapon_stats.join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            ).filter(IndividualPracticeSessionModel.shooter_id == shooter_id)

        weapon_stats = (
            weapon_stats.group_by(WeaponModel.name).order_by(desc("count")).all()
        )

        # por municion
        ammunition_stats = db.query(
            AmmunitionModel.name,
            func.count(PracticeExerciseModel.id).label("count"),
            func.avg(PracticeExerciseModel.accuracy_percentage).label("avg_accuracy"),
        ).join(
            AmmunitionModel, PracticeExerciseModel.ammunition_id == AmmunitionModel.id
        )

        if shooter_id:
            ammunition_stats = ammunition_stats.join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            ).filter(IndividualPracticeSessionModel.shooter_id == shooter_id)

        ammunition_stats = (
            ammunition_stats.group_by(AmmunitionModel.name)
            .order_by(desc("count"))
            .all()
        )

        return {
            "total_exercises": stats.total_exercises if stats.total_exercises else 0,
            "avg_accuracy": float(stats.avg_accuracy) if stats.avg_accuracy else 0.0,
            "total_ammunition_used": (
                stats.total_ammunition_used if stats.total_ammunition_used else 0
            ),
            "total_hits": stats.total_hits if stats.total_hits else 0,
            "hit_percentage": (
                (stats.total_hits / stats.total_ammunition_used * 100)
                if stats.total_ammunition_used and stats.total_ammunition_used > 0
                else 0.0
            ),
            "avg_reaction_time": (
                float(stats.avg_reaction_time) if stats.avg_reaction_time else None
            ),
            "by_distance": [
                {
                    "distance": d.distance,
                    "count": d.count,
                    "avg_accuracy": float(d.avg_accuracy) if d.avg_accuracy else 0.0,
                }
                for d in distance_stats
            ],
            "by_exercise_type": [
                {
                    "name": e.name,
                    "count": e.count,
                    "avg_accuracy": float(e.avg_accuracy) if e.avg_accuracy else 0.0,
                }
                for e in exercise_type_stats
            ],
            "by_weapon": [
                {
                    "name": w.name,
                    "count": w.count,
                    "avg_accuracy": float(w.avg_accuracy) if w.avg_accuracy else 0.0,
                }
                for w in weapon_stats
            ],
            "by_ammunition": [
                {
                    "name": a.name,
                    "count": a.count,
                    "avg_accuracy": float(a.avg_accuracy) if a.avg_accuracy else 0.0,
                }
                for a in ammunition_stats
            ],
        }

    @staticmethod
    def get_performance_analysis_by_category(
        db: Session,
        category: str,  # 'weapon', 'ammunition', 'target', 'exercise_type', etc
        shooter_id: Optional[UUID] = None,
    ) -> List[Dict[str, Any]]:
        # esta funcion permite obtener el analisis por diferntes categorias
        if category == "weapon":
            query = db.query(
                WeaponModel.id,
                WeaponModel.name,
                func.count(PracticeExerciseModel.id).label("exercices_count"),
                func.avg(PracticeExerciseModel.accuracy_percentage).label(
                    "avg_accuracy"
                ),
                func.sum(PracticeExerciseModel.ammunition_used).label(
                    "total_ammunition"
                ),
                func.sum(PracticeExerciseModel.hits).label("total_hits"),
            ).join(WeaponModel, PracticeExerciseModel.weapon_id == WeaponModel.id)

            group_by_field = WeaponModel.id
            order_by_field = WeaponModel.name
        elif category == "target":
            query = db.query(
                TargetModel.id,
                TargetModel.name,
                func.count(PracticeExerciseModel.id).label("exercices_count"),
                func.avg(PracticeExerciseModel.accuracy_percentage).label(
                    "avg_accuracy"
                ),
                func.sum(PracticeExerciseModel.ammunition_used).label(
                    "total_ammunition"
                ),
                func.sum(PracticeExerciseModel.hits).label("total_hits"),
            ).join(TargetModel, PracticeExerciseModel.target_id == TargetModel.id)

            group_by_field = TargetModel.id
            order_by_field = TargetModel.name

        elif category == "ammunition":
            query = db.query(
                AmmunitionModel.id,
                AmmunitionModel.name,
                func.count(PracticeExerciseModel.id).label("exercices_count"),
                func.avg(PracticeExerciseModel.accuracy_percentage).label(
                    "avg_accuracy"
                ),
                func.sum(PracticeExerciseModel.ammunition_used).label(
                    "total_ammunition"
                ),
                func.sum(PracticeExerciseModel.hits).label("total_hits"),
            ).join(
                AmmunitionModel,
                PracticeExerciseModel.ammunition_id == AmmunitionModel.id,
            )

            group_by_field = AmmunitionModel.id
            order_by_field = AmmunitionModel.name

        elif category == "exercise_type":
            query = db.query(
                ExerciseTypeModel.id,
                ExerciseTypeModel.name,
                func.count(PracticeExerciseModel.id).label("exercices_count"),
                func.avg(PracticeExerciseModel.accuracy_percentage).label(
                    "avg_accuracy"
                ),
                func.sum(PracticeExerciseModel.ammunition_used).label(
                    "total_ammunition"
                ),
                func.sum(PracticeExerciseModel.hits).label("total_hits"),
            ).join(
                ExerciseTypeModel,
                PracticeExerciseModel.exercise_type_id == ExerciseTypeModel.id,
            )

            group_by_field = ExerciseTypeModel.id
            order_by_field = ExerciseTypeModel.name

        else:
            return []

        if shooter_id:
            query = query.join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            ).filter(IndividualPracticeSessionModel.shooter_id == shooter_id)

        # agrupar y ordenar
        results = query.group_by(group_by_field).order_by(order_by_field).all()

        # convertimos a una lista de diccionarios mas legible
        analysis_results = []
        for row in results:
            result_dict = {}

            # los campos dependen de la categoria
            if category in ["weapon", "target", "ammunition", "exercise_type"]:
                result_dict = {
                    "id": str(row[0]),
                    "name": row[1],
                    "exercises_count": row[2],
                    "avg_accuracy": float(row[3]) if row[3] else 0.0,
                    "total_ammunition": row[4] if row[4] else 0,
                    "total_hits": row[5] if row[5] else 0,
                    "hit_percentage": (
                        (row[5] / row[4] * 100) if row[4] and row[4] > 0 else 0.0
                    ),
                }
            else:  # distance
                result_dict = {
                    "distance": row[0],
                    "exercises_count": row[1],
                    "avg_accuracy": float(row[2]) if row[2] else 0.0,
                    "total_ammunition": row[3] if row[3] else 0,
                    "total_hits": row[4] if row[4] else 0,
                    "hit_percentage": (
                        (row[4] / row[3] * 100) if row[3] and row[3] > 0 else 0.0
                    ),
                }
            analysis_results.append(result_dict)

        return analysis_results

    @staticmethod
    def get_with_relations(
        db: Session, exercise_id: UUID, relations: List[str] = None
    ) -> Optional[PracticeExerciseModel]:
        query = select(PracticeExerciseModel).where(
            PracticeExerciseModel.id == exercise_id
        )

        if relations:
            if "target_image" in relations:
                query = query.options(joinedload(PracticeExerciseModel.target_image))
            if "session" in relations:
                query = query.options(joinedload(PracticeExerciseModel.session))
            if "exercise_type" in relations:
                query = query.options(joinedload(PracticeExerciseModel.exercise_type))
            if "weapon" in relations:
                query = query.options(joinedload(PracticeExerciseModel.weapon))
            if "ammunition" in relations:
                query = query.options(joinedload(PracticeExerciseModel.ammunition))
            if "target" in relations:
                query = query.options(joinedload(PracticeExerciseModel.target))

        result = db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def update_metrics(db: Session, exercise_id: UUID, metrics: Dict) -> bool:
        try:
            allowed_fields = {
                "ammunition_used",
                "hits",
                "accuracy_percentage",
                "reaction_time",
                "updated_at",
            }
            # solo actualizar los campo permitidos
            update_data = {k: v for k, v in metrics.items() if k in allowed_fields}

            if not update_data:
                return False

            stmt = (
                update(PracticeExerciseModel)
                .where(PracticeExerciseModel.id == exercise_id)
                .values(**update_data)
            )

            result = db.execute(stmt)
            db.commit()

            return result.rowcount > 0
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating metrics: {e}")
            raise e

    @staticmethod
    def get_exercises_with_images(
        db: Session, session_id: UUID
    ) -> List[PracticeExerciseModel]:
        query = (
            select(PracticeExerciseModel)
            .where(
                PracticeExerciseModel.session_id == session_id,
                PracticeExerciseModel.target_image_id.is_not(None),
            )
            .options(joinedload(PracticeExerciseModel.target_image))
        )

        result = db.execute(query)
        return result.scalars().all()

    @staticmethod
    def update_exercise(
        db: Session, exercise_id: UUID, **kwargs
    ) -> Optional[PracticeExerciseModel]:
        try:
            exercise = PracticeExerciseRepository.get_by_id(exercise_id)
            if not exercise:
                return None

            # Actualizar campos proporcionados
            for key, value in kwargs.items():
                if hasattr(exercise, key):
                    setattr(exercise, key, value)

            db.commit()
            db.refresh(exercise)
            return exercise

        except Exception as e:
            db.rollback()
            raise e
