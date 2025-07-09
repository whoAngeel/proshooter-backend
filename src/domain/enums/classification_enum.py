from enum import Enum
class ShooterClassification(Enum):
    EXPERTO = "TE" # Tirador Experto
    CONFIABLE = "TC" # Tirador Confiable
    MEDIO = "TM" # Tirador Medio
    REGULAR = "TR" # Tirador Regular

class ShooterLevelEnum(Enum):
    EXPERTO = "Tirador Experto" # Tirador Experto
    CONFIABLE = "Tirador Confiable" # Tirador Confiable
    MEDIO = "Tirador Medio" # Tirador Medio
    REGULAR = "Tirador Regular" # Tirador Regular

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, value):
        for level in cls:
            if level.value == value:
                return level
        return ValueError(f"'{value}' no es un nivel de tirador valido")
