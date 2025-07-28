from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import math

from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository,
)
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.infraestructure.database.repositories.user_repo import (
    UserRepository,
    UserPersonalDataRepository,
)
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
    IndividualPracticeSessionStatistics,
    IndividualPracticeSessionDetailLite,
)
from src.presentation.schemas.practice_session_schema import (
    MyPracticeSessionSummary,
    PracticeExerciseSummary,
)
from src.application.services.practice_evaluation_service import (
    PracticeEvaluationService,
)

from src.presentation.schemas.instructor import PracticeSessionCreateRequest
from src.application.services.club_instructor import ClubInstructorService
from src.infraestructure.database.repositories.instructor import InstructorRepository


class PracticeSessionService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.club_instructor_service = ClubInstructorService(self.db)

    def create_session(
        self, session_data: PracticeSessionCreateRequest, user_id: UUID
    ) -> Tuple[Optional[any], Optional[str]]:
        try:
            # verificar que el shooter existe
            shooter = ShooterRepository.get_by_id(self.db, user_id)
            if not shooter:
                return None, "SHOOTER_NOT_FOUND"

            # validar instrotor si se proporciona
            if session_data.instructor_id:
                is_valid, error_msg = (
                    self.club_instructor_service.validate_instructor_selection(
                        session_data.instructor_id, shooter_id=user_id
                    )
                )

                if not is_valid:
                    return None, f"INVALID_INSTRUCTOR_SELECTION: {error_msg}"

            # crear datos de la sesion
            session_dict = {
                "shooter_id": user_id,
                "instructor_id": session_data.instructor_id,  # Puede ser None
                "location": session_data.location,
                "date": (
                    datetime.now()
                    if not session_data.date
                    else self._parse_date(session_data.date)
                ),
                "total_shots_fired": 0,
                "total_hits": 0,
                "accuracy_percentage": 0.0,
                "evaluation_pending": False,  # Se actualiza al finalizar
                "is_finished": False,
            }

            # session_dict = session_data.model_dump()
            # session_dict["shooter_id"] = shooter.user_id

            # if session_data.total_shots_fired > 0:
            #     session_dict["accuracy_percentage"] = (
            #         session_data.total_hits / session_data.total_shots_fired
            #     ) * 100
            # else:
            #     session_dict["accuracy_percentage"] = 0.0

            new_session = PracticeSessionRepository.create(self.db, session_dict)
            return new_session, None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_CRAETING_PRACTICE_SESSION: {str(e)}"

    def get_session_with_instructor_info(self, session_id: UUID) -> Optional[dict]:
        session = PracticeSessionRepository.get_with_exercises(self.db, session_id)
        if not session:
            return None

        # agregar informacion del instructor si existe
        instructor_info = None
        if session.instructor_id:
            instructor = InstructorRepository.get_instructor_basic_info(
                self.db, session.instructor_id
            )
            if instructor:
                instructor_info = {
                    "id": instructor.id,
                    "email": instructor.email,
                    "role": instructor.role,
                    "full_name": self.club_instructor_service._get_full_name(
                        instructor
                    ),
                    "is_chief_instructor": instructor.role == "INSTRUCTOR_JEFE",
                }
        return {
            "session": session,
            "instructor_info": instructor_info,
            "can_be_evaluated": session.instructor_id is not None
            and session.is_finished,
        }

    def update_session_instructor(
        self, session_id: UUID, instructor_id: Optional[UUID], shooter_id: UUID
    ) -> Tuple[bool, Optional[str]]:
        # solo permitir si la sesion no esta finalizada
        session = PracticeSessionRepository.get_by_id(self.db, session_id)
        if not session:
            return False, "SESSION_NOT_FOUND"

        if session.shooter_id != shooter_id:
            return False, "NOT_SESSION_OWNER"

        if session.is_finished:
            return False, "SESSION_ALREADY_FINISHED"

        # validar nuevo instructor si se proporciona
        if instructor_id:
            is_valid, error_msg = (
                self.club_instructor_service.validate_instructor_selection(
                    instructor_id, shooter_id
                )
            )
            if not is_valid:
                return False, f"INVALID_INSTRUCTOR_SELECTION: {error_msg}"

        # actualizar
        success = PracticeSessionRepository.update_session(
            self.db, session_id, instructor_id=instructor_id
        )
        return success, None if success else "ERROR_UPDATING_SESSION_INSTRUCTOR"

    def _parse_date(self, date_str: str) -> datetime:
        return datetime.now()

    # def get_session_by_id(self, session_id: UUID) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    def get_session_by_id(
        self, session_id: UUID
    ) -> Tuple[Optional[IndividualPracticeSessionDetail], Optional[str]]:
        session = PracticeSessionRepository.get_by_id(self.db, session_id)
        if not session:
            return None, "PRACTICE_SESSION_NOT_FOUND"

        return IndividualPracticeSessionDetail.model_validate(session), None
        # return session, None

    def get_all_sessions(
        self, filter_params: IndividualPracticeSessionFilter
    ) -> IndividualPracticeSessionList:
        sessions = []
        total_count = 0

        if filter_params.search:
            sessions = PracticeSessionRepository.search_by_term(
                self.db, filter_params.search
            )
            total_count = len(sessions)

            sessions = sessions[
                filter_params.skip : filter_params.skip + filter_params.limit
            ]
        elif filter_params.shooter_id:
            sessions = PracticeSessionRepository.get_by_shooter(
                self.db,
                filter_params.shooter_id,
                filter_params.skip,
                filter_params.limit,
            )
            total_count = PracticeSessionRepository.count_sessions(
                self.db, filter_params.shooter_id
            )
        elif filter_params.instructor_id:
            sessions = PracticeSessionRepository.get_by_instructor(
                self.db,
                filter_params.instructor_id,
                filter_params.skip,
                filter_params.limit,
            )
            total_count = len(
                PracticeSessionRepository.get_by_instructor(
                    self.db, filter_params.instructor_id
                )
            )
        elif filter_params.start_date and filter_params.end_date:
            sessions = PracticeSessionRepository.get_by_date_range(
                self.db,
                filter_params.start_date,
                filter_params.end_date,
                filter_params.shooter_id,
            )
            total_count = len(sessions)
            sessions = sessions[
                filter_params.skip : filter_params.skip + filter_params.limit
            ]
        elif (
            filter_params.min_accuracy is not None
            and filter_params.max_accuracy is not None
        ):
            sessions = PracticeSessionRepository.get_by_accuracy_range(
                self.db,
                filter_params.min_accuracy,
                filter_params.max_accuracy,
                filter_params.shooter_id,
            )
            total_count = len(sessions)
            sessions = sessions[
                filter_params.skip : filter_params.skip + filter_params.limit
            ]
        else:
            sessions = PracticeSessionRepository.get_all(
                self.db, filter_params.skip, filter_params.limit
            )
            total_count = PracticeSessionRepository.count_sessions(
                self.db, filter_params.shooter_id
            )

        page = (filter_params.skip // filter_params.limit) + 1
        pages = math.ceil(total_count / filter_params.limit) if total_count > 0 else 1

        items = [
            IndividualPracticeSessionDetailLite.model_validate(session)
            for session in sessions
        ]

        return IndividualPracticeSessionList(
            items=items,
            total=total_count,
            page=page,
            size=filter_params.limit,
            pages=pages,
        )

    def update_session(
        self, session_id: UUID, session_data: IndividualPracticeSessionUpdate
    ):
        try:
            existing_session = PracticeSessionRepository.get_by_id(self.db, session_id)
            if not existing_session:
                return None, "PRACTICE_SESSION_NOT_FOUND"

            # verificar que el instructor existe si se proporciona
            if session_data.instructor_id:
                instructor = UserRepository.get_by_id(
                    self.db, session_data.instructor_id
                )
                if not instructor:
                    return None, "INSTRUCTOR_NOT_FOUND"

            # preparar los datos
            session_dict = session_data.model_dump(
                exclude_unset=True, exclude_none=True
            )

            # recalcula el porcentaje de precision si se actualizan los disparos o aciertos
            if "total_shots_fired" in session_dict or "total_hits" in session_dict:
                total_shots = session_dict.get(
                    "total_shots_fired", existing_session.total_shots_fired
                )
                total_hits = session_dict.get("total_hits", existing_session.total_hits)

                if total_shots > 0:
                    session_dict["accuracy_percentage"] = (
                        total_hits / total_shots
                    ) * 100
                else:
                    session_dict["accuracy_percentage"] = 0.0
            # actualiza la sesion
            updated_session = PracticeSessionRepository.update(
                self.db, session_id, session_dict
            )

            if not updated_session:
                return None, "ERROR_UPDATING_PRACTICE_SESSION"
            return IndividualPracticeSessionRead.model_validate(updated_session), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPDATING_PRACTICE_SESSION: {str(e)}"

    def delete_session(self, session_id: UUID) -> Tuple[bool, Optional[str]]:
        try:
            existing_session = PracticeSessionRepository.get_by_id(self.db, session_id)
            if not existing_session:
                return False, "PRACTICE_SESSION_NOT_FOUND"

            success = PracticeSessionRepository.delete(self.db, session_id)

            if not success:
                return False, "ERROR_DELETING_PRACTICE_SESSION"

            return True, None
        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_DELETING_PRACTICE_SESSION: {str(e)}"

    def get_shooter_statistics(
        self, shooter_id: UUID, period: Optional[str] = None
    ) -> Tuple[Optional[IndividualPracticeSessionStatistics], Optional[str]]:
        try:
            # Verifica que el tirador existe
            shooter = ShooterRepository.get_by_id(self.db, shooter_id)
            if not shooter:
                return None, "SHOOTER_NOT_FOUND"

            # Valida el período si se proporciona
            if period and period not in ["week", "month", "year"]:
                return None, "INVALID_PERIOD"

            # Obtiene estadísticas
            stats = PracticeSessionRepository.get_statistics(
                self.db, shooter_id, period
            )

            # Convierte al esquema de estadísticas
            return (
                IndividualPracticeSessionStatistics(
                    total_sessions=stats["total_sessions"],
                    avg_accuracy=stats["avg_accuracy"],
                    total_shots=stats["total_shots"],
                    total_hits=stats["total_hits"],
                    hit_percentage=stats["hit_percentage"],
                    period=stats["period"],
                    shooter_id=shooter_id,
                ),
                None,
            )
        except Exception as e:
            return None, f"ERROR_GETTING_STATISTICS: {str(e)}"

    def get_recent_sessions(
        self, shooter_id: Optional[UUID] = None, limit: int = 5
    ) -> List[IndividualPracticeSessionDetailLite]:
        if shooter_id:
            sessions = PracticeSessionRepository.get_by_shooter(
                self.db, shooter_id, 0, limit
            )
        else:
            sessions = PracticeSessionRepository.get_all(self.db, 0, limit)
        return [
            IndividualPracticeSessionDetailLite.model_validate(session)
            for session in sessions
        ]

    def get_my_sessions(
        self,
        user_id: UUID,
        is_finished: Optional[bool] = None,
        skip: int = 0,
        limit: int = 5,
    ) -> List[MyPracticeSessionSummary]:
        sessions = PracticeSessionRepository.get_user_sessions(
            self.db, user_id, is_finished, skip=skip, limit=limit
        )
        eval_service = PracticeEvaluationService(self.db)
        result = []
        for session in sessions:
            exercises = [
                PracticeExerciseSummary(
                    id=ex.id,
                    exercise_type_name=(
                        ex.exercise_type.name if ex.exercise_type else None
                    ),
                    hits=ex.hits,
                    accuracy_percentage=ex.accuracy_percentage,
                    has_image=ex.target_image_id is not None,
                )
                for ex in session.exercises
            ]
            evaluation = eval_service.get_by_session_id(session.id)
            evaluation_info = None
            if evaluation:
                evaluation_info = {
                    "id": evaluation.id,
                    "final_score": evaluation.final_score,
                    "classification": eval_service.get_classification_value(
                        evaluation.classification
                    ),
                }
            result.append(
                MyPracticeSessionSummary(
                    id=session.id,
                    date=session.date,
                    location=session.location,
                    is_finished=session.is_finished,
                    evaluation_pending=session.evaluation_pending,
                    total_shots_fired=session.total_shots_fired,
                    total_hits=session.total_hits,
                    accuracy_percentage=session.accuracy_percentage,
                    exercises=exercises,
                    evaluation=evaluation_info,
                )
            )
        return result
