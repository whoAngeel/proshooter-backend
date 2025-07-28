from src.domain.entities.scoring import TargetZone
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class TargetType(Enum):
    """Tipos de blancos soportados"""

    PRO_SHOOTER = "PRO_SHOOTER"
    IPSC = "IPSC"
    ISSF = "ISSF"


@dataclass
class TargetConfiguration:
    """Configuración de un tipo de blanco"""

    name: str
    type: TargetType
    center_x_ratio: float  # 0.5 = centro de la imagen
    center_y_ratio: float  # 0.5 = centro de la imagen
    zones: List[TargetZone]

    def get_zone_by_score(self, score: int) -> Optional[TargetZone]:
        """Obtiene zona por puntuación"""
        return next((zone for zone in self.zones if zone.score == score), None)

    def get_max_score(self) -> int:
        """Puntuación máxima posible"""
        return max(zone.score for zone in self.zones) if self.zones else 0


class TargetConfigurations:
    """Configuraciones predefinidas de blancos"""

    PRO_SHOOTER = TargetConfiguration(
        name="PRO-SHOOTER",
        type=TargetType.PRO_SHOOTER,
        center_x_ratio=0.5,
        center_y_ratio=0.5,
        zones=[
            TargetZone(score=10, radius_ratio=0.045),  # Centro rojo
            TargetZone(score=9, radius_ratio=0.090),  # Primera zona verde
            TargetZone(score=8, radius_ratio=0.135),  # Zona 8
            TargetZone(score=7, radius_ratio=0.180),  # Zona 7
            TargetZone(score=6, radius_ratio=0.225),  # Zona 6
            TargetZone(score=5, radius_ratio=0.270),  # Zona 5
            TargetZone(score=4, radius_ratio=0.315),  # Zona 4
            TargetZone(score=3, radius_ratio=0.360),  # Zona 3
            TargetZone(score=2, radius_ratio=0.405),  # Zona 2
            TargetZone(score=1, radius_ratio=0.450),  # Zona 1 (borde)
        ],
    )

    @classmethod
    def get_config(cls, target_type: TargetType) -> TargetConfiguration:
        """Obtiene configuración por tipo"""
        configs = {
            TargetType.PRO_SHOOTER: cls.PRO_SHOOTER,
            # Agregar más configuraciones aquí
        }
        return configs.get(target_type, cls.PRO_SHOOTER)
