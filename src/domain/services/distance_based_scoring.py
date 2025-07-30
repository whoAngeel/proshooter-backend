import math
from typing import Tuple, Dict, Any
from src.domain.entities.scoring import ShotCoordinate, ShotScore


class DistanceBasedScoringService:
    """
    Servicio que calcula puntuación basándose únicamente en la distancia
    al centro de la imagen, sin importar las zonas del blanco físico
    """

    def __init__(self, max_distance_ratio: float = 1.0):
        """
        Args:
            max_distance_ratio: Distancia máxima para obtener puntos (1.0 = hasta el borde)
        """
        self.max_distance_ratio = max_distance_ratio

    def calculate_shot_score_by_distance(
        self,
        shot_coordinate: ShotCoordinate,
        image_width: int,
        image_height: int,
        scoring_method: str = "linear",  # "linear", "exponential", "zones"
    ) -> ShotScore:
        """
        Calcula puntuación basándose solo en distancia al centro de la imagen

        Args:
            shot_coordinate: Coordenadas del disparo
            image_width: Ancho de la imagen
            image_height: Alto de la imagen
            scoring_method: Método de cálculo ("linear", "exponential", "zones")

        Returns:
            ShotScore con puntuación basada en distancia
        """
        # Centro de la imagen (siempre 50%, 50%)
        center_x = image_width / 2
        center_y = image_height / 2

        # Calcular distancia euclidiana al centro
        distance_pixels = math.sqrt(
            (shot_coordinate.x - center_x) ** 2 + (shot_coordinate.y - center_y) ** 2
        )

        # Normalizar distancia (usar el menor de las dimensiones para mantener proporción)
        image_size = min(image_width, image_height)
        max_distance = (image_size / 2) * self.max_distance_ratio
        distance_ratio = distance_pixels / max_distance

        # Calcular puntuación según el método elegido
        if scoring_method == "linear":
            score = self._calculate_linear_score(distance_ratio)
        elif scoring_method == "exponential":
            score = self._calculate_exponential_score(distance_ratio)
        elif scoring_method == "zones":
            score = self._calculate_zone_score(distance_ratio)
        else:
            score = self._calculate_linear_score(distance_ratio)

        # Determinar zona descriptiva
        zone = self._get_zone_description(score)

        return ShotScore(
            coordinates=shot_coordinate,
            score=score,
            zone=zone,
            distance_from_center_pixels=distance_pixels,
            distance_from_center_ratio=distance_ratio,
        )

    def _calculate_linear_score(self, distance_ratio: float) -> int:
        """
        Cálculo lineal: 10 puntos en el centro, 0 puntos en el borde

        Fórmula: score = 10 * (1 - distance_ratio)
        """
        if distance_ratio >= 1.0:
            return 0

        # Puntuación lineal de 10 a 0
        score = 10 * (1 - distance_ratio)
        return max(0, int(round(score)))

    def _calculate_exponential_score(self, distance_ratio: float) -> int:
        """
        Cálculo exponencial: Más puntos cerca del centro, caída más rápida

        Fórmula: score = 10 * (1 - distance_ratio²)
        """
        if distance_ratio >= 1.0:
            return 0

        # Puntuación exponencial (curva cuadrática)
        score = 10 * (1 - distance_ratio**2)
        return max(0, int(round(score)))

    def _calculate_zone_score(self, distance_ratio: float) -> int:
        """
        Cálculo por zonas discretas (similar al blanco tradicional)
        """
        if distance_ratio >= 1.0:
            return 0

        # Definir zonas de puntuación
        zone_thresholds = [
            (0.05, 10),  # 5% del radio = 10 puntos
            (0.15, 9),  # 15% del radio = 9 puntos
            (0.25, 8),  # 25% del radio = 8 puntos
            (0.35, 7),  # 35% del radio = 7 puntos
            (0.45, 6),  # 45% del radio = 6 puntos
            (0.55, 5),  # 55% del radio = 5 puntos
            (0.65, 4),  # 65% del radio = 4 puntos
            (0.75, 3),  # 75% del radio = 3 puntos
            (0.85, 2),  # 85% del radio = 2 puntos
            (0.95, 1),  # 95% del radio = 1 punto
            (1.0, 0),  # Fuera = 0 puntos
        ]

        for threshold, score in zone_thresholds:
            if distance_ratio <= threshold:
                return score

        return 0

    def _get_zone_description(self, score: int) -> str:
        """Devuelve descripción de la zona según la puntuación"""
        zone_descriptions = {
            10: "bullseye",
            9: "inner_ring",
            8: "zone_8",
            7: "zone_7",
            6: "zone_6",
            5: "zone_5",
            4: "zone_4",
            3: "zone_3",
            2: "zone_2",
            1: "outer_ring",
            0: "outside",
        }
        return zone_descriptions.get(score, "outside")
