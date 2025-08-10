from datetime import datetime
from sqlalchemy.orm import Session
import logging
import io
import requests
import cv2
import base64
import numpy as np
from PIL import Image as PILImage

# from PIL import Image
from fastapi import HTTPException, Depends
from typing import List, Any, Tuple, Optional, Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from src.domain.enums.role_enum import RoleEnum

from src.infraestructure.utils.pdf_generator import PDFReportGenerator
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import matplotlib.patches as patches


from src.presentation.schemas.reports import ReportRequest, ReportData, ReportType
from src.infraestructure.database.session import get_db


class ReportService:
    """Servicio para generar reportes de tiradores"""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.pdf_generator = PDFReportGenerator()
        self.logger = logging.getLogger(__name__)

    async def generate_report(
        self, report_request: ReportRequest, current_user_id: str
    ) -> bytes:
        """Generar reporte según el tipo solicitado"""
        try:
            # Verificar permisos
            if not await self._check_report_permissions(
                report_request.shooter_id, current_user_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="No tienes permisos para generar este reporte",
                )

            # Obtener datos para el reporte
            report_data = await self._gather_report_data(report_request)

            # validar los datos
            self._validate_report_data(report_data)

            # Generar PDF según el tipo
            if report_request.report_type == ReportType.INDIVIDUAL_SESSION:
                pdf_bytes = self.pdf_generator.generate_session_report(report_data)
            elif report_request.report_type == ReportType.MONTHLY_SUMMARY:
                pdf_bytes = self.pdf_generator.generate_monthly_report(report_data)
            else:
                raise HTTPException(
                    status_code=400, detail="Tipo de reporte no soportado"
                )

            print(f"✅ PDF generado exitosamente, tamaño: {len(pdf_bytes)} bytes")
            return pdf_bytes

        except Exception as e:
            self.logger.error(f"❌ Error generando reporte: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error interno generando reporte: {e}"
            )

    async def _check_report_permissions(
        self, shooter_id: str, current_user_id: str
    ) -> bool:
        """Verificar permisos para generar reporte"""
        from src.infraestructure.database.models.user_model import UserModel

        try:
            user = (
                self.db.query(UserModel).filter(UserModel.id == current_user_id).first()
            )
            if not user:
                return False

            # Si es tirador, solo puede ver su propio reporte
            if user.role == RoleEnum.TIRADOR:
                return str(shooter_id) == str(current_user_id)

            # Si es admin, instructor o jefe, puede ver cualquier reporte
            if user.role in [
                RoleEnum.ADMIN,
                RoleEnum.INSTRUCTOR,
                RoleEnum.INSTRUCTOR_JEFE,
            ]:
                return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Error verificando permisos: {e}")
            return False

    async def _gather_report_data(self, request: ReportRequest) -> ReportData:
        """Recopilar datos necesarios para el reporte"""
        print(f"🔍 Recopilando datos para shooter_id: {request.shooter_id}")

        # Obtener información del tirador
        shooter_info = self._get_shooter_info(request.shooter_id)
        print(f"🔍 Shooter info obtenido: {bool(shooter_info)}")

        # Obtener sesiones de práctica
        sessions = self._get_practice_sessions(request)
        print(f"🔍 Sesiones obtenidas: {len(sessions)}")
        self._debug_session_data(sessions)

        # Obtener estadísticas
        statistics = self._get_shooter_statistics(request.shooter_id)
        print(f"🔍 Estadísticas obtenidas: {bool(statistics)}")

        # Obtener evaluaciones
        evaluations = self._get_evaluations(
            request.shooter_id, request.start_date, request.end_date
        )
        print(f"🔍 Evaluaciones obtenidas: {len(evaluations)}")

        # Obtener ejercicios
        exercises = self._get_exercises_from_sessions(sessions)
        print(f"🔍 Ejercicios extraídos: {len(exercises)}")

        # Generar imágenes de análisis si se solicitan
        analysis_images = []
        if request.include_images:
            analysis_images = self._generate_analysis_images(sessions)

        return ReportData(
            shooter_info=shooter_info,
            sessions=sessions,
            statistics=statistics,
            evaluations=evaluations,
            exercises=exercises,
            analysis_images=analysis_images,
        )

    def _debug_session_data(self, sessions: List[Dict[str, Any]]) -> None:
        """Método temporal para debugging"""
        print(f"🔍 DEBUG: Total sesiones encontradas: {len(sessions)}")
        for i, session in enumerate(sessions[:2]):  # Solo las primeras 2
            print(f"🔍 Sesión {i+1}:")
            print(f"  - ID: {session.get('id')}")
            print(f"  - Fecha: {session.get('date')}")
            print(f"  - Disparos: {session.get('total_shots_fired')}")
            print(f"  - Ejercicios: {len(session.get('exercises', []))}")

    def _get_shooter_info(self, shooter_id: str) -> Dict[str, Any]:
        """Obtener información del tirador"""
        from sqlalchemy.orm import joinedload
        from src.infraestructure.database.models.user_model import (
            UserModel,
            UserPersonalDataModel,
        )
        from src.infraestructure.database.models.shooter_model import ShooterModel
        from src.infraestructure.database.models.shooting_club_model import (
            ShootingClubModel,
        )

        try:
            # Consulta optimizada con joinedload para evitar consultas N+1
            user = (
                self.db.query(UserModel)
                .options(
                    joinedload(UserModel.personal_data),
                    joinedload(UserModel.shooter).joinedload(ShooterModel.club),
                )
                .filter(UserModel.id == shooter_id)
                .first()
            )

            if not user:
                return {}

            personal_data = user.personal_data
            shooter = user.shooter
            club = shooter.club if shooter else None

            classification = "Sin Clasificar"

            if shooter and shooter.level:
                try:
                    classification = (
                        shooter.level.value
                        if hasattr(shooter.level, "value")
                        else str(shooter.level)
                    )
                except:
                    classification = str(shooter.level)

            return {
                "user_id": str(user.id),
                "email": user.email,
                "role": user.role,
                "first_name": personal_data.first_name if personal_data else "N/A",
                "second_name": personal_data.second_name if personal_data else "",
                "last_name1": personal_data.last_name1 if personal_data else "N/A",
                "last_name2": personal_data.last_name2 if personal_data else "",
                "full_name": self._build_full_name(personal_data),
                "phone_number": personal_data.phone_number if personal_data else "N/A",
                "city": personal_data.city if personal_data else "N/A",
                "state": personal_data.state if personal_data else "N/A",
                "country": personal_data.country if personal_data else "N/A",
                "classification": classification,
                "club_name": club.name if club else "Sin club",
                "club_id": str(club.id) if club else None,
                "shooter_id": str(shooter.user_id) if shooter else None,
            }

        except Exception as e:
            self.logger.error(
                f"❌ Error obteniendo información del tirador {shooter_id}: {e}"
            )
            return {}

    def _build_full_name(self, personal_data) -> str:
        """Construir nombre completo del tirador"""
        if not personal_data:
            return "N/A"

        name_parts = [
            personal_data.first_name,
            personal_data.second_name or "",
            personal_data.last_name1,
            personal_data.last_name2 or "",
        ]

        return " ".join(part for part in name_parts if part and part.strip())

    def _get_practice_sessions(self, request: ReportRequest) -> List[Dict[str, Any]]:
        """Obtener sesiones de práctica con datos completos"""
        from sqlalchemy.orm import joinedload
        from src.infraestructure.database.models.practice_session_model import (
            IndividualPracticeSessionModel,
        )
        from src.infraestructure.database.models.user_model import (
            UserModel,
            UserPersonalDataModel,
        )
        from src.infraestructure.database.models.practice_exercise_model import (
            PracticeExerciseModel,
        )

        try:
            query = (
                self.db.query(IndividualPracticeSessionModel)
                .options(
                    joinedload(IndividualPracticeSessionModel.instructor).joinedload(
                        UserModel.personal_data
                    ),
                    joinedload(IndividualPracticeSessionModel.exercises).joinedload(
                        PracticeExerciseModel.weapon
                    ),
                    joinedload(IndividualPracticeSessionModel.exercises).joinedload(
                        PracticeExerciseModel.ammunition
                    ),
                    joinedload(IndividualPracticeSessionModel.exercises).joinedload(
                        PracticeExerciseModel.exercise_type
                    ),
                    joinedload(IndividualPracticeSessionModel.exercises).joinedload(
                        PracticeExerciseModel.target
                    ),
                    joinedload(IndividualPracticeSessionModel.evaluation),
                )
                .filter(IndividualPracticeSessionModel.shooter_id == request.shooter_id)
            )

            if request.start_date:
                query = query.filter(
                    IndividualPracticeSessionModel.date >= request.start_date
                )

            if request.end_date:
                query = query.filter(
                    IndividualPracticeSessionModel.date <= request.end_date
                )

            query = query.order_by(IndividualPracticeSessionModel.date.desc())

            sessions = query.all()

            return [self._serialize_session(session) for session in sessions]

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo sesiones de práctica: {e}")
            return []

    def _serialize_session(self, session) -> Dict[str, Any]:
        """Serializar sesión de práctica a diccionario"""
        instructor_name = "N/A"
        if session.instructor and session.instructor.personal_data:
            personal = session.instructor.personal_data
            instructor_name = f"{personal.first_name} {personal.last_name1}"

        return {
            "id": str(session.id),
            "date": session.date.strftime("%Y-%m-%d %H:%M:%S"),
            "location": session.location,
            "instructor_name": instructor_name,
            "total_shots_fired": session.total_shots_fired,
            "total_hits": session.total_hits,
            "accuracy_percentage": session.accuracy_percentage,
            "total_session_score": session.total_session_score,
            "average_score_per_exercise": session.average_score_per_exercise,
            "average_score_per_shot": session.average_score_per_shot,
            "best_shot_score": session.best_shot_score,
            "is_finished": session.is_finished,
            "evaluation_pending": session.evaluation_pending,
            "exercises": [self._serialize_exercise(ex) for ex in session.exercises],
            "evaluation": (
                self._serialize_evaluation(session.evaluation)
                if session.evaluation
                else None
            ),
        }

    def _serialize_exercise(self, exercise) -> Dict[str, Any]:
        """Serializar ejercicio a diccionario"""
        return {
            "id": str(exercise.id),
            "exercise_type": (
                exercise.exercise_type.name if exercise.exercise_type else "N/A"
            ),
            "distance": exercise.distance,
            "weapon_name": exercise.weapon.name if exercise.weapon else "N/A",
            "ammunition_type": (
                exercise.ammunition.caliber if exercise.ammunition else "N/A"
            ),
            "target_type": exercise.target.name if exercise.target else "N/A",
            "ammunition_allocated": exercise.ammunition_allocated,
            "ammunition_used": exercise.ammunition_used,
            "hits": exercise.hits,
            "accuracy_percentage": exercise.accuracy_percentage,
            "total_score": exercise.total_score,
            "average_score_per_shot": exercise.average_score_per_shot,
            "max_score_achieved": exercise.max_score_achieved,
            "group_diameter": exercise.group_diameter,
            "reaction_time": exercise.reaction_time,
            "firing_cadence": exercise.firing_cadence,
            "time_limit": exercise.time_limit,
            "has_target_image": exercise.target_image_id is not None,
        }

    def _serialize_evaluation(self, evaluation) -> Dict[str, Any]:
        """Serializar evaluación a diccionario"""
        if not evaluation:
            return None

        return {
            "id": str(evaluation.id),
            "score": evaluation.final_score,
            "comments": evaluation.instructor_notes,
            "date": evaluation.date.strftime("%Y-%m-%d %H:%M:%S"),
            "recommendations": evaluation.recomendations,
        }

    def _get_shooter_statistics(self, shooter_id: str) -> Dict[str, Any]:
        """Obtener estadísticas del tirador"""
        from src.infraestructure.database.models.shooter_stats_model import (
            ShooterStatsModel,
        )
        from src.infraestructure.database.models.shooter_model import ShooterModel

        try:
            stats = (
                self.db.query(ShooterStatsModel)
                .filter(ShooterStatsModel.shooter_id == shooter_id)
                .first()
            )

            # ✅ OBTENER LEVEL DEL SHOOTER
            shooter = (
                self.db.query(ShooterModel)
                .filter(ShooterModel.user_id == shooter_id)
                .first()
            )

            classification = "Sin clasificar"
            if shooter and shooter.level:
                try:
                    classification = (
                        shooter.level.value
                        if hasattr(shooter.level, "value")
                        else str(shooter.level)
                    )
                except:
                    classification = str(shooter.level)

            if not stats:
                return {
                    "total_shots": 0,
                    "accuracy": 0,
                    "total_sessions": 0,
                    "average_score": 0.0,
                    "classification": classification,
                    "last_updated": "N/A",
                }

            return {
                "shooter_id": str(stats.shooter_id),
                "total_shots": stats.total_shots,
                "accuracy": stats.accuracy,
                "reaction_shots": stats.reaction_shots,
                "precision_shots": stats.presicion_shots,
                "draw_time_avg": stats.draw_time_avg,
                "reload_time_avg": stats.reload_time_avg,
                "average_hit_factor": stats.average_hit_factor,
                "effectiveness": stats.effectiveness,
                "trend_accuracy": stats.trend_accuracy,
                "last_10_sessions_avg": stats.last_10_sessions_avg,
                "precision_exercise_accuracy": stats.precision_exercise_accuracy,
                "reaction_exercise_accuracy": stats.reaction_exercise_accuracy,
                "movement_exercise_accuracy": stats.movement_exercise_accuracy,
                "average_score": stats.average_score,
                "best_score_session": stats.best_score_session,
                "best_shot_ever": stats.best_shot_ever,
                "score_trend": stats.score_trend,
                "precision_exercise_avg_score": stats.precision_exercise_avg_score,
                "reaction_exercise_avg_score": stats.reaction_exercise_avg_score,
                "movement_exercise_avg_score": stats.movement_exercise_avg_score,
                "common_error_zones": stats.common_error_zones,
                "classification": classification,  # ✅ USAR CLASSIFICATION OBTENIDA DEL SHOOTER
                "total_sessions": self._count_total_sessions(shooter_id),
                "last_updated": (
                    stats.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                    if stats.updated_at
                    else "N/A"
                ),
            }

        except Exception as e:
            self.logger.error(
                f"❌ Error obteniendo estadísticas del tirador {shooter_id}: {e}"
            )
            return {}

    def _count_total_sessions(self, shooter_id: str) -> int:
        """Contar total de sesiones del tirador"""
        from src.infraestructure.database.models.practice_session_model import (
            IndividualPracticeSessionModel,
        )

        try:
            return (
                self.db.query(IndividualPracticeSessionModel)
                .filter(IndividualPracticeSessionModel.shooter_id == shooter_id)
                .count()
            )
        except Exception:
            return 0

    def _get_evaluations(
        self,
        shooter_id: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> List[Dict[str, Any]]:
        """Obtener evaluaciones del tirador"""
        from src.infraestructure.database.models.evaluation_model import (
            PracticeEvaluationModel,
        )
        from src.infraestructure.database.models.practice_session_model import (
            IndividualPracticeSessionModel,
        )
        from src.infraestructure.database.models.user_model import (
            UserModel,
            UserPersonalDataModel,
        )
        from sqlalchemy.orm import joinedload

        try:
            query = (
                self.db.query(PracticeEvaluationModel)
                .join(IndividualPracticeSessionModel)
                .options(
                    joinedload(PracticeEvaluationModel.evaluator).joinedload(
                        UserModel.personal_data
                    )
                )
                .filter(IndividualPracticeSessionModel.shooter_id == shooter_id)
            )

            if start_date:
                query = query.filter(PracticeEvaluationModel.date >= start_date)

            if end_date:
                query = query.filter(PracticeEvaluationModel.date <= end_date)

            query = query.order_by(PracticeEvaluationModel.date.desc())

            evaluations = query.all()

            result = []
            for evaluation in evaluations:
                instructor_name = "N/A"

                if evaluation.evaluator and evaluation.evaluator.personal_data:
                    personal = evaluation.evaluator.personal_data
                    instructor_name = " ".join(
                        part
                        for part in [
                            personal.first_name,
                            personal.second_name,
                            personal.last_name1,
                            personal.last_name2,
                        ]
                        if part
                    )

                result.append(
                    {
                        "id": str(evaluation.id),
                        "score": evaluation.final_score,
                        "comments": evaluation.instructor_notes,
                        "recommendations": evaluation.recomendations,
                        "date": evaluation.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "instructor_name": instructor_name,
                        "session_id": str(evaluation.session_id),
                    }
                )

            return result

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo evaluaciones: {e}")
            return []

    def _get_exercises_from_sessions(
        self, sessions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extraer ejercicios de las sesiones"""
        exercises = []

        for session in sessions:
            session_exercises = session.get("exercises", [])

            for exercise in session_exercises:
                exercises.append(
                    {
                        "name": exercise.get("exercise_type", "Ejercicio Desconocido"),
                        "distance": exercise.get("distance", "N/A"),
                        "shots": exercise.get("ammunition_used", 0),
                        "hits": exercise.get("hits", 0),
                        "accuracy": exercise.get("accuracy_percentage", 0),
                        "score": int(exercise.get("total_score", 0)),
                        "max_score": exercise.get("max_score_achieved", 0),
                        "weapon": exercise.get("weapon_name", "N/A"),
                        "ammunition": exercise.get("ammunition_type", "N/A"),
                        "target": exercise.get("target_type", "N/A"),
                        "reaction_time": exercise.get("reaction_time"),
                        "group_diameter": exercise.get("group_diameter"),
                        "observations": f"Cadencia: {exercise.get('firing_cadence', 'N/A')}, Tiempo límite: {exercise.get('time_limit', 'N/A')}",
                    }
                )

        return exercises

    def _map_practice_type_to_exercise(self, practice_type: str) -> str:
        """Mapear tipo de práctica a nombre de ejercicio"""
        mapping = {
            "precision": "Evaluación de Precisión",
            "reaction": "Evaluación de Reacción (Desenfunde)",
            "movement": "Tiro en Movimiento",
            "transition": "Transición de Armas",
            "barricade": "Tiro con Barricadas",
            "vehicle": "Reacción en Vehículos",
            "multiple_targets": "Blancos Múltiples",
            "distance": "Tiro a Distancia",
        }
        return mapping.get(practice_type.lower(), f"Ejercicio: {practice_type}")

    def _get_classification_text(self, level):
        # Si level es un Enum, devuelve su valor legible
        if level is None:
            return "Sin clasificar"
        try:
            return level.value
        except AttributeError:
            return str(level)

    def _validate_report_data(self, report_data: ReportData) -> bool:
        """Validar que los datos del reporte sean suficientes"""
        print("🔍 VALIDANDO DATOS DEL REPORTE:")
        print(f"  - Shooter info: {bool(report_data.shooter_info)}")
        print(f"  - Sessions: {len(report_data.sessions)}")
        print(f"  - Statistics: {bool(report_data.statistics)}")
        print(f"  - Evaluations: {len(report_data.evaluations)}")
        print(f"  - Exercises: {len(report_data.exercises)}")

        if report_data.shooter_info:
            print(f"  - Nombre completo: {report_data.shooter_info.get('full_name')}")
            print(
                f"  - Clasificación: {report_data.shooter_info.get('classification')}"
            )

        return True

    def _get_exercises_with_images(
        self, sessions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Obtener ejercicios que tienen imágenes con análisis"""
        exercises_with_images = []

        for session in sessions:
            for exercise in session.get("exercises", []):
                if exercise.get("has_target_image"):
                    # Obtener análisis de la imagen
                    image_analysis = self._get_exercise_image_analysis(exercise["id"])
                    if image_analysis:
                        exercise_data = {
                            **exercise,
                            "image_analysis": image_analysis,
                            "session_date": session.get("date"),
                            "session_location": session.get("location"),
                        }
                        exercises_with_images.append(exercise_data)

        return exercises_with_images

    def _get_exercise_image_analysis(
        self, exercise_id: str
    ) -> Optional[Dict[str, Any]]:
        """Obtener análisis de imagen de un ejercicio específico"""
        from src.infraestructure.database.models.practice_exercise_model import (
            PracticeExerciseModel,
        )
        from src.infraestructure.database.models.target_image_model import (
            TargetImageModel,
        )
        from sqlalchemy.orm import joinedload

        try:
            exercise = (
                self.db.query(PracticeExerciseModel)
                .options(
                    joinedload(PracticeExerciseModel.target_image).joinedload(
                        TargetImageModel.analyses
                    )
                )
                .filter(PracticeExerciseModel.id == exercise_id)
                .first()
            )

            if not exercise or not exercise.target_image:
                return None

            image = exercise.target_image
            if not image.analyses:
                return None

            analysis = image.analyses[0]  # Último análisis

            return {
                "analysis_id": str(analysis.id),
                "total_impacts": analysis.total_impacts_detected,
                "fresh_impacts_inside": analysis.fresh_impacts_inside,
                "fresh_impacts_outside": analysis.fresh_impacts_outside,
                "accuracy_percentage": analysis.accuracy_percentage,
                "total_score": analysis.total_score,
                "average_score_per_shot": analysis.average_score_per_shot,
                "max_score_achieved": analysis.max_score_achieved,
                "group_diameter": analysis.shooting_group_diameter,
                "group_center": analysis.group_center,
                "impact_coordinates": analysis.impact_coordinates,
                "score_distribution": analysis.score_distribution,
                "analysis_timestamp": analysis.analysis_timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo análisis de imagen: {e}")
            return None

    def _get_exercise_image_with_impacts(
        self, exercise_id: str, mode: str = "impacts"
    ) -> Optional[str]:
        """Generar imagen con impactos marcados y convertir a base64 para PDF"""
        from src.infraestructure.database.models.practice_exercise_model import (
            PracticeExerciseModel,
        )
        from src.infraestructure.database.models.target_image_model import (
            TargetImageModel,
        )
        from sqlalchemy.orm import joinedload

        try:
            exercise = (
                self.db.query(PracticeExerciseModel)
                .options(
                    joinedload(PracticeExerciseModel.target_image).joinedload(
                        TargetImageModel.analyses
                    )
                )
                .filter(PracticeExerciseModel.id == exercise_id)
                .first()
            )

            if not exercise or not exercise.target_image:
                return None

            image = exercise.target_image
            if not image.analyses or not image.analyses[0].impact_coordinates:
                return None

            analysis = image.analyses[0]

            # Descargar imagen
            if not image.file_path or not image.file_path.startswith("http"):
                return None

            response = requests.get(image.file_path)
            if response.status_code != 200:
                return None

            # Procesar imagen
            pil_image = PILImage.open(io.BytesIO(response.content)).convert("RGB")
            image_np = np.array(pil_image)
            h, w = image_np.shape[:2]

            # Dibujar impactos
            for impact in analysis.impact_coordinates:
                x = int(impact.get("centro_x", 0))
                y = int(impact.get("centro_y", 0))
                es_fresco = impact.get("es_fresco", False)

                # Color: verde para frescos, rojo para cubiertos
                color = (0, 255, 0) if es_fresco else (255, 0, 0)
                cv2.circle(image_np, (x, y), 15, color, thickness=3)

                # Información del impacto
                score = impact.get("scores", "-")
                zone = impact.get("zone", "-")

                info_text = f"Score: {score} | Zone: {zone}"
                cv2.putText(
                    image_np,
                    info_text,
                    (x + 20, y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

            # Convertir a base64
            result_image = PILImage.fromarray(image_np)
            buf = io.BytesIO()
            result_image.save(buf, format="JPEG", quality=85)
            buf.seek(0)

            return base64.b64encode(buf.getvalue()).decode("utf-8")

        except Exception as e:
            self.logger.error(f"❌ Error generando imagen con impactos: {e}")
            return None

    def _generate_analysis_images(self, sessions: List[Dict[str, Any]]) -> List[str]:
        """Generar imágenes de análisis basadas en las sesiones"""
        images = []

        try:
            # Obtener ejercicios con imágenes
            exercises_with_images = self._get_exercises_with_images(sessions)

            for exercise in exercises_with_images[:5]:  # Máximo 5 imágenes por reporte
                image_base64 = self._get_exercise_image_with_impacts(exercise["id"])
                if image_base64:
                    images.append(
                        {
                            "image_data": image_base64,
                            "exercise_name": exercise.get("exercise_type", "Ejercicio"),
                            "session_date": exercise.get("session_date"),
                            "analysis": exercise.get("image_analysis", {}),
                        }
                    )

        except Exception as e:
            self.logger.error(f"❌ Error generando imágenes de análisis: {e}")

        return images
