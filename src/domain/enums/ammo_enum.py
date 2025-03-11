from enum import Enum

class AmmoType(str, Enum):
    STANDARD = "Estándar"
    COMPETITION = "Competición"
    PRACTICE = "Práctica"
    MATCH = "Match"
    HOLLOW_POINT = "Punta hueca"
    FULL_METAL_JACKET = "Encamisada"
    SUBSONIC = "Subsónica"
    OTHER = "Otro"

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, value):
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"'{value}' no es un tipo de munición valido")
