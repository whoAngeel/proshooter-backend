from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from uuid import UUID
import math

from src.infraestructure.database.repositories.exercise_type_repo import ExerciseTypeRepository
from src.infraestructure.database.models.exercise_type_model import ExerciseTypeModel
from src.infraestructure.database.session import get_db
from src.presentation.schemas.exercise_type_schema import (
    ExerciseTypeCreate,
    ExerciseTypeUpdate,
    ExerciseTypeDetail,
    ExerciseTypeList,
    ExerciseTypeFilter,
    ExerciseTypeRead,
)

class ExerciseTypeService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_exercise_type(self, exercise_type_data: ExerciseTypeCreate) -> Tuple[Optional[ExerciseTypeRead], Optional[str]]:
        try:
            # Verificar si el tipo de ejercicio ya existe
            existing = self.db.query(ExerciseTypeModel).filter_by(
                name = exercise_type_data.name
            ).first()

            if existing:
                return None, "EXERCISE_TYPE_NAME_ALREADY_EXISTS"

            # preparar lso datos para la creacion
            exercise_type_dict = exercise_type_data.model_dump()

            new_exercise_type = ExerciseTypeRepository.create(self.db, exercise_type_dict)

            return ExerciseTypeRead.model_validate(new_exercise_type), None
        except Exception as e:
            self.db.rollback()
            print(f"Error creating exercise type: {e}")
            return None, f"EXERCISE_TYPE_CREATION_FAILED: {str(e)}"

    def get_exercise_type_by_id(self, exercise_type_id: UUID) -> Tuple[Optional[ExerciseTypeRead], Optional[str]]:

        exercise_type = ExerciseTypeRepository.get_by_id(self.db, exercise_type_id)
        if not exercise_type:
            return None, "EXERCISE_TYPE_NOT_FOUND"
        return ExerciseTypeRead.model_validate(exercise_type), None


    def get_exercise_type_detail(self, exercise_type_id: UUID) -> Tuple[Optional[ExerciseTypeDetail], Optional[str]]:
        exercise_type = ExerciseTypeRepository.get_by_id(self.db, exercise_type_id)
        if not exercise_type:
            return None, "EXERCISE_TYPE_NOT_FOUND"

        exercises_count = len(ExerciseTypeRepository.get_exercises_by_type(self.db, exercise_type_id))

        exercise_type_dict = ExerciseTypeRead.model_validate(exercise_type).model_dump()
        exercise_type_dict["exercises_count"] = exercises_count

        return ExerciseTypeDetail(**exercise_type_dict), None

    def get_all_exercise_types(self, filter_params: ExerciseTypeFilter)->ExerciseTypeList:
        if filter_params.search:
            exercise_types = ExerciseTypeRepository.search_by_term(self.db, filter_params.search)
        elif filter_params.difficulty is not None:
            exercise_types = ExerciseTypeRepository.get_by_difficulty(self.db, filter_params.difficulty)
        else:
            exercise_types = ExerciseTypeRepository.get_all(
                self.db,
                skip=filter_params.skip,
                limit=filter_params.limit,
                active_only=filter_params.active_only
            )

        if filter_params.search:
            total = len(exercise_types)
        elif filter_params.difficulty is not None:
            total = len(exercise_types)
        else:
            query = self.db.query(ExerciseTypeModel)
            if filter_params.active_only:
                query = query.filter(ExerciseTypeModel.is_active == True)
            total = query.count()

        page = (filter_params.skip // filter_params.limit) + 1
        pages = math.ceil(total / filter_params.limit) if total > 0 else 1

        items = [ExerciseTypeRead.model_validate(exercise_type) for exercise_type in exercise_types]

        return ExerciseTypeList(
            items=items,
            total=total,
            page=page,
            size=filter_params.limit,
            pages=pages
        )

    def update_exercise_type(
        self,
        exercise_type_id: UUID,
        exercise_type_data: ExerciseTypeUpdate
    ) -> Tuple[Optional[ExerciseTypeRead], Optional[str]]:
        try:
            existing_exercise_type = ExerciseTypeRepository.get_by_id(self.db, exercise_type_id)
            if not existing_exercise_type:
                return None, "EXERCISE_TYPE_NOT_FOUND"

            # verificar si hay un cambio de nombre y si ya existe otro con ese nombre
            if exercise_type_data and exercise_type_data != existing_exercise_type.name:
                name_exists = self.db.query(ExerciseTypeModel).filter_by(
                    name = exercise_type_data.name
                ).filter(ExerciseTypeModel.id != exercise_type_id).first()
                if name_exists:
                    return None, "EXERCISE_TYPE_NAME_ALREADY_EXISTS"
            # preparar los datos para actualizar
            exercise_type_dict = exercise_type_data.model_dump(exclude_unset=True, exclude_none=True)

            # actualizar el tipo de ejercicio
            updated_exercise_type = ExerciseTypeRepository.update(self.db, exercise_type_id, exercise_type_dict)
            return ExerciseTypeRead.model_validate(updated_exercise_type), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPDATING_EXERCISE_TYPE: {str(e)}"

    def delete_exercise_type(self, exercise_type_id: UUID, soft_delete: bool = True) -> Tuple[bool, Optional[str]]:
        try:
            existing_exercise_type = ExerciseTypeRepository.get_by_id(self.db, exercise_type_id)
            if not existing_exercise_type:
                return False, "EXERCISE_TYPE_NOT_FOUND"

            # verificar si tiene ejercicios asociados
            exercises = ExerciseTypeRepository.get_exercises_by_type(self.db, exercise_type_id)
            if exercises and not soft_delete:
                return False, "CANNOT_DELETE_EXERCISE_TYPE_WITH_ASSOCIATED_EXERCISES"

            if soft_delete:
                success = ExerciseTypeRepository.desactivate(self.db, exercise_type_id)
            else:
                success = ExerciseTypeRepository.delete(self.db, exercise_type_id)

            if not success:
                return False, "ERROR_DELETING_EXERCISE_TYPE"
            return True, None
        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_DELETING_EXERCISE_TYPE: {str(e)}"
    def get_exercises_by_type(self, exercise_type_id: UUID) -> Tuple[Optional[List], Optional[str]]:
        """
        Obtiene los ejercicios asociados a un tipo específico.

        Args:
            exercise_type_id: UUID del tipo de ejercicio

        Returns:
            Tupla con la lista de ejercicios (o None) y un mensaje de error (o None)
        """
        # Verificar que el tipo de ejercicio existe
        exercise_type = ExerciseTypeRepository.get_by_id(self.db, exercise_type_id)
        if not exercise_type:
            return None, "EXERCISE_TYPE_NOT_FOUND"

        # Obtener los ejercicios asociados
        exercises = ExerciseTypeRepository.get_exercises_by_type(self.db, exercise_type_id)
        #  TODO:

        # Aquí normalmente mappearíamos los ejercicios a un esquema, pero no tenemos definido el esquema
        # para los ejercicios en este momento. Se podría retornar directamente la lista de modelos.
        return exercises, None
