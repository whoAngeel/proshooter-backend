from enum import Enum

class TargetType(str, Enum):
    CONCENTRIC = "Concéntrico"
    IPSC = "IPSC"

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, value):
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"'{value}' no es un tipo de objetivo valido")
