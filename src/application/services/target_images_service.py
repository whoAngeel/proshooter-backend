from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from uuid import UUID
import os

from src.infraestructure.database.repositories.target_images_repo import (
    TargetImagesRepository,
)
from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository,
)
from src.infraestructure.database.session import get_db
from src.presentation.schemas.target_images_schema import (
    TargetImageCreate,
    TargetImageDetail,
    TargetImageUpdate,
    TargetImageFilter,
    TargetImageList,
    TargetImageRead,
    TargetImageAnalysisSummary,
    TargetImageUploadResponse,
)


class TargetImagesService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def upload_image(
        self, image_data: TargetImageCreate
    ) -> Tuple[Optional[TargetImageUploadResponse], Optional[str]]:
        """Sube una imagen de blanco y devuelve la respuesta."""
        try:
            # verficar que el ejercicio exista
            exercise = PracticeExerciseRepository.get_by_id(
                self.db, image_data.exercise_id
            )
            if not exercise:
                return None, "EXERCISE_NOT_FOUND"

            # TODO: Subir la imagen a s3

            image_dict = image_data.model_dump()
            new_image = TargetImagesRepository.create(self.db, image_dict)

            response = TargetImageUploadResponse(
                image_id=new_image.id,
                file_path=new_image.file_path,
                file_size=new_image.file_size,
                content_type=new_image.content_type,
                upload_status="SUCCESS",
                message="Image uploaded successfully",
            )

            return response, None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPLOADING_IMAGE: {str(e)}"

    def get_exercise_image(
        self, exercise_id
    ) -> Tuple[Optional[TargetImageRead], Optional[str]]:
        """Obtiene todas las imágenes asociadas a un ejercicio."""
        try:
            exercise = PracticeExerciseRepository.get_by_id(
                self.db, exercise_id=exercise_id
            )
            if not exercise:
                return None, "EXERCISE_NOT_FOUND"

            image = TargetImagesRepository.get_by_exercise_id(
                self.db, exercise_id=exercise_id
            )
            image_read = TargetImageRead.model_validate(image)
            return image_read, None
        except Exception as e:
            return None, f"ERROR_GETTING_EXERCISE_IMAGE: {str(e)}"

    def get_image_by_id(
        self, image_id: UUID
    ) -> Tuple[Optional[TargetImageDetail], Optional[str]]:
        """Obtiene los detalles de una imagen por su ID."""
        try:
            image = TargetImagesRepository.get_by_id(self.db, image_id=image_id)
            if not image:
                return None, "IMAGE_NOT_FOUND"

            image_detail = TargetImageDetail.model_validate(image)
            return image_detail, None
        except Exception as e:
            return None, f"ERROR_GETTING_IMAGE_BY_ID: {str(e)}"

    def delete_image(self, image_id: UUID) -> Tuple[bool, Optional[str]]:
        try:
            image = self.get_image_by_id(image_id)
            # TODO: Eliminar el archivo de imagen de S3

            pass
        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_DELETING_IMAGE: {str(e)}"
