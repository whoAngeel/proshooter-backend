from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import Session, joinedload
import os

from src.infraestructure.database.models.target_image_model import TargetImageModel
from src.infraestructure.database.models.practice_exercise_model import (
    PracticeExerciseModel,
)
from src.infraestructure.database.models.practice_session_model import (
    IndividualPracticeSessionModel,
)


class TargetImagesRepository:
    @staticmethod
    def get_by_exercise_id(
        db: Session, exercise_id: UUID
    ) -> Optional[TargetImageModel]:
        """
        Obtiene la imagen asociada a un ejercicio específico.
        """
        return (
            db.query(TargetImageModel)
            .filter(TargetImageModel.exercise_id == exercise_id)
            .first()
        )

    @staticmethod
    def create(db: Session, image_data: dict) -> TargetImageModel:
        image = TargetImageModel(**image_data)
        db.add(image)
        db.commit()
        db.refresh(image)
        return image

    @staticmethod
    def get_by_id(db: Session, image_id: UUID) -> Optional[TargetImageModel]:
        """ """
        return (
            db.query(TargetImageModel)
            .options(
                joinedload(TargetImageModel.exercise),
                joinedload(TargetImageModel.analyses),
            )
            .filter(TargetImageModel.id == image_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TargetImageModel]:
        return (
            db.query(TargetImageModel)
            .options(
                joinedload(TargetImageModel.exercise),
                joinedload(TargetImageModel.analyses),
            )
            .order_by(desc(TargetImageModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_shooter(
        db: Session,
        shooter_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TargetImageModel]:
        return (
            db.query(TargetImageModel)
            .join(
                PracticeExerciseModel,
                TargetImageModel.exercise_id == PracticeExerciseModel.id,
            )
            .join(
                IndividualPracticeSessionModel,
                PracticeExerciseModel.session_id == IndividualPracticeSessionModel.id,
            )
            .filter(IndividualPracticeSessionModel.shooter_id == shooter_id)
            .order_by(desc(TargetImageModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def def_by_date_range(
        db: Session,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
        shooter_id: Optional[UUID] = None,
    ) -> List[TargetImageModel]:
        query = db.query(TargetImageModel.uploaded_at.between(start_date, end_date))

        if shooter_id:
            query = (
                query.join(
                    PracticeExerciseModel,
                    TargetImageModel.exercise_id == PracticeExerciseModel.id,
                )
                .join(
                    IndividualPracticeSessionModel,
                    PracticeExerciseModel.session_id
                    == IndividualPracticeSessionModel.id,
                )
                .filter(IndividualPracticeSessionModel.shooter_id == shooter_id)
            )
        return (
            query.order_by(desc(TargetImageModel.uploaded_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_orphaned_images(db: Session) -> List[TargetImageModel]:
        """
        Identifica imágenes que ya no tienen un ejercicio válido asociado.
        Esto puede ocurrir si se eliminan ejercicios pero no se limpian
        adecuadamente las imágenes asociadas.
        """
        return (
            db.query(TargetImageModel)
            .outerjoin(
                PracticeExerciseModel,
                TargetImageModel.exercise_id == PracticeExerciseModel.id,
            )
            .filter(PracticeExerciseModel.id.is_(None))
            .all()
        )

    @staticmethod
    def get_images_without_analysis(
        db: Session,
    ) -> List[TargetImageModel]:
        """
        Obtiene las imagenes que no han sido analizadas.
        Util para procesos batch de analisis automatico o para identificar trabajo pendiente de analisis
        """
        return (
            db.query(TargetImageModel)
            .outerjoin(TargetImageModel.analyses)
            .filter(~TargetImageModel.analyses.any())
        )

    @staticmethod
    def update(db: Session, image_id: UUID, image_data: dict) -> TargetImageModel:
        """
        Actualiza los datos de una imagen en la base de datos.
        """
        image = (
            db.query(TargetImageModel).filter(TargetImageModel.id == image_id).first()
        )

        if not image:
            return None

        db.commit()
        db.refresh(image)
        return image

    @staticmethod
    def delete(db: Session, image_id: UUID) -> bool:
        """
        Elimina una imagen de la base de datos.
        """
        image = (
            db.query(TargetImageModel).filter(TargetImageModel.id == image_id).first()
        )

        if not image:
            return False

        db.delete(image)
        db.commit()
        return True

    @staticmethod
    def search_by_combined_criteria(
        db: Session, filter_params: any, skip: int = 0, limit: int = 100
    ) -> List[TargetImageModel]:
        """
        Busqueda avanzada que combina varios criterios de filtrado.
        """
        query = db.query(TargetImageModel).options(
            joinedload(TargetImageModel.exercise)
        )

        if filter_params.get("exercise_id"):
            query = query.filter(
                TargetImageModel.exercise_id == filter_params["exercise_id"]
            )

        if filter_params.get("shooter_id"):
            query = (
                query.join(
                    PracticeExerciseModel,
                    TargetImageModel.exercise_id == PracticeExerciseModel.id,
                )
                .join(
                    IndividualPracticeSessionModel,
                    PracticeExerciseModel.session_id
                    == IndividualPracticeSessionModel.id,
                )
                .filter(
                    IndividualPracticeSessionModel.shooter_id
                    == filter_params["shooter_id"]
                )
            )

        # filtro por rango de fechas
        if filter_params.get("start_date") and filter_params.get("end_date"):
            query = query.filter(
                TargetImageModel.uploaded_at.between(
                    filter_params["start_date"], filter_params["end_date"]
                )
            )

        if filter_params.get("has_analysis") is not None:
            if filter_params["has_analysis"]:
                query = query.filter(TargetImageModel.analyses.any())
            else:
                query = query.filter(~TargetImageModel.analyses.any())
        return (
            query.order_by(desc(TargetImageModel.uploaded_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def has_analysis(db: Session, image_id: UUID) -> bool:
        """
        Verifica si una imagen tiene análisis asociados.
        """
        image = (
            db.query(TargetImageModel)
            .options(joinedload(TargetImageModel.analyses))
            .filter(TargetImageModel.id == image_id)
            .first()
        )

        if image and image.analyses and len(image.analyses) > 0:
            return True
        return False
