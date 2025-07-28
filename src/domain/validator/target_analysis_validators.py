from typing import List, Tuple, Optional
from src.domain.entities.scoring import ShotCoordinate
from src.domain.value_objects.target_config import TargetConfiguration


class TargetAnalysisValidator:

    @staticmethod
    def validate_shot_coordinates(
        coordinates: List[ShotCoordinate], image_width: int, image_height: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida que las coordenadas de disparo estén dentro de los límites de la imagen.

        Args:
            coordinates: Lista de ShotCoordinate a validar.
            image_width: Ancho de la imagen en píxeles.
            image_height: Alto de la imagen en píxeles.

        Returns:
            Tuple con un booleano indicando si es válido y un mensaje opcional.
        """
        for i, coord in enumerate(coordinates):
            if coord.x < 0 or coord.x > image_width:
                return (
                    False,
                    f"Coordenada X fuera del disparo [{i}] fuera de rango: {coord.x}",
                )
            if coord.y < 0 or coord.y > image_height:
                return (
                    False,
                    f"Coordenada Y fuera del disparo [{i}] fuera de rango: {coord.y}",
                )
            if coord.confidence < 0 or coord.confidence > 1:
                return (
                    False,
                    f"Confianza fuera de rango en disparo [{i}]: {coord.confidence}",
                )
        return True, None

    @staticmethod
    def validate_target_configuration(
        config: TargetConfiguration,
    ) -> Tuple[bool, Optional[str]]:
        """Valida configuarion de blanco"""
        if not (0 <= config.center_x_ratio <= 1):
            return (
                False,
                f"center_x_ratio debe estar entre 0 y 1: {config.center_x_ratio}",
            )
        if not (0 <= config.center_y_ratio <= 1):
            return (
                False,
                f"center_y_ratio debe estar entre 0 y 1: {config.center_y_ratio}",
            )
        if not config.zones:
            return False, "Configuración de zonas no puede estar vacía"

        prev_radius = 0
        for zone in sorted(config.zones, key=lambda z: z.radius_ratio):
            if zone.radius_ratio <= prev_radius:
                return (
                    False,
                    f"Las zonas deben tener radios crecientes. Zona {zone.score} tiene radio {zone.radius_ratio}",
                )
            prev_radius = zone.radius_ratio

        return True, None

    @staticmethod
    def validate_image_format(
        image_width: int, image_height: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida que las dimensiones de la imagen sean positivas.

        Args:
            image_width: Ancho de la imagen en píxeles.
            image_height: Alto de la imagen en píxeles.

        Returns:
            Tuple con un booleano indicando si es válido y un mensaje opcional.
        """
        if image_width != image_height:
            return (
                False,
                f"La imagen debe ser cuadrada (1:1). Actual: {image_width}x{image_height}",
            )
        if image_width < 256:  # tamaño mínimo recomendado
            return (
                False,
                f"El ancho de la imagen debe ser al menos 256x256 píxeles. Actual: {image_width}x{image_height}",
            )
        return True, None
