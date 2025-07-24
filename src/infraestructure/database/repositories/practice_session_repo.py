from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, between, desc, select, update, and_
from datetime import datetime, timedelta, timezone
import logging

from ..models.practice_session_model import (
    IndividualPracticeSessionModel as PracticeSessionModel,
)
from ..models.shooter_model import ShooterModel
from ..models.user_model import UserPersonalDataModel, UserModel
from ..models.practice_exercise_model import PracticeExerciseModel

logger = logging.getLogger(__name__)


class PracticeSessionRepository:

    @staticmethod
    def create(db: Session, session_data: dict) -> PracticeSessionModel:
        session = PracticeSessionModel(**session_data)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_by_id(db: Session, session_id: UUID) -> Optional[PracticeSessionModel]:
        return (
            db.query(PracticeSessionModel)
            .options(
                joinedload(PracticeSessionModel.shooter).options(
                    joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                ),
                joinedload(PracticeSessionModel.exercises),
                joinedload(PracticeSessionModel.evaluation),
                joinedload(PracticeSessionModel.instructor),
            )
            .filter(PracticeSessionModel.id == session_id)
            .first()
        )

    @staticmethod
    def get_with_exercises(
        db: Session, session_id: UUID
    ) -> Optional[PracticeSessionModel]:

        # result = db.execute(query)
        return (
            db.query(PracticeSessionModel)
            .options(joinedload(PracticeSessionModel.exercises))
            .filter(PracticeSessionModel.id == session_id)
            .first()
        )

    @staticmethod
    def update_totals(db: Session, session_id: UUID) -> bool:
        try:
            totals = PracticeSessionRepository.calculate_totals(db, session_id)
            if totals["error"]:
                return False

            stmt = (
                update(PracticeSessionModel)
                .where(PracticeSessionModel.id == session_id)
                .values(
                    total_shots_fired=totals["total_shots_fired"],
                    total_hits=totals["total_hits"],
                    accuracy_percentage=totals["accuracy_percentage"],
                )
            )
            result = db.execute(stmt)
            db.commit()
            return result.rowcount > 0
        except Exception as e:
            db.rollback()
            return False

    @staticmethod
    def calculate_totals(db: Session, session_id: UUID) -> Dict:
        try:
            query = select(
                func.sum(PracticeExerciseModel.ammunition_used).label("total_shots"),
                func.sum(PracticeExerciseModel.hits).label("total_hits"),
                func.count(PracticeExerciseModel.id).label("exercise_count"),
            ).where(PracticeExerciseModel.session_id == session_id)

            result = db.execute(query)
            row = result.fetchone()
            if not row:
                return {
                    "total_shots_fired": 0,
                    "total_hits": 0,
                    "accuracy_percentage": 0.0,
                    "error": "No se encontraron ejercicios",
                }
            total_shots = row[0] or 0
            total_hits = row[1] or 0
            exercise_count = row[2] or 0

            accuracy_percentage = 0.0
            if total_shots > 0:
                accuracy_percentage = (total_hits / total_shots) * 100

            return {
                "total_shots_fired": total_shots,
                "total_hits": total_hits,
                "accuracy_percentage": round(accuracy_percentage, 2),
                "exercise_count": exercise_count,
                "error": None,
            }
        except Exception as e:
            return {
                "total_shots_fired": 0,
                "total_hits": 0,
                "accuracy_percentage": 0.0,
                "error": str(e),
            }

    @staticmethod
    def finish_session(db: Session, session_id: UUID) -> bool:
        try:
            if not PracticeSessionRepository.update_totals(db, session_id):
                return False

            stmt = (
                update(PracticeSessionModel)
                .where(PracticeSessionModel.id == session_id)
                .values(is_finished=True, evaluation_pending=True)
            )
            result = db.execute(stmt)
            db.commit()
            return result.rowcount > 0
        except Exception as e:
            db.rollback()
            return False

    @staticmethod
    def can_modify_session(db: Session, session_id: UUID) -> bool:
        session = PracticeSessionRepository.get_by_id(db, session_id=session_id)
        return session and not session.is_finished

    @staticmethod
    def get_sessions_by_shooter(
        db: Session, shooter_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeSessionModel]:
        return (
            db.query(PracticeSessionModel)
            .filter(PracticeSessionModel.shooter_id == shooter_id)
            .order_by(desc(PracticeSessionModel.date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_sessions_by_instructor(
        db: Session, instructor_id: UUID, only_pending: bool = True
    ):
        query = select(PracticeSessionModel).where(
            PracticeSessionModel.instructor_id == instructor_id
        )

        if only_pending:
            query = query.where(
                and_(
                    PracticeSessionModel.is_finished == True,
                    PracticeSessionModel.evaluation_pending == True,
                )
            )
        result = db.execute(query)
        return result.scalars().all()

    @staticmethod
    def get_finished_sessions_by_shooter(
        db: Session, shooter_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeSessionModel]:
        return (
            db.query(PracticeSessionModel)
            .filter(
                PracticeSessionModel.shooter_id == shooter_id,
                PracticeSessionModel.is_finished == True,
            )
            .order_by(desc(PracticeSessionModel.date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_session(
        db: Session, session_id: UUID, **kwargs
    ) -> Optional[PracticeSessionModel]:
        session = PracticeSessionRepository.get_by_id(db, session_id=session_id)
        if not session:
            return None

        if session.is_finished and "is_finished" not in kwargs:
            raise

        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session_summary(db: Session, session_id: UUID) -> Dict:
        session = PracticeSessionRepository.get_by_id(db, session_id=session_id)
        if not session:
            return {"error": "Sesión no encontrada"}

        exercises = session.exercises
        exercise_summary = []
        for exercise in exercises:
            exercise_summary.append(
                {
                    "id": str(exercise.id),
                    "exercise_type": (
                        {
                            "name": exercise.exercise_type.name,
                            "description": exercise.exercise_type.description,
                            "difficulty": exercise.exercise_type.difficulty,
                        }
                        if exercise.exercise_type
                        else None
                    ),
                    "weapon": {
                        "id": str(exercise.weapon.id) if exercise.weapon else None,
                        "name": exercise.weapon.name if exercise.weapon else None,
                        "caliber": exercise.weapon.caliber if exercise.weapon else None,
                    },
                    "ammunition": {
                        "id": (
                            str(exercise.ammunition.id) if exercise.ammunition else None
                        ),
                        "name": (
                            exercise.ammunition.name if exercise.ammunition else None
                        ),
                        "caliber": (
                            exercise.ammunition.caliber if exercise.ammunition else None
                        ),
                    },
                    "ammunition_allocated": exercise.ammunition_allocated,
                    "ammunition_used": exercise.ammunition_used,
                    "hits": exercise.hits,
                    "accuracy_percentage": exercise.accuracy_percentage,
                    "has_image": exercise.target_image_id is not None,
                }
            )
        return {
            "session_id": str(session.id),
            "shooter_id": str(session.shooter_id),
            "date": session.date,
            "location": session.location,
            "is_finished": session.is_finished,
            "evaluation_pending": session.evaluation_pending,
            "total_shots_fired": session.total_shots_fired,
            "total_hits": session.total_hits,
            "accuracy_percentage": session.accuracy_percentage,
            "exercise_count": len(exercises),
            "exercises": exercise_summary,
        }

    @staticmethod
    def get_all(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[PracticeSessionModel]:
        return (
            db.query(PracticeSessionModel)
            .options(
                joinedload(PracticeSessionModel.shooter),
            )
            .order_by(desc(PracticeSessionModel.date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_shooter(
        db: Session, shooter_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PracticeSessionModel]:
        return (
            db.query(PracticeSessionModel)
            .options(
                joinedload(PracticeSessionModel.evaluation),
            )
            .filter(PracticeSessionModel.shooter_id == shooter_id)
            .order_by(desc(PracticeSessionModel.date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_instructor(
        db: Session, instructor_id: UUID, skip: int = 0, limit: int = 100
    ):
        return (
            db.query(PracticeSessionModel)
            .options(joinedload(PracticeSessionModel.shooter))
            .filter(PracticeSessionModel.instructor_id == instructor_id)
            .order_by(desc(PracticeSessionModel.date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_date_range(
        db: Session,
        start_date: datetime,
        end_date: datetime,
        shooter_id: Optional[UUID] = None,
    ) -> List[PracticeSessionModel]:
        query = db.query(PracticeSessionModel).filter(
            between(PracticeSessionModel.date, start_date, end_date)
        )
        if shooter_id:
            query = query.filter(PracticeSessionModel.shooter_id == shooter_id)

        return query.order_by(PracticeSessionModel.date).all()

    @staticmethod
    def search_by_term(db: Session, term: str) -> List[PracticeSessionModel]:
        return (
            db.query(PracticeSessionModel)
            .join(ShooterModel, PracticeSessionModel.shooter_id == ShooterModel.user_id)
            .filter(
                or_(
                    PracticeSessionModel.location.ilike(f"%{term}%"),
                    UserPersonalDataModel.first_name.ilike(f"%{term}%"),
                    UserPersonalDataModel.last_name1.ilike(f"%{term}%"),
                    UserPersonalDataModel.last_name2.ilike(f"%{term}%"),
                )
            )
            .order_by(desc(PracticeSessionModel.date))
            .all()
        )

    @staticmethod
    def update(
        db: Session, session_id: UUID, session_data: dict
    ) -> Optional[PracticeSessionModel]:
        session = (
            db.query(PracticeSessionModel)
            .filter(PracticeSessionModel.id == session_id)
            .first()
        )

        if not session:
            return None

        for key, value in session_data.items():
            if hasattr(session, key):
                setattr(session, key, value)

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete(db: Session, session_id: UUID) -> bool:
        session = PracticeSessionRepository.get_by_id(db, session_id=session_id)
        if not session:
            return False

        db.delete(session)
        db.commit()

        return True

    @staticmethod
    def get_statistics(
        db: Session, shooter_id: UUID, period: Optional[str] = None
    ) -> dict:
        # Determina el rango de fechas según el período
        end_date = datetime.now(timezone.utc)
        start_date = None

        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)

        # Consulta base para estadísticas
        query = db.query(
            func.count(PracticeSessionModel.id).label("total_sessions"),
            func.avg(PracticeSessionModel.accuracy_percentage).label("avg_accuracy"),
            func.sum(PracticeSessionModel.total_shots_fired).label("total_shots"),
            func.sum(PracticeSessionModel.total_hits).label("total_hits"),
        ).filter(PracticeSessionModel.shooter_id == shooter_id)

        # Aplica filtro de fecha si se especificó un período
        if start_date:
            query = query.filter(
                between(PracticeSessionModel.date, start_date, end_date)
            )

        stats = query.first()

        # Calcula métricas adicionales
        return {
            "total_sessions": stats.total_sessions if stats.total_sessions else 0,
            "avg_accuracy": float(stats.avg_accuracy) if stats.avg_accuracy else 0.0,
            "total_shots": stats.total_shots if stats.total_shots else 0,
            "total_hits": stats.total_hits if stats.total_hits else 0,
            "hit_percentage": (
                (stats.total_hits / stats.total_shots * 100)
                if stats.total_shots and stats.total_shots > 0
                else 0.0
            ),
            "period": period if period else "all_time",
            "shooter_id": str(shooter_id),
        }

    @staticmethod
    def get_by_accuracy_range(
        db: Session,
        min_accuracy: float,
        max_accuracy: float,
        shooter_id: Optional[UUID] = None,
    ) -> List[PracticeSessionModel]:
        query = db.query(PracticeSessionModel).filter(
            between(
                PracticeSessionModel.accuracy_percentage, min_accuracy, max_accuracy
            )
        )

        if shooter_id:
            query = query.filter(PracticeSessionModel.shooter_id == shooter_id)

        return query.order_by(desc(PracticeSessionModel.accuracy_percentage)).all()

    @staticmethod
    def count_sessions(db: Session, shooter_id: Optional[UUID] = None) -> int:
        query = db.query(func.count(PracticeSessionModel.id))

        if shooter_id:
            query = query.filter(PracticeSessionModel.shooter_id == shooter_id)

        return query.scalar()

    @staticmethod
    def get_user_sessions(
        db: Session,
        user_id: UUID,
        is_finished: Optional[bool] = None,
        skip: int = 0,
        limit: int = 5,
    ) -> List[PracticeSessionModel]:
        query = db.query(PracticeSessionModel).filter(
            PracticeSessionModel.shooter_id == user_id
        )

        if is_finished is not None:
            query = query.filter(PracticeSessionModel.is_finished == is_finished)
        query = query.order_by(desc(PracticeSessionModel.created_at))
        return (
            query.order_by(desc(PracticeSessionModel.date))
            .offset(skip)
            .limit(limit)
            .all()
        )
