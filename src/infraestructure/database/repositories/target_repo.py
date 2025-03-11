from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete

from src.infraestructure.database.models.target_model import TargetModel
from src.domain.enums.target_enum import TargetType # Nota

class TargetRepository:
    """
    Repositorio para operaciones relacionadas con los blancos.

    Este repositorio proporciona métodos para crear, leer, actualizar y eliminar
    blancos en la base de datos, así como para buscar blancos por diferentes criterios.
    """

    @staticmethod
    async def create(db: Session, target_data: dict) -> TargetModel:
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
        db.flush()
        return target

    @staticmethod
    async def get_by_id(db: Session, target_id: UUID) -> Optional[TargetModel]:
        """
        Obtiene un blanco por su ID.

        Args:
            db (Session): Sesión de base de datos.
            target_id (UUID): ID del blanco a buscar.

        Returns:
            Optional[TargetModel]: El blanco encontrado o None si no existe.
        """
        query = select(TargetModel).where(TargetModel.id == target_id)
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[TargetModel]:
        """
        Obtiene todos los blancos con paginación.

        Args:
            db (Session): Sesión de base de datos.
            skip (int): Número de registros a omitir.
            limit (int): Número máximo de registros a devolver.

        Returns:
            List[TargetModel]: Lista de blancos.
        """
        query = select(TargetModel).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_type(db: Session, target_type: TargetType) -> List[TargetModel]:
        """
        Obtiene todos los blancos de un tipo específico.

        Args:
            db (Session): Sesión de base de datos.
            target_type (TargetType): Tipo de blanco a buscar.

        Returns:
            List[TargetModel]: Lista de blancos del tipo especificado.
        """
        query = select(TargetModel).where(TargetModel.target_type == target_type)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_active(db: Session) -> List[TargetModel]:
        """
        Obtiene todos los blancos activos.

        Args:
            db (Session): Sesión de base de datos.

        Returns:
            List[TargetModel]: Lista de blancos activos.
        """
        query = select(TargetModel).where(TargetModel.is_active == True)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update(db: Session, target_id: UUID, target_data: dict) -> Optional[TargetModel]:
        """
        Actualiza un blanco existente.

        Args:
            db (Session): Sesión de base de datos.
            target_id (UUID): ID del blanco a actualizar.
            target_data (dict): Datos del blanco a actualizar.

        Returns:
            Optional[TargetModel]: El blanco actualizado o None si no existe.
        """
        query = update(TargetModel).where(TargetModel.id == target_id).values(**target_data)
        await db.execute(query)

        # Obtener el blanco actualizado
        return await TargetRepository.get_by_id(db, target_id)

    @staticmethod
    async def delete(db: Session, target_id: UUID) -> bool:
        """
        Elimina un blanco de la base de datos.

        Args:
            db (Session): Sesión de base de datos.
            target_id (UUID): ID del blanco a eliminar.

        Returns:
            bool: True si el blanco fue eliminado, False si no existe.
        """
        # Primero verificamos que el blanco existe
        target = await TargetRepository.get_by_id(db, target_id)
        if not target:
            return False

        # Eliminar el blanco
        query = delete(TargetModel).where(TargetModel.id == target_id)
        await db.execute(query)
        return True

    @staticmethod
    async def deactivate(db: Session, target_id: UUID) -> Optional[TargetModel]:
        """
        Desactiva un blanco (soft delete).

        Args:
            db (Session): Sesión de base de datos.
            target_id (UUID): ID del blanco a desactivar.

        Returns:
            Optional[TargetModel]: El blanco desactivado o None si no existe.
        """
        target = await TargetRepository.get_by_id(db, target_id)
        if not target:
            return None

        target.is_active = False
        db.flush()
        return target

    @staticmethod
    async def search_by_name(db: Session, name: str) -> List[TargetModel]:
        """
        Busca blancos por nombre (búsqueda parcial).

        Args:
            db (Session): Sesión de base de datos.
            name (str): Nombre o parte del nombre a buscar.

        Returns:
            List[TargetModel]: Lista de blancos que coinciden con el criterio de búsqueda.
        """
        query = select(TargetModel).where(TargetModel.name.ilike(f"%{name}%"))
        result = await db.execute(query)
        return result.scalars().all()
