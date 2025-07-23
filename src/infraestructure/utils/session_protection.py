from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from functools import wraps
from typing import Callable, Any

from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository,
)
from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository,
)
from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository,
)


class SessionProtectionMixin:
    """
    Mixin para agregar validaciones a servicios
    """

    def __init__(self, db: Session):
        self.db = db
        self.practice_session_repo = PracticeSessionRepository()
        self.practice_exercise_repo = PracticeExerciseRepository()

    def validate_session_not_finished(self, session_id: UUID):
        """
        valida que una sesion no este finalizada
        lanza una HTTPException si la sesion esta finalizada

        """
        session = self.practice_session_repo.get_by_id(self.db, session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        if session.is_finished:
            raise HTTPException(
                status_code=400, detail="No se puede modificar una sesión finalizada"
            )
        return session

    def validate_exercise_session_not_finished(self, exercise_id: UUID):
        """
        valida que un ejercicio no este finalizado
        lanza una HTTPException si el ejercicio esta finalizado

        """
        exercise = self.practice_exercise_repo.get_with_relations(
            self.db, exercise_id=exercise_id, relations=["session"]
        )

        if not exercise:
            raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

        if not exercise.session:
            raise HTTPException(
                status_code=404, detail="Sesión del ejercicio no encontrada"
            )
        if exercise.session.is_finished:
            raise HTTPException(
                status_code=400,
                detail="No se puede modificar un ejercicio de una sesión finalizada",
            )

        return exercise


# Decorador para métodos que requieren sesión no finalizada
def require_session_not_finished(get_session_id_func: Callable):
    """
    Decorador que valida que la sesión no esté finalizada antes de ejecutar el método

    Args:
        get_session_id_func: Función que extrae el session_id de los argumentos del método
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Extraer session_id usando la función proporcionada
            session_id = get_session_id_func(*args, **kwargs)

            # Validar que la sesión no esté finalizada
            session_repo = PracticeSessionRepository()
            if not session_repo.can_modify_session(self.db, session_id):
                raise HTTPException(
                    status_code=400,
                    detail="No se puede modificar una sesión finalizada",
                )

            # Ejecutar el método original
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


# Funciones de utilidad standalone
def check_session_not_finished(db: Session, session_id: UUID) -> bool:
    session_repo = PracticeSessionRepository()
    return session_repo.can_modify_session(db, session_id)


def get_session_from_exercise(db: Session, exercise_id: UUID) -> UUID:
    exercise_repo = PracticeExerciseRepository()
    exercise = exercise_repo.get_with_relations(db, exercise_id, relations=["session"])

    if not exercise or not exercise.session:
        raise HTTPException(status_code=404, detail="Ejercicio o sesión no encontrada")
    return exercise.session.id


def validate_exercise_modification_allowed(db: Session, exercise_id: UUID):
    """valida que se pueda modificar un ejercicio (que su sesion no este finalizada)"""
    session_id = get_session_from_exercise(db, exercise_id=exercise_id)
    if not check_session_not_finished(db, session_id):
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar un ejercicio de una sesión finalizada",
        )
