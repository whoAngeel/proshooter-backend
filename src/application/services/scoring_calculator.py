import math
import numpy as np
from typing import List, Tuple, Dict
from src.domain.entities.scoring import (
    ShotCoordinate,
    ShotScore,
    GroupStatistics,
    TargetConfiguration,
)


class ScoringCalculatorService:
    def __init__(self, target_config: TargetConfiguration):
        self.target_config = target_config

    def calculate_shot_score(
        self, shot_coordinate: ShotCoordinate, image_width: int, image_height: int
    ) -> ShotScore:
        """
        Calcula la puntuación de un disparo individual

        Args:
            shot_coordinate: Coordenadas del impacto
            image_width: Ancho de la imagen en píxeles
            image_height: Alto de la imagen en píxeles

        Returns:
            ShotScore con la puntuación y zona correspondiente
        """
        # Calcular centro del blanco en píxeles
        center_x = image_width * self.config.center_x_ratio
        center_y = image_height * self.config.center_y_ratio

        # Calcular distancia euclidiana al centro
        distance_pixels = math.sqrt(
            (shot_coordinate.x - center_x) ** 2 + (shot_coordinate.y - center_y) ** 2
        )

        # Normalizar distancia usando el menor de las dimensiones
        image_size = min(image_width, image_height)
        distance_ratio = distance_pixels / (image_size / 2)

        # Determinar zona y puntuación
        score = 0
        zone = "outside"

        # Buscar en qué zona cae el disparo (de mayor a menor puntuación)
        sorted_zones = sorted(self.config.zones, key=lambda z: z.radius_ratio)

        for zone_info in sorted_zones:
            if distance_ratio <= zone_info.radius_ratio:
                score = zone_info.score
                zone = f"zone_{score}"
                break

        return ShotScore(
            coordinates=shot_coordinate,
            score=score,
            zone=zone,
            distance_from_center_pixels=distance_pixels,
            distance_from_center_ratio=distance_ratio,
        )

    def calculate_multiple_shots_score(
        self,
        shot_coordinates: List[ShotCoordinate],
        image_width: int,
        image_height: int,
    ) -> Tuple[List[ShotScore], Dict[str, int]]:
        """calcula puntuaciones para multples disparos


        Args:
            shot_coordinates (List[ShotCoordinate]): _description_
            image_width (int): _description_
            image_height (int): _description_

        Returns:
            Tuple[List[ShotScore], Dict[str, int]]: _description_
        """
        shot_scores = []
        score_distribution = {str(i): 0 for i in range(0, 11)}  # 0-10 puntos
        for coordinate in shot_coordinates:
            shot_score = self.calculate_shot_score(
                coordinate, image_width, image_height
            )
            shot_scores.append(shot_score)
            score_distribution[str(shot_score.score)] += 1

        return shot_scores, score_distribution

    def calculate_group_statistics(
        self, shot_scores: List[ShotScore]
    ) -> GroupStatistics:
        if not shot_scores:
            return GroupStatistics(
                center_x=0.0,
                center_y=0.0,
                diameter=0.0,
                average_distance_from_center=0.0,
                std_deviation=0.0,
                shots_count=0,
            )
        # extraer coordenadas
        x_coords = [shot.coordinates.x for shot in shot_scores]
        y_coords = [shot.coordinates.y for shot in shot_scores]

        # centro del grupo (centroide)
        group_center_x = np.mean(x_coords)
        group_center_y = np.mean(y_coords)

        # calcular diametro del grupo (maxima distancia entre disparos)
        max_distance = 0.0
        for i in range(len(shot_scores)):
            for j in range(i + 1, len(shot_scores)):
                dist = math.sqrt(
                    (x_coords[i] - x_coords[j]) ** 2 + (y_coords[i] - y_coords[j]) ** 2
                )
                max_distance = max(max_distance, dist)

        # calcular dispercion desde el centro del grupo
        distances_from_group_center = [
            math.sqrt((x - group_center_x) ** 2 * (y - group_center_y) ** 2)
            for x, y in zip(x_coords, y_coords)
        ]
        avg_distance = np.mean(distances_from_group_center)
        std_dev = np.std(distances_from_group_center)
        return GroupStatistics(
            center_x=group_center_x,
            center_y=group_center_y,
            diameter=max_distance,
            average_distance_from_center=avg_distance,
            std_deviation=std_dev,
            shots_count=len(shot_scores),
        )
