from enum import Enum, auto


class RoleEnum(str, Enum):
    """
    Enumeración de roles de usuarios en el sistema.

    Al heredar de str, los valores pueden ser usados directamente como strings,
    facilitando las comparaciones y serialización.
    """
    TIRADOR = "TIRADOR"
    INSTRUCTOR = "INSTRUCTOR"
    INSTRUCTOR_JEFE = "INSTRUCTOR_JEFE"
    ADMIN = "ADMIN"

    def __str__(self):
        return self.value

    @classmethod
    def has_value(cls, value):
        """
        Verifica si un valor dado corresponde a alguno de los roles definidos.

        Args:
            value (str): Valor a verificar

        Returns:
            bool: True si el valor es un rol válido, False en caso contrario
        """
        return value in [item.value for item in cls]

    @classmethod
    def from_string(cls, value):
        """
        Obtiene el enum correspondiente a partir de una cadena.

        Args:
            value (str): Valor del rol como cadena

        Returns:
            RoleEnum: Valor del enum correspondiente

        Raises:
            ValueError: Si el valor no corresponde a ningún rol
        """
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"'{value}' no es un rol válido")

    def can_create_club(self):
        """
        Verifica si el rol tiene permiso para crear un club de tiro.

        Returns:
            bool: True si tiene permiso, False en caso contrario
        """
        return self in [RoleEnum.INSTRUCTOR_JEFE, RoleEnum.ADMIN]

    def can_manage_shooters(self):
        """
        Verifica si el rol puede gestionar tiradores.

        Returns:
            bool: True si tiene permiso, False en caso contrario
        """
        return self in [RoleEnum.INSTRUCTOR, RoleEnum.INSTRUCTOR_JEFE, RoleEnum.ADMIN]

    def can_evaluate_shooters(self):
        """
        Verifica si el rol puede evaluar tiradores.

        Returns:
            bool: True si tiene permiso, False en caso contrario
        """
        return self in [RoleEnum.INSTRUCTOR, RoleEnum.INSTRUCTOR_JEFE]
