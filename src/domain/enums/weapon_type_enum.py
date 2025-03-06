from enum import Enum

class WeaponTypeEnum(Enum):
    PISTOL = "Pistola"
    RIFLE = "Rifle"
    REVOLVER = "Revolver"
    SHOTGUN = "Escopeta"
    CARBINE = "Carabina"
    SMG = "Subametralladora"
    SNIPER_RIFLE = "Rifle de precisión"
    OTHER = "Otro"

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, value):
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"'{value}' no es un tipo de arma valido")
