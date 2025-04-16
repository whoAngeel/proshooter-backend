from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import math

from src.infraestructure.database.repositories.practice_session_repo import PracticeSessionRepository
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.infraestructure.database.repositories.user_repo import UserRepository, UserPersonalDataRepository
from src.infraestructure.database.session import get_db
from src.presentation.schemas.practice_session_schema import (
    InstructorInfo,
    ShooterInfo,
    IndividualPracticeSessionBase,
    IndividualPracticeSessionCreate,
    IndividualPracticeSessionRead,
    IndividualPracticeSessionUpdate,
    IndividualPracticeSessionDetail,
    IndividualPracticeSessionFilter,
    IndividualPracticeSessionList,
    IndividualPracticeSessionStatistics
)

class PracticeSessionService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_session(self, session_data: IndividualPracticeSessionCreate, user_id: UUID) -> Tuple[Optional[IndividualPracticeSessionRead], Optional[str]]:
        try:
            shooter = ShooterRepository.get_by_user_id(self.db, user_id)
            if not shooter:
                return None, "SHOOTER_NOT_FOUND"

            # verificar
            if session_data.instructor_id:
                instructor = UserRepository.get_by_id(self.db, session_data.instructor_id)
                if not instructor:
                    return None, "INSTRUCTOR_NOT_FOUND"

            session_dict = session_data.model_dump()
            session_dict["shooter_id"] = shooter.user_id


            if session_data.total_shots_fired > 0:
                session_dict["accuracy_percentage"] = (session_data.total_hits / session_data.total_shots_fired) * 100
            else:
                session_dict["accuracy_percentage"] = 0.0

            new_session = PracticeSessionRepository.create(self.db, session_dict)
            return IndividualPracticeSessionRead.model_validate(new_session), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_CRAETING_PRACTICE_SESSION: {str(e)}"

    # def get_session_by_id(self, session_id: UUID) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    def get_session_by_id(self, session_id: UUID) -> Tuple[Optional[IndividualPracticeSessionDetail], Optional[str]]:
        session = PracticeSessionRepository.get_by_id(self.db, session_id)
        if not session:
            return None, "PRACTICE_SESSION_NOT_FOUND"

        # return IndividualPracticeSessionDetail.model_validate(session), None
        return session, None

    def get_all_sessions(self, filter_params: IndividualPracticeSessionFilter) -> IndividualPracticeSessionList:
        sessions = []
        total_count = 0

        if filter_params.search:
            sessions = PracticeSessionRepository.search_by_term(self.db, filter_params.search)
            total_count = len(sessions)

            sessions = sessions[filter_params.skip:filter_params.skip + filter_params.limit]
        elif filter_params.shooter_id:
            sessions = PracticeSessionRepository.get_by_shooter(
                self.db, filter_params.shooter_id, filter_params.skip, filter_params.limit
            )
            total_count = PracticeSessionRepository.count_sessions(self.db, filter_params.shooter_id)
        elif filter_params.instructor_id:
            sessions = PracticeSessionRepository.get_by_instructor(
                self.db, filter_params.instructor_id, filter_params.skip, filter_params.limit
            )
            total_count = len(PracticeSessionRepository.get_by_instructor(self.db, filter_params.instructor_id))
        elif filter_params.start_date and filter_params.end_date:
            sessions = PracticeSessionRepository.get_by_date_range(
                self.db, filter_params.start_date, filter_params.end_date, filter_params.shooter_id
            )
            total_count = len(sessions)
            sessions = sessions[filter_params.skip:filter_params.skip + filter_params.limit]
        elif filter_params.min_accuracy is not None and filter_params.max_accuracy is not None:
            sessions = PracticeSessionRepository.get_by_accuracy_range(
                self.db, filter_params.min_accuracy, filter_params.max_accuracy, filter_params.shooter_id
            )
            total_count = len(sessions)
            sessions = sessions[filter_params.skip:filter_params.skip + filter_params.limit]
        else:
            sessions = PracticeSessionRepository.get_all(self.db, filter_params.skip, filter_params.limit)
            total_count = PracticeSessionRepository.count_sessions(self.db, filter_params.shooter_id)

        page = (filter_params.skip // filter_params.limit) + 1
        pages = math.ceil(total_count / filter_params.limit) if total_count > 0 else 1

        items = [IndividualPracticeSessionRead.model_validate(session) for session in sessions]

        return IndividualPracticeSessionList(
            items=items,
            total=total_count,
            page=page,
            size=filter_params.limit,
            pages=pages
        )
