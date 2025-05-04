from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import func, or_, desc, and_
from sqlalchemy.orm import Session, joinedload

from src.infraestructure.database.models.practice_exercise_model import PracticeExerciseModel
from src.infraestructure.database.models.evaluation_model import PracticeEvaluationModel
from src.infraestructure.database.models.practice_session_model import IndividualPracticeSessionModel
from src.infraestructure.database.models.shooter_model import ShooterModel
from src.domain.enums.classification_enum import ShooterLevelEnum

class PracticeEvaluationRepository:
    @staticmethod
    def create(db: Session, evaluation_data: dict)-> PracticeEvaluationModel:
        evaluation = PracticeEvaluationModel(**evaluation_data)
        db.add(evaluation)

        # Actualizar el estado de evaluacion pendiente en la session
        session = db.query(IndividualPracticeSessionModel).filter(
            IndividualPracticeSessionModel.id == evaluation_data["session_id"]
        ).first()

        if session:
            session.evaluation_pending = False

        db.commit()
        db.refresh(evaluation)
        return evaluation

    @staticmethod
    def get_by_id(db: Session, evaluation_id: UUID)-> Optional[PracticeEvaluationModel]:
        return db.query(PracticeEvaluationModel).options(
            joinedload(PracticeEvaluationModel.session),
            joinedload(PracticeEvaluationModel.evaluator)
        ).filter(
            PracticeEvaluationModel.id == evaluation_id
        ).first()

    @staticmethod
    def get_by_session_id(db: Session, session_id: UUID)-> Optional[PracticeEvaluationModel]:
        return db.query(PracticeEvaluationModel).options(
            joinedload(PracticeEvaluationModel.session),
        ).filter(
            PracticeEvaluationModel.session_id == session_id
        ).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[PracticeEvaluationModel]:
        return db.query(PracticeEvaluationModel).options(
            joinedload(PracticeEvaluationModel.session),
            joinedload(PracticeEvaluationModel.evaluator)
        ).order_by(
            desc(PracticeEvaluationModel.date)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_shooter(
        db: Session,
        shooter_id: UUID,
        skip: int = 0,
        limit: int = 100
    )-> List[PracticeEvaluationModel]:
        return db.query(PracticeEvaluationModel).join(
            IndividualPracticeSessionModel,
            PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id
        ).filter(
            IndividualPracticeSessionModel.shooter_id == shooter_id
        ).order_by(
            desc(PracticeEvaluationModel.date)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_evaluator(
        db: Session,
        evaluator_id:UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[PracticeEvaluationModel]:
        return db.query(PracticeEvaluationModel).filter(
            PracticeEvaluationModel.evaluator_id == evaluator_id
        ).order_by(
            desc(PracticeEvaluationModel.date)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, evaluation_id: UUID, evaluation_data: dict)-> Optional[PracticeEvaluationModel]:
        evaluation = db.query(PracticeEvaluationModel).filter(
            PracticeEvaluationModel.id == evaluation_id
        ).first()

        if not evaluation:
            return None

        for key, value in evaluation_data.items():
            if hasattr(evaluation, key):
                setattr(evaluation, key, value)

        db.commit()
        db.refresh(evaluation)
        return evaluation

    @staticmethod
    def delete(db: Session, evaluation_id: UUID) -> bool:
        evaluation = db.query(PracticeEvaluationModel).filter(
            PracticeEvaluationModel.id == evaluation_id
        ).first()

        if not evaluation:
            return False

        # Restaurar el estado de evaluacion pendiente en la session
        session = db.query(IndividualPracticeSessionModel).filter(
            IndividualPracticeSessionModel.id == evaluation.session_id
        ).first()

        if session:
            session.evaluation_pending = True

        db.delete(evaluation)
        db.commit()
        return True

    @staticmethod
    def get_shooter_evaluation_history(
        db: Session,
        shooter_id: UUID,
        limit: int = 10
    ) -> List[PracticeEvaluationModel]:
        # Obtiene las evaluaciones mas recientes de un tirador
        return db.query(PracticeEvaluationModel).join(
            IndividualPracticeSessionModel,
            PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id
        ).filter(
            IndividualPracticeSessionModel.shooter_id == shooter_id
        ).order_by(
            desc(PracticeEvaluationModel.date)
        ).limit(limit).all()

    @staticmethod
    def get_shooter_classification_distribution(db: Session, shooter_id: UUID)-> Dict[str, int]:
        # Obtiene la distribucion de clasificaciones del tirador a lo largo del tiempo
        query = db.query(
            PracticeEvaluationModel.classification,
            func.count(PracticeEvaluationModel.id).label("count")
        ).join(
            IndividualPracticeSessionModel,
            PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id
        ).filter(
            IndividualPracticeSessionModel.shooter_id == shooter_id
        ).group_by(
            PracticeEvaluationModel.classification
        ).all()

        #dict con todas las clasificaciones posibles
        distribution = {level.name: 0 for level in ShooterLevelEnum}

        # actualizar los conteos reales
        for classification, count in query:
            distribution[classification.name] = count

        return distribution

    @staticmethod
    def get_issue_zones_frequency(db: Session, shooter_id: UUID)->Dict[str, int]:
        pass

    @staticmethod
    def get_average_ratings(db: Session, shooter_id: UUID)-> Dict[str, float]:
        # calcula promedios de las calificaciones especificas (postura, agarre, etc)
        query = db.query(
            func.avg(PracticeEvaluationModel.posture_rating).label("posture"),
            func.avg(PracticeEvaluationModel.grip_rating).label("grip"),
            func.avg(PracticeEvaluationModel.sight_alignment_rating).label("sight_alignment"),
            func.avg(PracticeEvaluationModel.trigger_control_rating).label("trigger_control"),
            func.avg(PracticeEvaluationModel.breathing_rating).label("breathing")
        ).join(
            IndividualPracticeSessionModel,
            PracticeEvaluationModel.session_id == IndividualPracticeSessionModel.id
        ).filter(
            IndividualPracticeSessionModel.shooter_id == shooter_id
        ).first()

        ratings = {}

        if query:
            for key, value in query._asdict().items():
                ratings[key] = float(value) if value is not None else None

        return ratings

    @staticmethod
    def check_classification_change_criteria(db: Session, shooter_id: UUID, curre)
