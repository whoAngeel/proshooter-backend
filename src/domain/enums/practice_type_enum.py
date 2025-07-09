from enum import Enum

class PracticeTypeEnum(Enum):
    RAPID_FIRE = "Tiro Rápido"
    DISTANCE = "Distancia"
    PRECISION = "Precisión"

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, value):
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"'{value}' no es un tipo de tiro valido")
