# Constantes para puntuaciones IPSC
class IPSCScoring:
    """
    Constantes para puntuaciones en blancos IPSC.

    Estas constantes definen los valores de puntuación para las
    diferentes zonas en los blancos IPSC.
    """
    ZONE_A = 5  # Zona A (Alpha)
    ZONE_C = 3  # Zona C (Charlie)
    ZONE_D = 1  # Zona D (Delta)
    NO_SHOOT = -10  # Penalización por impactar un 'No-Shoot'


# Constantes para puntuaciones en blancos concéntricos
class ConcentricScoring:
    """
    Constantes para puntuaciones en blancos concéntricos.

    Define los valores típicos para los anillos en blancos
    de competición estándar.
    """
    CENTER_X = 10  # Centro X (diez interior)
    CENTER_10 = 10  # Centro (diez)
    RING_9 = 9
    RING_8 = 8
    RING_7 = 7
    RING_6 = 6
    RING_5 = 5
    RING_4 = 4
    RING_3 = 3
    RING_2 = 2
    RING_1 = 1
    MISS = 0
