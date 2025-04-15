from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.infraestructure.database.models.exercise_type_model import ExerciseTypeModel

class ExerciseTypeRepository:
    """
    Repositorio para operaciones relacionadas con los tipos de ejercicios.

    Este repositorio proporciona métodos para crear, leer, actualizar y eliminar
    tipos de ejercicios en la base de datos, así como para buscar ejercicios por diferentes criterios.
    """
    
    @staticmethod
    def create(db: Session, exercise_type_data: dict) -> ExerciseTypeModel:
        """
        Crea un nuevo tipo de ejercicio en la base de datos.

        Args:
            db (Session): Sesión de base de datos.
            exercise_type_data (dict): Datos del tipo de ejercicio a crear.

        Returns:
            ExerciseTypeModel: El tipo de ejercicio creado.
        """
        exercise_type = ExerciseTypeModel(**exercise_type_data)
        db.add(exercise_type)
        db.commit()
        db.refresh(exercise_type)
        return exercise_type
    
    @staticmethod
    def get_by_id(db: Session, exercise_type_id: UUID)-> Optional[ExerciseTypeModel]:
        return db.query(ExerciseTypeModel).filter(ExerciseTypeModel.id == exercise_type_id).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[ExerciseTypeModel]:
        query = db.query(ExerciseTypeModel)
        if active_only:
            query = query.filter(ExerciseTypeModel.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def search_by_term(db: Session, term: str)-> List[ExerciseTypeModel]:
        """
        Busca tipos de ejercicios por término en nombre o descripción.

        Args:
            db (Session): Sesión de base de datos.
            term (str): Término de búsqueda.

        Returns:
            List[ExerciseTypeModel]: Lista de tipos de ejercicios que coinciden con el término.
        """
        search_term = f"%{term}%"
        return db.query(ExerciseTypeModel).filter(
            or_(
                ExerciseTypeModel.name.ilike(search_term),
                ExerciseTypeModel.description.ilike(search_term),
                ExerciseTypeModel.objective.ilike(search_term)
            )
        ).all()
        
    @staticmethod
    def get_by_difficulty(db: Session, difficulty: int) -> List[ExerciseTypeModel]:
        return db.query(ExerciseTypeModel).filter(
            ExerciseTypeModel.difficulty == difficulty,
            ExerciseTypeModel.is_active == True
        ).all()
        
    @staticmethod
    def update(db: Session, exercise_type_id: UUID, exercise_type_data: dict) -> Optional[ExerciseTypeModel]:
        """
        Actualiza un tipo de ejercicio existente.

        Args:
            db (Session): Sesión de base de datos.
            exercise_type_id (UUID): ID del tipo de ejercicio a actualizar.
            exercise_type_data (dict): Datos a actualizar.

        Returns:
            Optional[ExerciseTypeModel]: El tipo de ejercicio actualizado o None si no existe.
        """
        exercise_type = ExerciseTypeRepository.get_by_id(db, exercise_type_id)
        if not exercise_type:
            return None
        
        for key, value in exercise_type_data.items():
            if hasattr(exercise_type, key):
                setattr(exercise_type, key, value)
                
        db.commit()
        db.refresh(exercise_type)
        
        return exercise_type
    
    @staticmethod
    def delete(db: Session, exercise_type_id: UUID)-> bool:
        exercise_type = db.query(ExerciseTypeModel).filter(
            ExerciseTypeModel.id == exercise_type_id
        ).first()
        
        if not exercise_type:
            return False
        
        db.delete(exercise_type)
        db.commit()
        
        return True
    
    @staticmethod
    def desactivate(db: Session, exercise_type_id: UUID)-> bool:
        exercise_type = db.query(ExerciseTypeModel).filter(
            ExerciseTypeModel.id == exercise_type_id
        ).first()
        
        if not exercise_type:
            return False
        
        exercise_type.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_exercises_by_type(db: Session, exercise_type_id: UUID) -> List:
        """
        Obtiene todos los ejercicios de un tipo específico.

        Args:
            db (Session): Sesión de base de datos.
            exercise_type_id (UUID): ID del tipo de ejercicio.

        Returns:
            List: Lista de ejercicios del tipo especificado.
        """
        exercise_type = db.query(ExerciseTypeModel).filter(ExerciseTypeModel.id == exercise_type_id).first()
        
        if not exercise_type or not exercise_type.exercises:
            return []
            
        return exercise_type.exercises
        
        
