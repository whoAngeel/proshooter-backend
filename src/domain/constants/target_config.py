class TargetConfiguration:
    """Configuración para diferentes tipos de blancos"""

    PRO_SHOOTER_CONFIG = {
        "name": "PRO-SHOOTER",
        "center_x_ratio": 0.5,  # Centro en 50% del ancho
        "center_y_ratio": 0.5,  # Centro en 50% del alto
        "zones": [
            {"score": 10, "radius_ratio": 0.045},  # Zona roja central (10 puntos)
            {"score": 9, "radius_ratio": 0.090},  # Primera zona verde
            {"score": 8, "radius_ratio": 0.135},  # Zona 8
            {"score": 7, "radius_ratio": 0.180},  # Zona 7
            {"score": 6, "radius_ratio": 0.225},  # Zona 6
            {"score": 5, "radius_ratio": 0.270},  # Zona 5
            {"score": 4, "radius_ratio": 0.315},  # Zona 4
            {"score": 3, "radius_ratio": 0.360},  # Zona 3
            {"score": 2, "radius_ratio": 0.405},  # Zona 2
            {"score": 1, "radius_ratio": 0.450},  # Zona 1 (borde exterior)
        ],
    }
