from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID


class SessionEvaluationStatus(BaseModel):
    session_id: str
    date: datetime
    location: str
    total_shots: int
    accuracy: float
    total_score: int
    instructor_id: Optional[str] = None
    instructor_name: Optional[str] = None
    evaluation_status: str  # "evaluated", "pending", "no_instructor"
    evaluation_pending: bool
    exercises_count: int
    finalization_date: datetime
    evaluation: Optional[Dict[str, Any]] = None


class SessionsWithEvaluationResponse(BaseModel):
    sessions: List[SessionEvaluationStatus]
    total_sessions: int
    counts: Dict[str, int]
    shooter_id: str


class EvaluationDetailResponse(BaseModel):
    evaluation_id: str
    session_info: Dict[str, Any]
    instructor_info: Dict[str, Any]
    evaluation_scores: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    feedback: Dict[str, Any]
    issue_analysis: Dict[str, Any]
    evaluation_metadata: Dict[str, Any]


class EvaluationSummaryResponse(BaseModel):
    total_evaluations: int
    average_score: float
    latest_evaluation: Optional[Dict[str, Any]]
    score_trend: float
    evaluations_by_instructor: Dict[str, Any]
    score_distribution: Dict[str, int]
