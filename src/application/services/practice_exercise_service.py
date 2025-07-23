from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime
import math
from fastapi import UploadFile

from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository,
)
from src.infraestructure.database.repositories.practice_session_repo import (
    PracticeSessionRepository as IndividualPracticeSessionRepository,
)
from src.infraestructure.database.repositories.exercise_type_repo import (
    ExerciseTypeRepository,
)
from src.infraestructure.database.repositories.target_repo import TargetRepository
from src.infraestructure.database.repositories.weapon_repo import WeaponRepository
from src.infraestructure.database.repositories.ammunition_repo import (
    AmmunitionRepository,
)
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.infraestructure.database.repositories.target_images_repo import (
    TargetImagesRepository,
)
from src.infraestructure.database.session import get_db
from src.presentation.schemas.practice_exercise_schema import (
    PracticeExerciseCreate,
    PracticeExerciseRead,
    PracticeExerciseDetail,
    PracticeExerciseUpdate,
    PracticeExerciseList,
    PracticeExerciseStatistics,
    PracticeExerciseFilter,
    PerformanceAnalysis,
)
from src.presentation.schemas.target_images_schema import (
    TargetImageUpdate,
    TargetImageUploadResponse,
)
from src.infraestructure.utils.s3_utils import upload_file_to_s3


