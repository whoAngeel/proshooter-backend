from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


@dataclass
class ShotCoordinate:
    """Coordenada de un disparo en píxeles"""

    x: float
    y: float
    confidence: float


@dataclass
class TargetZone:
    """Zona de puntuación en el blanco"""

    score: int
    radius_ratio: float  # Ratio del radio respecto al tamaño de la imagen


@dataclass
class ShotScore:
    """Puntuación de un disparo individual"""

    coordinates: ShotCoordinate
    score: int
    zone: str
    distance_from_center_pixels: float
    distance_from_center_ratio: float


@dataclass
class GroupStatistics:
    """Estadísticas del grupo de tiro"""

    center_x: float
    center_y: float
    diameter: float
    average_distance_from_center: float
    std_deviation: float
    shots_count: int
