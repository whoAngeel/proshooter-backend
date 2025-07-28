from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime

from src.domain.entities.scoring import ShotScore, GroupStatistics
from src.domain.value_objects.target_config import TargetType


class TargetAnalysisAggregate:
    """
    Agregado que encapsula toda la informacion de un analisis de blanco
    """

    # Identificación
    exercise_id: UUID
    target_image_id: UUID
    analysis_timestamp: datetime

    # Detecciones básicas (existentes)
    total_impacts_detected: int
    fresh_impacts_inside: int
    fresh_impacts_outside: int
    covered_impacts_inside: int
    covered_impacts_outside: int
    accuracy_percentage: float
    average_confidence: float

    # Puntuación (nuevos)
    shot_scores: List[ShotScore]
    total_score: int
    average_score_per_shot: float
    max_score_achieved: int
    score_distribution: Dict[str, int]

    # Agrupamiento (nuevos)
    group_statistics: Optional[GroupStatistics]

    # Metadatos
    target_type: TargetType
    model_version: str
    confidence_threshold: float

    @property
    def fresh_shots_count(self) -> int:
        """Total de disparos frescos"""
        return self.fresh_impacts_inside + self.fresh_impacts_outside

    @property
    def score_efficiency_percentage(self) -> float:
        """Eficiencia de puntuación vs máximo posible"""
        if self.fresh_shots_count == 0:
            return 0.0
        max_possible = self.fresh_shots_count * 10  # 10 puntos máximo
        return (self.total_score / max_possible) * 100

    @property
    def has_scoring_data(self) -> bool:
        """Indica si tiene datos de puntuación calculados"""
        return len(self.shot_scores) > 0

    def get_shots_in_zone(self, zone_score: int) -> List[ShotScore]:
        """Obtiene disparos en una zona específica"""
        return [shot for shot in self.shot_scores if shot.score == zone_score]

    def calculate_summary_stats(self) -> Dict[str, Any]:
        """Calcula estadísticas resumidas"""
        return {
            "total_score": self.total_score,
            "fresh_shots": self.fresh_shots_count,
            "average_score": self.average_score_per_shot,
            "accuracy": self.accuracy_percentage,
            "score_efficiency": self.score_efficiency_percentage,
            "group_diameter": (
                self.group_statistics.diameter if self.group_statistics else None
            ),
            "best_shot_score": self.max_score_achieved,
        }
