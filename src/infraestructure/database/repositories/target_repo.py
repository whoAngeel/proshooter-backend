from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.infraestructure.database.models.target_model import TargetModel
from src.domain.enums.target_enum import TargetType # Nota

class TargetRepository:
    """
    Repositorio para operaciones relacionadas con los blancos.

    Este repositorio proporciona métodos para crear, leer, actualizar y eliminar
    blancos en la base de datos, así como para buscar blancos por diferentes criterios.
    """

    @staticmethod
    def create(db: Session, target_data: dict) -> TargetModel:
        """
        Crea un nuevo blanco en la base de datos.

        Args:
            db (Session): Sesión de base de datos.
            target_data (dict): Datos del blanco a crear.

        Returns:
            TargetModel: El blanco creado.
        """
        target = TargetModel(**target_data)
        db.add(target)
        db.commit()
        return target

    @staticmethod
    def get_by_id(db: Session, target_id: UUID) -> Optional[TargetModel]:
        """
        Obtiene un blanco por su ID.

        Args:
            db (Session): Sesión de base de datos.
            target_id (UUID): ID del blanco a buscar.

        Returns:
            Optional[TargetModel]: El blanco encontrado o None si no existe.
        """
        result = db.query(TargetModel).filter(TargetModel.id == target_id).first()
        return result

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[TargetModel]:
        """
        Obtiene todos los blancos con paginación.

        Args:
            db (Session): Sesión de base de datos.
            skip (int): Número de registros a omitir.
            limit (int): Número máximo de registros a devolver.

        Returns:
            List[TargetModel]: Lista de blancos.
        """
        return db.query(TargetModel).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_type(db: Session, target_type: TargetType) -> List[TargetModel]:
        """
        Obtiene todos los blancos de un tipo específico.

        Args:
            db (Session): Sesión de base de datos.
            target_type (TargetType): Tipo de blanco a buscar.

        Returns:
            List[TargetModel]: Lista de blancos del tipo especificado.
        """
        result = db.query(TargetModel).filter(TargetModel.target_type == target_type).all()
        return result

    @staticmethod
    def get_active(db: Session) -> List[TargetModel]:
        """
        Obtiene todos los blancos activos.

        Args:
            db (Session): Sesión de base de datos.

        Returns:
            List[TargetModel]: Lista de blancos activos.
        """
        result = db.query(TargetModel).filter(TargetModel.is_active == True).all()
        return result

    @staticmethod
    def update(db: Session, target_id: UUID, target_data: dict) -> Optional[TargetModel]:
        """
        Actualiza un blanco existente.

        Args:
            db (Session): Sesión de base de datos.
            target_id (UUID): ID del blanco a actualizar.
            target_data (dict): Datos del blanco a actualizar.

        Returns:
            Optional[TargetModel]: El blanco actualizado o None si no existe.
        """
        target = db.query(TargetModel).filter(TargetModel.id == target_id).first()
        if not target:
            return None

        for key, value in target_data.items():
            setattr(target, key, value)

        db.commit()
        return target

    @staticmethod
    def delete(db: Session, target_id: UUID) -> bool:
        """
        Elimina un blanco de la base de datos.

        Args:
            db (Session): Sesión de base de datos.
            target_id (UUID): ID del blanco a eliminar.

        Returns:
            bool: True si el blanco fue eliminado, False si no existe.
        """
        # Primero verificamos que el blanco existe
        target = db.query(TargetModel).filter(TargetModel.id == target_id).first()
        if not target:
            return False

        # Eliminar el blanco
        db.delete(target)
        db.commit()
        return True

    @staticmethod
    def deactivate(db: Session, target_id: UUID) -> Optional[TargetModel]:
        """
        Desactiva un blanco (soft delete).

        Args:
            db (Session): Sesión de base de datos.
            target_id (UUID): ID del blanco a desactivar.

        Returns:
            Optional[TargetModel]: El blanco desactivado o None si no existe.
        """
        target = db.query(TargetModel).filter(TargetModel.id == target_id).first()
        if not target:
            return None

        target.is_active = False
        db.commit()
        return target

    @staticmethod
    def search_by_name(db: Session, name: str) -> List[TargetModel]:
        """
        Busca blancos por nombre (búsqueda parcial).

        Args:
            db (Session): Sesión de base de datos.
            name (str): Nombre o parte del nombre a buscar.

        Returns:
            List[TargetModel]: Lista de blancos que coinciden con el criterio de búsqueda.
        """
        result = db.query(TargetModel).filter(TargetModel.name.ilike(f"%{name}%")).all()
        return result

    @staticmethod
    def search_by_term(db: Session, term: str) -> List[TargetModel]:
        search_pattern = f"%{term}%"

        query = db.query(TargetModel).filter(
            or_(
                TargetModel.name.ilike(search_pattern),
                TargetModel.description.ilike(search_pattern)
            )
        ).order_by(TargetModel.name)

        return query.all()
