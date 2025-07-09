from enum import Enum
class PracticeType(Enum):
    PRECISION = "Precisión"
    REACTION = "Reacción"
    DRAW = "Desenfunde"
    RELOAD = "Cambio de cargador"
    MOVEMENT = "Tiro en movimiento"

    def __str__(self):
        return self.value

    @classmethod
    def has_value(cls, value):
        return value in [item.value for item in cls]
