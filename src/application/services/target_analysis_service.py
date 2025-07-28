import requests
from io import BytesIO
from PIL import Image
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from uuid import UUID
from typing import Optional, Tuple, List, Any
import logging

from src.infraestructure.ml_models import get_bullet_detector, BulletDetectorError
from src.infraestructure.database.session import get_db
from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository,
)
from src.infraestructure.database.repositories.target_analysis_repo import (
    TargetAnalysisRepository,
)
from src.infraestructure.database.models.target_analysis_model import (
    TargetAnalysisModel,
)
from src.presentation.schemas.target_analysis_schema import *
from src.application.services.exercise_consolidation import ExerciseConsolidationService
from src.presentation.schemas.exercise_consolidation import (
    ExerciseConsolidationResult,
    ExerciseConsolidationStatus,
)

from src.domain.entities.scoring import ShotCoordinate
from src.application.services.scoring_calculator import ScoringCalculatorService
from src.application.services.detection_converter import DetectionConverter
from src.domain.value_objects.target_config import TargetConfigurations, TargetType
from src.domain.validator.target_analysis_validators import TargetAnalysisValidator

logger = logging.getLogger(__name__)


class TargetAnalysisService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.detector = get_bullet_detector()
        self.consolidation_service = ExerciseConsolidationService(self.db)

        # servicios de puntuacion
        self.scoring_calculator = ScoringCalculatorService(
            TargetConfigurations.PRO_SHOOTER
        )
        self.detection_converter = DetectionConverter()

    def analyze_exersise_image(
        self,
        exercise_id: UUID,
        confidence_threshold: float = 0.25,
        force_reanalysis: bool = False,
        enable_scoring: bool = True,
    ) -> tuple[Optional[ExerciseAnalysisResponse], Optional[str]]:
        """
        Método mejorado que mantiene compatibilidad total con la versión existente
        y agrega cálculo de puntuación opcional

        Args:
            exercise_id: ID del ejercicio
            confidence_threshold: Umbral de confianza para detección
            force_reanalysis: Forzar nuevo análisis
            enable_scoring: Si calcular puntuación (nuevo parámetro opcional)
        """
        try:
            # obtener ejercicio con imagen
            exercise = PracticeExerciseRepository.get_by_id(self.db, exercise_id)
            if not exercise or not exercise.target_image:
                return None, "EXERCISE_OR_IMAGE_NOT_FOUND"

            # verificar si ya existe analisis
            existing_analysis = self._get_latest_analysis(exercise.target_image.id)
            if existing_analysis and not force_reanalysis:
                return self._build_response_from_db(existing_analysis), None

            # descargar imagen desde S3
            image_bytes = self._download_image_from_s3(exercise.target_image.file_path)

            # obtener dimensieons de imagen
            image_width, image_height = self._get_image_dimensions(image_bytes)

            # validar formato de imagen si scoring está habilitado
            if enable_scoring:
                is_valid, error_msg = TargetAnalysisValidator.validate_image_format(
                    image_height=image_height, image_width=image_width
                )
                if not is_valid:
                    logger.warning(f"⚠️ Imagen no optima para puntuacion: {error_msg}")
                    # no fallar solo registrar warning
            #  procesar con el modelo YOLO
            analysis_result = self.detector.analyze_with_stats(
                image_data=image_bytes, confidence_threshold=confidence_threshold
            )

            detections = analysis_result["detections"]
            stats = analysis_result["statistics"]

            # preparar datos basicos
            basic_analysis_data = self._prepare_analysis_data(
                stats=stats,
                detections=detections,
                confidence_threshold=confidence_threshold,
            )

            # calcular puntiaciones si esta habilitado
            scoring_data = None
            enhanced_detections = detections  # por defecto usar detecciones originales
            if enable_scoring:
                try:
                    scoring_data, enhanced_detections = self._calculate_scoring_data(
                        detections, image_width, image_height
                    )
                    logger.info(
                        f"✅ Puntuación calculada: {scoring_data.get("total_score", 0)} puntos"
                    )
                except Exception as e:
                    logger.error(f"❌ Error al calcular puntuación: {str(e)}")
                    # no fallar el analisis completo
            if existing_analysis:
                db_analysis = self._update_analysis_with_scoring(
                    existing_analysis.id, basic_analysis_data, scoring_data
                )
            else:
                db_analysis = self._create_analysis_with_scoring(
                    exercise.target_image.id, basic_analysis_data, scoring_data
                )

            # consolidacion
            consolidation_result = self._conslidate_exercise_after_analysis(exercise_id)

            response = self._build_enhanced_response(
                exercise_id, db_analysis, enhanced_detections
            )

            # agregar info de consolidacion
            if consolidation_result:
                response.consolidation_info = {
                    "ammunition_validation_status": consolidation_result.ammunition_validation.status,
                    "warning": consolidation_result.ammunition_validation.warning,
                    "needs_manual_review": consolidation_result.ammunition_validation.needs_manual_review,
                }

            return response, None

        except BulletDetectorError as e:
            return None, f"DETECTION_ERROR: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Error en análisis mejorado: {str(e)}")
            return None, f"ENHANCED_ANALYSIS_ERROR: {str(e)}"

    def analyze_exersise_image(
        self,
        exercise_id: UUID,
        confidence_threshold: float = 0.25,
        force_reanalysis: bool = False,
    ) -> Tuple[Optional[ExerciseAnalysisResponse], Optional[str]]:
        """
        Método de compatibilidad que mantiene la firma exacta del servicio original
        Redirige al método mejorado con scoring habilitado por defecto
        """
        return self.analyze_exersise_image(
            exercise_id=exercise_id,
            confidence_threshold=confidence_threshold,
            force_reanalysis=force_reanalysis,
            enable_scoring=True,  # Habilitar puntuación por defecto
        )

    def get_exercise_analysis(
        self, exercise_id: UUID
    ) -> Tuple[Optional[ExerciseAnalysisResponse], Optional[str]]:
        try:
            exercise = PracticeExerciseRepository.get_by_id(self.db, exercise_id)
            if not exercise or not exercise.target_image:
                return None, "EXERCISE_OR_IMAGE_NOT_FOUND"

            existing_analysis = self._get_latest_analysis(exercise.target_image.id)
            if not existing_analysis:
                return None, "ANALYSIS_NOT_FOUND"

            response = self._build_response_from_db(existing_analysis)
            return response, None
        except Exception as e:
            return None, f"ANALYSIS_RETRIEVAL_ERROR: {str(e)}"

    def _download_image_from_s3(self, s3_path: str) -> bytes:
        """Descarga la imagen desde S3 y la devuelve como bytes."""
        s3_url = f"{s3_path}"
        response = requests.get(s3_url)
        response.raise_for_status()
        return response.content

    def _process_detections(
        self, detections: List, confidence_threshold: float
    ) -> dict:
        """Procesa las detecciones del modelo y calcula estadísticas"""

        # Separar por tipos
        fresh_inside = [d for d in detections if d["es_fresco"] and d["dentro_blanco"]]
        fresh_outside = [
            d for d in detections if d["es_fresco"] and not d["dentro_blanco"]
        ]
        covered_inside = [
            d for d in detections if not d["es_fresco"] and d["dentro_blanco"]
        ]
        covered_outside = [
            d for d in detections if not d["es_fresco"] and not d["dentro_blanco"]
        ]

        total_fresh = len(fresh_inside) + len(fresh_outside)
        accuracy = (len(fresh_inside) / total_fresh * 100) if total_fresh > 0 else 0.0

        # Estadísticas de confianza
        all_confidences = [d["confianza"] for d in detections]
        confidence_stats = {
            "promedio": np.mean(all_confidences) if all_confidences else 0.0,
            "minimo": min(all_confidences) if all_confidences else 0.0,
            "maximo": max(all_confidences) if all_confidences else 0.0,
            "desviacion_estandar": np.std(all_confidences) if all_confidences else 0.0,
        }

        return {
            "total_impacts_detected": len(detections),
            "fresh_impacts_inside": len(fresh_inside),
            "fresh_impacts_outside": len(fresh_outside),
            "covered_impacts_inside": len(covered_inside),
            "covered_impacts_outside": len(covered_outside),
            "accuracy_percentage": accuracy,
            "average_confidence": confidence_stats["promedio"],
            "impact_coordinates": detections,
            "confidence_stats": confidence_stats,
            "confidence_threshold": confidence_threshold,
        }

    def _save_analysis_to_db(
        self, target_image_id: UUID, analysis_data: dict
    ) -> TargetAnalysisModel:
        """Guarda el análisis en la base de datos"""

        analysis_dict = {
            "target_image_id": target_image_id,
            "total_impacts_detected": analysis_data["total_impacts_detected"],
            "fresh_impacts_inside": analysis_data["fresh_impacts_inside"],
            "fresh_impacts_outside": analysis_data["fresh_impacts_outside"],
            "covered_impacts_inside": analysis_data["covered_impacts_inside"],
            "covered_impacts_outside": analysis_data["covered_impacts_outside"],
            "accuracy_percentage": analysis_data["accuracy_percentage"],
            "average_confidence": analysis_data["average_confidence"],  # ← CAMBIAR AQUÍ
            "impact_coordinates": analysis_data["impact_coordinates"],
            "confidence_stats": analysis_data["confidence_stats"],
            "analysis_method": analysis_data["analysis_method"],
            "model_version": analysis_data["model_version"],
            "confidence_threshold": analysis_data["confidence_threshold"],
        }

        return TargetAnalysisRepository.create(self.db, analysis_dict)

    def _get_latest_analysis(
        self, target_image_id: UUID
    ) -> Optional[TargetAnalysisModel]:
        """Obtiene el análisis más reciente para una imagen de blanco"""
        return (
            self.db.query(TargetAnalysisModel)
            .filter(TargetAnalysisModel.target_image_id == target_image_id)
            .order_by(TargetAnalysisModel.analysis_timestamp.desc())
            .first()
        )

    def _prepare_analysis_data(
        self, stats: dict, detections: list, confidence_threshold: float
    ) -> dict:
        """Prepara los datos para guardar en BD usando estadísticas ya calculadas"""
        return {
            "total_impacts_detected": stats["total_impacts"],
            "fresh_impacts_inside": stats["fresh_impacts_inside"],
            "fresh_impacts_outside": stats["fresh_impacts_outside"],
            "covered_impacts_inside": stats["covered_impacts_inside"],
            "covered_impacts_outside": stats["covered_impacts_outside"],
            "accuracy_percentage": stats["accuracy_percentage"],
            "average_confidence": stats["average_confidence"],
            "impact_coordinates": detections,
            "confidence_stats": stats["confidence_stats"],
            "confidence_threshold": confidence_threshold,
            "analysis_method": "YOLO_v8",
            "model_version": "1.0",
        }

    def _build_response_from_db(
        self, db_analysis: TargetAnalysisModel
    ) -> ExerciseAnalysisResponse:
        """Construye respuesta usando datos existentes de la BD"""
        exercise_id = db_analysis.target_image.exercise.id

        # Recalcular precisión si está en 0 pero hay datos
        precision_porcentaje = db_analysis.accuracy_percentage
        if precision_porcentaje == 0.0:
            total_frescos = (
                db_analysis.fresh_impacts_inside + db_analysis.fresh_impacts_outside
            )
            if total_frescos > 0:
                precision_porcentaje = (
                    db_analysis.fresh_impacts_inside / total_frescos
                ) * 100

        return ExerciseAnalysisResponse(
            exercise_id=exercise_id,
            analysis_id=db_analysis.id,
            analysis_timestamp=db_analysis.analysis_timestamp,
            total_impactos_detectados=db_analysis.total_impacts_detected,
            impactos_frescos_dentro=db_analysis.fresh_impacts_inside,
            impactos_frescos_fuera=db_analysis.fresh_impacts_outside,
            impactos_tapados_dentro=db_analysis.covered_impacts_inside,
            impactos_tapados_fuera=db_analysis.covered_impacts_outside,
            precision_porcentaje=precision_porcentaje,  # ← Usar valor recalculado
            coordenadas_impactos=db_analysis.impact_coordinates or [],
            estadisticas_confianza=db_analysis.confidence_stats or {},
            modelo_version=db_analysis.model_version or "1.0",
            umbral_confianza=db_analysis.confidence_threshold or 0.25,
        )

    def _build_response(
        self, exercise_id: UUID, db_analysis: TargetAnalysisModel, detections: list
    ) -> ExerciseAnalysisResponse:
        """Construye la respuesta final del análisis"""
        return ExerciseAnalysisResponse(
            exercise_id=exercise_id,
            analysis_id=db_analysis.id,
            analysis_timestamp=db_analysis.analysis_timestamp,
            total_impactos_detectados=db_analysis.total_impacts_detected,
            impactos_frescos_dentro=db_analysis.fresh_impacts_inside,
            impactos_frescos_fuera=db_analysis.fresh_impacts_outside,
            impactos_tapados_dentro=db_analysis.covered_impacts_inside,
            impactos_tapados_fuera=db_analysis.covered_impacts_outside,
            precision_porcentaje=db_analysis.accuracy_percentage,
            coordenadas_impactos=detections,
            estadisticas_confianza=db_analysis.confidence_stats or {},
            modelo_version=db_analysis.model_version or "1.0",
            umbral_confianza=db_analysis.confidence_threshold or 0.25,
        )

    def _update_analysis_in_db(
        self, analysis_id: UUID, analysis_data: dict
    ) -> TargetAnalysisModel:
        """Actualiza un análisis existente en lugar de crear uno nuevo"""

        update_data = {
            "analysis_timestamp": datetime.now(),  # Actualizar timestamp
            "total_impacts_detected": analysis_data["total_impacts_detected"],
            "fresh_impacts_inside": analysis_data["fresh_impacts_inside"],
            "fresh_impacts_outside": analysis_data["fresh_impacts_outside"],
            "covered_impacts_inside": analysis_data["covered_impacts_inside"],
            "covered_impacts_outside": analysis_data["covered_impacts_outside"],
            "accuracy_percentage": analysis_data["accuracy_percentage"],
            "average_confidence": analysis_data["average_confidence"],
            "impact_coordinates": analysis_data["impact_coordinates"],
            "confidence_stats": analysis_data["confidence_stats"],
            "confidence_threshold": analysis_data["confidence_threshold"],
        }

        # Usar tu repository para actualizar
        return TargetAnalysisRepository.update(self.db, analysis_id, update_data)

    def _update_exercise_stats_fallback(self, exercise_id: UUID):
        exercise = PracticeExerciseRepository.get_by_id(self.db, exercise_id)
        if not exercise or not exercise.target_image:
            return

        # obtener el analisis
        analysis = self._get_latest_analysis(exercise.target_image.id)
        if not analysis:
            return

        total_fresh_shots = (
            analysis.fresh_impacts_inside + analysis.fresh_impacts_outside
        )
        hits = analysis.fresh_impacts_inside
        accuracy = (hits / total_fresh_shots * 100) if total_fresh_shots > 0 else 0.0

        update_data = {
            "ammunition_used": total_fresh_shots,
            "hits": hits,
            "accuracy_percentage": accuracy,
        }
        PracticeExerciseRepository.update(self.db, exercise_id, update_data)

    def _conslidate_exercise_after_analysis(
        self, exercise_id: UUID
    ) -> Optional[ExerciseConsolidationResult]:

        try:
            result = self.consolidation_service.update_exercise_from_analysis(
                exercise_id=exercise_id
            )

            if result.ammunition_validation.warning:
                logger.warning(
                    f"⚠️ Consolidación de ejercicio {exercise_id} con advertencia: {result.ammunition_validation.warning}"
                )

            return result

        except Exception as e:
            # si falla la consolicacion log de error pero no falla todo el analilsis
            logger.error(f"❌ Error al consolidar ejercicio {exercise_id}: {str(e)}")
            self._update_exercise_stats_fallback(exercise_id)
            return None

    def get_exercise_analysis_with_scoring(
        self, exercise_id: UUID
    ) -> Tuple[Optional[ExerciseAnalysisResponse], Optional[str]]:
        """Obtiene analisis existene con datos de puntuacion mejorados"""
        try:
            exercise = PracticeExerciseRepository.get_by_id(self.db, exercise_id)
            if not exercise or not exercise.target_image:
                return None, "EXERCISE_OR_IMAGE_NOT_FOUND"

            existing_analysis = self._get_latest_analysis(exercise.target_image.id)
            if not existing_analysis:
                return None, "ANALYSIS_NOT_FOUND"
            response = self._build_enhanced_response_from_db(existing_analysis)
            return response, None
        except Exception as e:
            logger.error(f"❌ Error al obtener análisis con puntuación: {str(e)}")
            return None, f"ANALYSIS_RETRIEVAL_ERROR: {str(e)}"

    def _get_image_dimensions(self, image_bytes: bytes) -> Tuple[int, int]:
        """Obtiene las dimensiones de la imagen"""
        pil_image = Image.open(BytesIO(image_bytes))
        return pil_image.size  # (width, height)

    def _calculate_scoring_data(
        self, detections: List[Dict], image_width: int, image_height: int
    ) -> Tuple[Dict[str, Any], List[Dict]]:
        """
        Calcula los datos de puntuación a partir de las detecciones
        y devuelve la puntuación total y las zonas de impacto.
        """
        # convertir detecciones a coordenadas de disparo
        shot_coordinates = self.detection_converter.detections_to_shot_coordinates(
            detections, only_fresh=True
        )

        # validar coordenadas
        is_valid, error_msg = TargetAnalysisValidator.validate_shot_coordinates(
            shot_coordinates, image_width, image_height
        )
        if not is_valid:
            logger.error(f"❌ Coordenadas de disparo inválidas: {error_msg}")
            raise ValueError(f"Invalid shot coordinates: {error_msg}")

        # calcular puntuaciones individuales
        shot_scores, score_distribution = (
            self.scoring_calculator.calculate_multiple_shots_score(
                shot_coordinates=shot_coordinates,
                image_width=image_width,
                image_height=image_height,
            )
        )

        # calcular estadisticas de grupo
        group_stats = self.scoring_calculator.calculate_group_statistics(
            shot_scores=shot_scores
        )

        # calcular metricas totales
        total_score = sum(shot.score for shot in shot_scores)
        avg_score = total_score / len(shot_scores) if shot_scores else 0.0
        max_score = max((shot.score for shot in shot_scores), default=0)

        # preparar datos de puntuacion
        scoring_data = {
            "total_score": total_score,
            "average_score_per_shot": avg_score,
            "max_score_achieved": max_score,
            "score_distribution": score_distribution,
            "shooting_group_diameter": group_stats.diameter,
            "group_center_x": group_stats.center_x,
            "group_center_y": group_stats.center_y,
        }

        enhanced_detections = self.detection_converter.shot_scores_to_detection_format(
            shot_scores=shot_scores
        )
        return scoring_data, enhanced_detections

    def _prepare_basic_analysis_data(
        self, stats: dict, detections: list, confidence_threshold: float
    ) -> dict:
        """Prepara datos básicos del análisis (método existente mejorado)"""
        return {
            "total_impacts_detected": stats["total_impacts"],
            "fresh_impacts_inside": stats["fresh_impacts_inside"],
            "fresh_impacts_outside": stats["fresh_impacts_outside"],
            "covered_impacts_inside": stats["covered_impacts_inside"],
            "covered_impacts_outside": stats["covered_impacts_outside"],
            "accuracy_percentage": stats["accuracy_percentage"],
            "average_confidence": stats["average_confidence"],
            "impact_coordinates": detections,
            "confidence_stats": stats["confidence_stats"],
            "confidence_threshold": confidence_threshold,
            "analysis_method": "YOLO_v8",
            "model_version": "1.0",
        }

    def _create_analysis_with_scoring(
        self, target_image_id: UUID, basic_data: dict, scoring_data: Optional[dict]
    ) -> TargetAnalysisModel:
        return TargetAnalysisRepository.create_with_scoring(
            self.db, target_image_id, basic_data, scoring_data
        )

    def _update_analysis_with_scoring(
        self, analysis_id: UUID, basic_data: dict, scoring_data: Optional[dict]
    ) -> TargetAnalysisModel:
        updated_analysis = TargetAnalysisRepository.update(
            self.db, analysis_id, basic_data
        )

        # actualizar datos de puntuacion si estan disponibles
        if scoring_data and updated_analysis:
            updated_analysis = TargetAnalysisRepository.update_scoring_data(
                self.db, analysis_id, scoring_data
            )
        return updated_analysis

    def _build_enhanced_response(
        self,
        exercise_id: UUID,
        db_analysis: TargetAnalysisModel,
        detections: List[Dict],
    ) -> ExerciseAnalysisResponse:
        """Construye respuesta mejorada con datos de puntuación"""

        # Calcular precisión si está en 0 pero hay datos (compatibilidad)
        precision_porcentaje = db_analysis.accuracy_percentage
        if precision_porcentaje == 0.0:
            total_frescos = (
                db_analysis.fresh_impacts_inside + db_analysis.fresh_impacts_outside
            )
            if total_frescos > 0:
                precision_porcentaje = (
                    db_analysis.fresh_impacts_inside / total_frescos
                ) * 100

        # Construir respuesta base (compatible)
        response = ExerciseAnalysisResponse(
            exercise_id=exercise_id,
            analysis_id=db_analysis.id,
            analysis_timestamp=db_analysis.analysis_timestamp,
            total_impactos_detectados=db_analysis.total_impacts_detected,
            impactos_frescos_dentro=db_analysis.fresh_impacts_inside,
            impactos_frescos_fuera=db_analysis.fresh_impacts_outside,
            impactos_tapados_dentro=db_analysis.covered_impacts_inside,
            impactos_tapados_fuera=db_analysis.covered_impacts_outside,
            precision_porcentaje=precision_porcentaje,
            coordenadas_impactos=detections,
            estadisticas_confianza=db_analysis.confidence_stats or {},
            modelo_version=db_analysis.model_version or "1.0",
            umbral_confianza=db_analysis.confidence_threshold or 0.25,
        )

        # ✅ AGREGAR campos de puntuación si están disponibles
        if db_analysis.has_scoring_data:
            # Agregar campos dinámicamente para mantener compatibilidad
            response.puntuacion_total = db_analysis.total_score
            response.puntuacion_promedio = db_analysis.average_score_per_shot
            response.puntuacion_maxima = db_analysis.max_score_achieved
            response.distribucion_puntuacion = db_analysis.score_distribution or {}
            response.diametro_grupo = db_analysis.shooting_group_diameter
            response.eficiencia_puntuacion = db_analysis.score_efficiency_percentage

            if db_analysis.group_center:
                response.centro_grupo = db_analysis.group_center

        return response

    def _build_enhanced_response_from_db(
        self, db_analysis: TargetAnalysisModel
    ) -> ExerciseAnalysisResponse:
        """Construye respuesta desde datos existentes en BD"""
        exercise_id = db_analysis.target_image.exercise.id
        detections = db_analysis.impact_coordinates or []

        return self._build_enhanced_response(exercise_id, db_analysis, detections)
