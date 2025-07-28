from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Dict, Any


@dataclass
class TargetAnalysisCompletedEvent:
    """Evento que se dispara cuando se completa un analisis"""

    exercise_id: UUID
    analysis_id: UUID
    total_score: int
    accuracy_percentage: float
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class HighScoreAchievedEvent:
    """Evento cuando se logra una puntuación alta"""

    exercise_id: UUID
    shooter_id: UUID
    score: int
    accuracy: float
    is_personal_best: bool
    timestamp: datetime
