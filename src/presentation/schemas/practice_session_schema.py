from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator

class ShooterInfo(BaseModel):
    user_id: UUID

    range: Optional[str]
    user: Optional["UserReadLite"]
    model_config = {"from_attributes": True}

class InstructorInfo(BaseModel):
    id: UUID
    personal_data: Optional["UserPersonalDataReadLite"]
    # full_name: str
    model_config = {"from_attributes" : True}

class PracticeExerciseBase(BaseModel):
    session_id: UUID
    exercise_type_id: UUID
    target_id: UUID
    weapon_id: UUID
    ammunition_id: UUID
    distance: str
    firing_cadence: Optional[str] = None
    time_limit: Optional[str] = None
    ammunition_allocated: int = 0
    ammunition_used: int = 0
    hits: int = 0
    reaction_time: Optional[float] = None

class PracticeExerciseRead(PracticeExerciseBase):
    id: UUID
    accuracy_percentage: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class EvaluationInfo(BaseModel):
    id: UUID
    final_score: float
    classification: str

class IndividualPracticeSessionBase(BaseModel):
    # shooter_id: UUID
    instructor_id: Optional[UUID] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    location: str
    total_shots_fired: int = 0
    total_hits: int = 0


class IndividualPracticeSessionCreate(IndividualPracticeSessionBase):
    # shooter_id: UUID
    @model_validator(mode='after')
    def validate_hits_not_greater_than_shots(self) -> 'IndividualPracticeSessionCreate':
        if self.total_hits > self.total_shots_fired:
            raise ValueError('Total hits cannot be greater than total shots fired')
        return self

class IndividualPracticeSessionUpdate(BaseModel):
    instructor_id: Optional[UUID] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    total_shots_fired: Optional[int] = None
    total_hits: Optional[int] = None

    @model_validator(mode='after')
    def validate_hits_not_greater_than_shots(self) -> 'IndividualPracticeSessionUpdate':
        if (self.total_hits is not None and self.total_shots_fired is not None and
                self.total_hits > self.total_shots_fired):
            raise ValueError('Total hits cannot be greater than total shots fired')
        return self

class IndividualPracticeSessionRead(IndividualPracticeSessionBase):
    id: UUID
    accuracy_percentage: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class IndividualPracticeSessionDetail(BaseModel):
    shooter_id: UUID
    instructor_id: Optional[UUID] = None
    date: datetime
    location: str
    total_shots_fired: int = 0
    total_hits: int = 0

    id: UUID
    accuracy_percentage: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    shooter: Optional[ShooterInfo] = None
    instructor: Optional[InstructorInfo] = None
    exercises: Optional[List[PracticeExerciseRead]] = None
    evaluation: Optional[EvaluationInfo] = None

    model_config = {"from_attributes": True}

class IndividualPracticeSessionDetailLite(BaseModel):

    date: datetime = Field(default_factory=datetime.now())
    location: str
    total_shots_fired: int = 0
    total_hits: int = 0

    id: UUID
    accuracy_percentage: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    shooter: Optional[ShooterInfo] = None
    instructor: Optional[InstructorInfo] = None

    model_config = {"from_attributes": True}

class IndividualPracticeSessionList(BaseModel):
    # items: List[IndividualPracticeSessionRead]
    items: List[IndividualPracticeSessionDetailLite]
    total: int
    page: int
    size: int
    pages: int

class IndividualPracticeSessionFilter(BaseModel):
    shooter_id: Optional[UUID] = None
    instructor_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_accuracy: Optional[float] = None
    max_accuracy: Optional[float] = None
    search: Optional[str] = None
    skip: int = 0
    limit: int = 100


class IndividualPracticeSessionStatistics(BaseModel):
    total_sessions: int
    avg_accuracy: float
    total_shots: int
    total_hits: int
    hit_percentage: float
    period: str
    shooter_id: UUID


from .user_schemas import UserReadLite, UserPersonalDataReadLite
UserReadLite.model_rebuild()
