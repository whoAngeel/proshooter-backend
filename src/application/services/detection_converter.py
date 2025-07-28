from typing import List, Dict, Any
from src.domain.entities.scoring import ShotCoordinate


class DetectionConverter:
    """convierte detecciones del ML a entidades de dominio"""

    @staticmethod
    def detections_to_shot_coordinates(
        detections: List[Dict[str, Any]], only_fresh: bool = True
    ) -> List[ShotCoordinate]:
        """
        Convierte una lista de detecciones a coordenadas de disparo.

        Args:
            detections: Lista de detecciones con formato {'x': float, 'y': float, 'score': float}
            only_fresh: Si True, filtra las detecciones para incluir solo las frescas.

        Returns:
            Lista de ShotCoordinate.
        """
        shot_coordinates = []
        for detection in detections:
            if only_fresh and detection.get("es_fresco", True) is False:
                continue
            coordinate = ShotCoordinate(
                x=float(detection.get("centro_x", 0)),
                y=float(detection.get("centro_y", 0)),
                confidence=float(detection.get("confianza", 0)),
            )
            shot_coordinates.append(coordinate)

        return shot_coordinates

    @staticmethod
    def shot_scores_to_detection_format(shot_scores: List) -> List[Dict[str, Any]]:
        """
        Convierte una lista de ShotScore a formato de detección para compatibilidad

        Args:
            shoots_scores: Lista de objetos ShotScore.

        Returns:
            Lista de diccionarios con formato
        """
        detections = []
        for shot_score in shot_scores:
            detection = {
                "centro_x": shot_score.coordinates.x,
                "centro_y": shot_score.coordinates.y,
                "confianza": shot_score.coordinates.confidence,
                "es_fresco": True,  # asumimos que son fresscos si tienen puntuacion
                "scores": shot_score.score,
                "zone": shot_score.zone,
                "distance_from_center": shot_score.distance_from_center_pixels,
                "distance_ratio": shot_score.distance_from_center_ratio,
            }
            detections.append(detection)
        return detections