class PracticeExerciseService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_exercise(
        self, exercise_data: PracticeExerciseCreate
    ) -> Tuple[Optional[PracticeExerciseRead], Optional[str]]:
        try:
            # verificar que los objetos relacionados existen
            session = IndividualPracticeSessionRepository.get_by_id(
                self.db, exercise_data.session_id
            )
            if not session:
                return None, "PRACTICE_SESSION_NOT_FOUND"

            if session.is_finished:
                return None, "PRACTICE_SESSION_ALREADY_FINISHED"

            exercise_type = ExerciseTypeRepository.get_by_id(
                self.db, exercise_data.exercise_type_id
            )
            if not exercise_type:
                return None, "EXERCISE_TYPE_NOT_FOUND"

            target = TargetRepository.get_by_id(self.db, exercise_data.target_id)
            if not target:
                return None, "TARGET_NOT_FOUND"

            weapon = WeaponRepository.get_by_id(self.db, exercise_data.weapon_id)
            if not weapon:
                return None, "WEAPON_NOT_FOUND"

            ammunition = AmmunitionRepository.get_by_id(
                self.db, exercise_data.ammunition_id
            )
            if not ammunition:
                return None, "AMMUNITION_NOT_FOUND"

            is_compatible = WeaponRepository.check_compatibility(
                self.db, exercise_data.weapon_id, exercise_data.ammunition_id
            )
            if not is_compatible:
                return None, "WEAPON_AMMUNITION_NOT_COMPATIBLE"

            # convertir lo datos a diccionario para crear el ejercicio
            exercise_dict = exercise_data.model_dump()

            new_exercise = PracticeExerciseRepository.create(self.db, exercise_dict)

            self._update_session_totals(session.id)

            return PracticeExerciseRead.model_validate(new_exercise), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_CREATING_EXERCISE: {str(e)}"

    def get_exercise_by_id(
        self, exercise_id: UUID
    ) -> Tuple[Optional[PracticeExerciseDetail], Optional[str]]:
        try:
            exercise = PracticeExerciseRepository.get_by_id(self.db, exercise_id)
            if not exercise:
                return None, "PRACTICE_EXERCISE_NOT_FOUND"
            if exercise.target_image and exercise.target_image.analyses:
                analysis = exercise.target_image.analyses[0]
                exercise.target_image.analysis = analysis
            elif exercise.target_image:
                exercise.target_image.analysis = None

            return PracticeExerciseDetail.model_validate(exercise), None
        except Exception as e:
            return None, f"ERROR_FETCHING_EXERCISE: {str(e)}"

    def get_all_exercises(
        self, filter_params: PracticeExerciseFilter
    ) -> PracticeExerciseList:
        filter_dict = filter_params.model_dump(exclude_unset=True)

        exercises = PracticeExerciseRepository.search_by_combined_criteria(
            self.db, filter_dict, filter_params.skip, filter_params.limit
        )

        total_count = PracticeExerciseRepository.count_by_criteria(self.db, filter_dict)

        page = (filter_params.skip // filter_params.limit) + 1
        pages = math.ceil(total_count / filter_params.limit) if total_count > 0 else 1

        items = [PracticeExerciseRead.model_validate(ex) for ex in exercises]

        return PracticeExerciseList(
            items=items,
            total=total_count,
            page=page,
            size=filter_params.limit,
            pages=pages,
        )

    def get_session_exercises(
        self, session_id: UUID
    ) -> Tuple[Optional[List[PracticeExerciseRead]], Optional[str]]:
        session = IndividualPracticeSessionRepository.get_by_id(self.db, session_id)
        if not session:
            return None, "PRACTICE_SESSION_NOT_FOUND"

        exercises = PracticeExerciseRepository.get_by_session(self.db, session_id)

        return [PracticeExerciseRead.model_validate(ex) for ex in exercises], None

    def udpate_exercise(
        self, exercise_id: UUID, exercise_data: PracticeExerciseUpdate
    ) -> Tuple[Optional[PracticeExerciseRead], Optional[str]]:
        try:
            existing_exercise = PracticeExerciseRepository.get_by_id(
                self.db, exercise_id
            )
            if not existing_exercise:
                return None, "PRACTICE_EXERCISE_NOT_FOUND"

            # verificar entidades relacionadas si se estan actualizando
            if exercise_data.exercise_type_id:
                exercise_type = ExerciseTypeRepository.get_by_id(
                    self.db, exercise_data.exercise_type_id
                )
                if not exercise_type:
                    return None, "EXERCISE_TYPE_NOT_FOUND"
            if exercise_data.target_id:
                target = TargetRepository.get_by_id(self.db, exercise_data.target_id)
                if not target:
                    return None, "TARGET_NOT_FOUND"
            if exercise_data.weapon_id:
                weapon = WeaponRepository.get_by_id(self.db, exercise_data.weapon_id)
                if not weapon:
                    return None, "WEAPON_NOT_FOUND"
            if exercise_data.ammunition_id:
                ammunition = AmmunitionRepository.get_by_id(
                    self.db, exercise_data.ammunition_id
                )
                if not ammunition:
                    return None, "AMMUNITION_NOT_FOUND"

            # verificar compatibilidad entre arma y municion
            weapon_id = exercise_data.weapon_id or existing_exercise.weapon_id
            ammo_id = exercise_data.ammunition_id or existing_exercise.ammunition_id

            if exercise_data.weapon_id or exercise_data.ammunition_id:
                is_compatible = WeaponRepository.check_compatibility(
                    self.db, weapon_id, ammo_id
                )
                if not is_compatible:
                    return None, "WEAPON_AMMUNITION_NOT_COMPATIBLE"

            # convertir los datos a diccionario para actualizar el ejercicio
            exercise_dict = exercise_data.model_dump(
                exclude_unset=True, exclude_none=True
            )

            # actualizar el ejercicio en la base de datos
            updated_exercise = PracticeExerciseRepository.update(
                self.db, exercise_id, exercise_dict
            )

            if not updated_exercise:
                return None, "ERROR_UPDATING_EXERCISE"

            self._update_session_totals(existing_exercise.session_id)

            return PracticeExerciseRead.model_validate(updated_exercise), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPDATING_EXERCISE: {str(e)}"

    def delete_exercise(self, exercise_id: UUID) -> Tuple[bool, Optional[str]]:
        try:
            existing_exercise = PracticeExerciseRepository.get_by_id(
                self.db, exercise_id
            )
            if not existing_exercise:
                return False, "PRACTICE_EXERCISE_NOT_FOUND"

            session_id = existing_exercise.session_id

            success = PracticeExerciseRepository.delete(self.db, exercise_id)

            if not success:
                return False, "ERROR_DELETING_EXERCISE"

            self._update_session_totals(session_id)

            return True, None
        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_DELETING_EXERCISE: {str(e)}"

    def upload_exercise_image(
        self, exercise_id: UUID, file: UploadFile, user_id: UUID, replace: bool = False
    ) -> Tuple[Optional[TargetImageUploadResponse], Optional[str]]:
        exercise = PracticeExerciseRepository.get_by_id(self.db, exercise_id)
        if not exercise:
            return None, "EXERCISE_NOT_FOUND"
        try:
            # Si hay imagen y se pide reemplazar, eliminar la anterior
            if replace and exercise.target_image_id:
                old_image = TargetImagesRepository.get_by_id(
                    self.db, exercise.target_image_id
                )
                if old_image:
                    # Eliminar de S3
                    from src.infraestructure.utils.s3_utils import delete_file_from_s3

                    try:
                        delete_file_from_s3(
                            old_image.file_path, bucket_name="proshooter"
                        )
                    except Exception as e:
                        print(f"Error eliminando imagen anterior de S3: {str(e)}")
                    # Eliminar de la base de datos
                    TargetImagesRepository.delete(self.db, old_image.id)
            elif exercise.target_image_id:
                # Si no se pide reemplazo y ya hay imagen, retornar error
                return None, "EXERCISE_ALREADY_HAS_IMAGE"

            folder = f"target_images/{user_id}"
            file_url = upload_file_to_s3(
                file,
                file_name_prefix="exercise_image",
                bucket_name="proshooter",
                folder=folder,
                allowed_types=["image/png", "image/jpeg"],
                max_size_mb=5,  # 5 MB
            )
            image_dict = {
                "file_path": file_url,
                "file_size": file.size,
                "content_type": file.content_type,
            }
            new_image = TargetImagesRepository.create(self.db, image_dict)
            # Actualizar el ejercicio con el id de la imagen
            updated_exercise = PracticeExerciseRepository.update(
                self.db, exercise_id, {"target_image_id": new_image.id}
            )
            response = TargetImageUploadResponse(
                image_id=new_image.id,
                file_path=new_image.file_path,
                file_size=new_image.file_size,
                content_type=new_image.content_type,
                upload_status="SUCCESS",
                message="Image uploaded and associated successfully",
            )
            return response, None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPLOADING_EXERCISE_IMAGE: {str(e)}"

    def get_exercise_statistics(
        self, shooter_id: Optional[UUID] = None
    ) -> Tuple[Optional[PracticeExerciseStatistics], Optional[str]]:
        try:
            # si se proporciona un id de tirador, verificamos que exista
            if shooter_id:
                shooter, _ = ShooterRepository.get_by_user_id(self.db, shooter_id)
                if not shooter:
                    return None, "SHOOTER_NOT_FOUND"

            stats = PracticeExerciseRepository.get_statistics(self.db, shooter_id)

            # convertir el formato del esquema
            statistics = PracticeExerciseStatistics(
                total_exercises=stats["total_exercises"],
                avg_accuracy=stats["avg_accuracy"],
                total_ammunition_used=stats["total_ammunition_used"],
                total_hits=stats["total_hits"],
                hit_percentage=stats["hit_percentage"],
                avg_reaction_time=stats["avg_reaction_time"],
                by_distance=stats["by_distance"],
                by_exercise_type=stats["by_exercise_type"],
                by_weapon=stats["by_weapon"],
            )

            return statistics, None
        except Exception as e:
            return None, f"ERROR_GETTING_STATISTICS: {str(e)}"

    def get_performance_analysis(
        self, category: str, shooter_id: Optional[UUID] = None
    ) -> Tuple[Optional[PerformanceAnalysis], Optional[str]]:
        try:
            valid_categories = [
                "weapon",
                "target",
                "ammunition",
                "distance",
                "exercise_type",
            ]
            if category not in valid_categories:
                return (
                    None,
                    f"INVALID_CATEGORY: deberia ser uno de {', '.join(valid_categories)}",
                )

            if shooter_id:
                shooter, _ = ShooterRepository.get_by_user_id(self.db, shooter_id)
                if not shooter:
                    return None, "SHOOTER_NOT_FOUND"

            analysis_data = (
                PracticeExerciseRepository.get_performance_analysis_by_category(
                    self.db, category, shooter_id
                )
            )

            total_accuracy = 0
            total_items = len(analysis_data)

            if total_items > 0:
                for item in analysis_data:
                    total_accuracy += item.get("avg_accuracy", 0)
                avg_accuracy = total_accuracy / total_items

            else:
                avg_accuracy = 0

            analysis = PerformanceAnalysis(
                category=category,
                items=analysis_data,
                avg_accuracy=avg_accuracy,
                total_exercises=sum(
                    item.get("exercises_count", 0) for item in analysis_data
                ),
            )

            return analysis, None
        except Exception as e:
            return None, f"ERROR_GETTING_PERFORMANCE_ANALYSIS: {str(e)}"

    def _update_session_totals(self, session_id: UUID) -> None:
        """
        METODO auxiliar para actualizar los totales de disparos, aciertos y precision de una sesion
        """

        try:
            exercises = PracticeExerciseRepository.get_by_session(self.db, session_id)

            total_shots = sum(exercise.ammunition_used for exercise in exercises)
            total_hits = sum(exercise.hits for exercise in exercises)

            # precision
            accuracy_percentage = (
                (total_hits / total_shots * 100) if total_shots > 0 else 0.0
            )

            session_data = {
                "total_shots_fired": total_shots,
                "total_hits": total_hits,
                "accuracy_percentage": accuracy_percentage,
            }

            IndividualPracticeSessionRepository.update(
                self.db, session_id, session_data
            )
        except Exception as e:
            self.db.rollback()
            print(f"Error updating session totals: {str(e)}")
