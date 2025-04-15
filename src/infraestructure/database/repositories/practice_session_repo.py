from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, between, desc
from datetime import datetime, timedelta

from ..models.practice_session_model import IndividualPracticeSessionModel as PracticeSessionModel
from ..models.shooter_model import ShooterModel
from ..models.practice_exercise_model import PracticeExerciseModel

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
        return db.query(PracticeSessionModel).options(
            joinedload(PracticeSessionModel.shooter),
            joinedload(PracticeSessionModel.exercises),
            joinedload(PracticeSessionModel.evaluation)
        ).filter(PracticeSessionModel.id == session_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int=100) -> List[PracticeSessionModel]:
        return db.query(PracticeSessionModel).options(
            joinedload(PracticeSessionModel.shooter),
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_shooter(db: Session, shooter_id: UUID, skip: int = 0, limit: int=100) -> List[PracticeSessionModel]:
        return db.query(PracticeSessionModel).options(
            joinedload(PracticeSessionModel.evaluation),
        ).filter(
            PracticeSessionModel.shooter_id == shooter_id
        ).order_by(
            PracticeSessionModel.date.desc()
        ).offset(skip).limit(limit).all()
        
    @staticmethod
    def get_by_date_range(db: Session, start_date: datetime, end_date: datetime, shooter_id: Optional[UUID] = None) -> List[PracticeSessionModel]:
        query = db.query(PracticeSessionModel).filter(
            PracticeSessionModel.date.between(start_date, end_date)
        )
        if shooter_id:
            query = query.filter(PracticeSessionModel.shooter_id == shooter_id)
            
        return query.order_by(PracticeSessionModel.date).all()
    
    @staticmethod
    def update(db: Session, session_id: UUID, session_data :dict) -> Optional[PracticeSessionModel]:
        session = db.query(PracticeSessionModel).filter(
            PracticeSessionModel.id == session_id
        ).first()
        
        if not session:
            return None
        
        for key, value in session_data.items():
            if hasattr(session, key):
                setattr(session, key, value)
                
        db.flush()
        return session
    
    @staticmethod
    def delete(db: Session, session_id: UUID) -> bool:
        session = PracticeSessionRepository.get_by_id(db, session_id=session_id)
        if not session:
            return False
        
        db.delete(session)
        db.flush()
        
        return True
    
    @staticmethod
    def get_statistics(db: Session, shooter_id: UUID, period: Optional[str] = None) -> dict:
        
        end_date = datetime.now()
        start_date = None
        
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month": 
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
            
        query = db.query(
            func.count(PracticeSessionModel.id).label("total_sessions"),
            func.avg(PracticeSessionModel.accuracy_percentage).label("avg_accuracy"),
            func.sum(PracticeSessionModel.total_shots_fired).label("total_shots"),
            func.sum(PracticeSessionModel.total_hits).label("total_hits")
        ).filter(
            PracticeSessionModel.shooter_id == shooter_id
        )
        
        if start_date:
            query = query.filter(PracticeSessionModel.date.between(start_date, end_date))
            
        stats = query.first()
        
        locations_query = db.query(
            PracticeSessionModel.location,
            func.count(PracticeSessionModel.id).label("count")
        ).filter(
            PracticeSessionModel.shooter_id == shooter_id
        ).order_by(
            func.count(PracticeSessionModel.id).desc()
        ).limit(3)
        
        return {
            "total_sessions": stats.total_sessions if stats.total_sessions else 0,
            "avg_accuracy": float(stats.avg_accuracy) if stats.avg_accuracy else 0.0,
            "total_shots": stats.total_shots if stats.total_shots else 0,
            "total_hits": stats.total_hits if stats.total_hits else 0,
            "period": period if period else "all_time",
            "shooter_id": str(shooter_id)
        }
        
        
        

