# 1. EXTENDER EL SERVICIO EXISTENTE SIN ROMPER NADA
# src/application/services/enhanced_target_analysis_service.py

import logging
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import numpy as np
import requests
from fastapi import Depends, HTTPException
from PIL import Image
from sqlalchemy.orm import Session

from src.application.services.detection_converter import DetectionConverter
from src.application.services.exercise_consolidation import ExerciseConsolidationService
from src.application.services.scoring_calculator import ScoringCalculatorService

# Nuevas importaciones para puntuación
from src.domain.entities.scoring import ShotCoordinate
from src.domain.services.distance_based_scoring import DistanceBasedScoringService
from src.domain.validator.target_analysis_validators import TargetAnalysisValidator
from src.domain.value_objects.target_config import TargetConfigurations, TargetType
from src.infraestructure.database.models.target_analysis_model import (
    TargetAnalysisModel,
)
from src.infraestructure.database.repositories.practice_exercise_repo import (
    PracticeExerciseRepository,
)
from src.infraestructure.database.repositories.target_analysis_repo import (
    TargetAnalysisRepository,
)
from src.infraestructure.database.session import get_db

# Importaciones existentes (mantener)
from src.infraestructure.ml_models import BulletDetectorError, get_bullet_detector
from src.presentation.schemas.target_analysis_schema import ExerciseAnalysisResponse

logger = logging.getLogger(__name__)


class EnhancedTargetAnalysisService:
    """
    Servicio mejorado que mantiene 100% compatibilidad con el servicio existente
    y agrega funcionalidad de puntuación
    """

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.detector = get_bullet_detector()
        self.consolidation_service = ExerciseConsolidationService(self.db)

        # ✅ NUEVOS: Servicios de puntuación
        self.scoring_calculator = ScoringCalculatorService(
            TargetConfigurations.PRO_SHOOTER
        )
        self.detection_converter = DetectionConverter()
        self.distance_scoring = DistanceBasedScoringService(max_distance_ratio=1.0)

    # ✅ MÉTODO PRINCIPAL MEJORADO (compatible con el existente)
    def analyze_exercise_image(
        self,
        exercise_id: UUID,
        confidence_threshold: float = 0.25,
        force_reanalysis: bool = False,
        enable_scoring: bool = True,  # NUEVO: Parámetro opcional para activar puntuación
        scoring_method: str = "linear",  # NUEVO: Método de puntuación ("linear", "exponential", "zones")
    ) -> Tuple[Optional[ExerciseAnalysisResponse], Optional[str]]:
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
            # 1. Obtener ejercicio con imagen (igual que antes)
            exercise = PracticeExerciseRepository.get_by_id(
                self.db, exercise_id=exercise_id
            )
            if not exercise or not exercise.target_image:
                return None, "EXERCISE_OR_IMAGE_NOT_FOUND"

            # 2. Verificar si ya existe análisis (igual que antes)
            existing_analysis = self._get_latest_analysis(exercise.target_image.id)
            if existing_analysis and not force_reanalysis:
                return self._build_enhanced_response_from_db(existing_analysis), None

            # 3. Descargar imagen desde S3 (igual que antes)
            image_bytes = self._download_image_from_s3(exercise.target_image.file_path)

            # 4. Obtener dimensiones de imagen (NUEVO para validación)
            image_width, image_height = self._get_image_dimensions(image_bytes)

            # 5. Validar formato de imagen si scoring está habilitado
            if enable_scoring:
                is_valid, error_msg = TargetAnalysisValidator.validate_image_format(
                    image_width, image_height
                )
                if not is_valid:
                    logger.warning(f"Imagen no óptima para puntuación: {error_msg}")
                    # No fallar, solo registrar warning

            # 6. Procesar con el modelo YOLO (igual que antes)
            analysis_result = self.detector.analyze_with_stats(
                image_data=image_bytes, confidence_threshold=confidence_threshold
            )

            detections = analysis_result["detections"]
            stats = analysis_result["statistics"]

            # 7. Preparar datos básicos (con impactos enriquecidos si hay scoring)
            scoring_data = None
            enhanced_detections = detections  # Por defecto, usar detecciones originales

            if enable_scoring:
                try:
                    scoring_data, enhanced_detections = self._calculate_scoring_data(
                        detections, image_width, image_height, scoring_method
                    )
                    logger.info(
                        f"📄 Puntuación calculada: {scoring_data.get('total_score', 0)} puntos"
                    )
                except Exception as e:
                    logger.error(f"❌ Error calculando puntuación: {str(e)}")
                    # No fallar el análisis completo, continuar sin puntuación

            # Usar los impactos enriquecidos para guardar en BD
            basic_analysis_data = self._prepare_basic_analysis_data(
                stats, enhanced_detections, confidence_threshold
            )

            # 9. Guardar o actualizar en BD
            if existing_analysis:
                db_analysis = self._update_analysis_with_scoring(
                    existing_analysis.id, basic_analysis_data, scoring_data
                )
            else:
                db_analysis = self._create_analysis_with_scoring(
                    exercise.target_image.id, basic_analysis_data, scoring_data
                )

            # 10. Consolidación (igual que antes)
            consolidation_result = self._consolidate_exercise_after_analysis(
                exercise_id
            )

            # 11. Construir respuesta mejorada
            response = self._build_enhanced_response(
                exercise_id, db_analysis, enhanced_detections
            )

            # 12. Agregar info de consolidación (igual que antes)
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
            logger.error(f"Error en análisis mejorado: {str(e)}")
            return None, f"ENHANCED_ANALYSIS_ERROR: {str(e)}"

    # ✅ MÉTODO DE COMPATIBILIDAD TOTAL (mantener firma exacta del original)
    def analyze_excersise_image(
        self,
        exercise_id: UUID,
        confidence_threshold: float = 0.25,
        force_reanalysis: bool = False,
    ) -> Tuple[Optional[ExerciseAnalysisResponse], Optional[str]]:
        """
        Método de compatibilidad que mantiene la firma exacta del servicio original
        Redirige al método mejorado con scoring habilitado por defecto
        """
        return self.analyze_exercise_image(
            exercise_id=exercise_id,
            confidence_threshold=confidence_threshold,
            force_reanalysis=force_reanalysis,
            enable_scoring=True,  # Habilitar puntuación por defecto
        )

    # ✅ NUEVO: Método específico para obtener análisis con puntuación
    def get_exercise_analysis_with_scoring(
        self, exercise_id: UUID
    ) -> Tuple[Optional[ExerciseAnalysisResponse], Optional[str]]:
        """Obtiene análisis existente con datos de puntuación mejorados"""
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
            logger.error(f"Error obteniendo análisis: {str(e)}")
            return None, f"ANALYSIS_RETRIEVAL_ERROR: {str(e)}"

    # ✅ MÉTODOS AUXILIARES NUEVOS
    def _get_image_dimensions(self, image_bytes: bytes) -> Tuple[int, int]:
        """Obtiene dimensiones de la imagen"""
        pil_image = Image.open(BytesIO(image_bytes))
        return pil_image.size  # (width, height)

    def _calculate_scoring_data(
        self,
        detections: List[Dict],
        image_width: int,
        image_height: int,
        scoring_method: str = "linear",
    ) -> Tuple[Dict[str, Any], List[Dict]]:
        """
        Calcula datos de puntuación para las detecciones

        Returns:
            Tuple[scoring_data, enhanced_detections]
        """
        # Convertir detecciones a coordenadas de disparo
        shot_coordinates = self.detection_converter.detections_to_shot_coordinates(
            detections, only_fresh=True
        )

        if not shot_coordinates:
            return self._empty_scoring_data(), detections

        shot_scores = []
        score_distribution = {str(i): 0 for i in range(0, 11)}
        for coordinate in shot_coordinates:
            shot_score = self.distance_scoring.calculate_shot_score_by_distance(
                coordinate, image_width, image_height, scoring_method=scoring_method
            )
            shot_scores.append(shot_score)
            score_distribution[str(shot_score.score)] += 1

        gropu_stats = self.scoring_calculator.calculate_group_statistics(shot_scores)

        # calcular metricas totales
        total_score = sum(shot.score for shot in shot_scores)
        avg_score = total_score / len(shot_scores) if shot_scores else 0
        max_score = max((shot.score for shot in shot_scores), default=0)

        # preparar datos de puntuacion
        scoring_data = {
            "total_score": total_score,
            "average_score_per_shot": avg_score,
            "max_score_achieved": max_score,
            "score_distribution": score_distribution,
            "shooting_group_diameter": gropu_stats.diameter,
            "group_center_x": gropu_stats.center_x,
            "group_center_y": gropu_stats.center_y,
        }

        enhanced_detections = []
        for i, detection in enumerate(detections):
            if detection.get("es_fresco", False) and i < len(shot_scores):
                shot_score = shot_scores[i]
                enhanced_detection = {
                    **detection,
                    "scores": shot_score.score,  #
                    "zone": shot_score.zone,
                    "distance_from_center": shot_score.distance_from_center_pixels,
                    "distance_ratio": shot_score.distance_from_center_ratio,
                }
                enhanced_detections.append(enhanced_detection)
            else:
                enhanced_detections.append(detection)

        return scoring_data, enhanced_detections

    def _empty_scoring_data(self) -> Dict[str, Any]:
        """Datos vacíos cuando no hay disparos frescos"""
        return {
            "total_score": 0,
            "average_score_per_shot": 0.0,
            "max_score_achieved": 0,
            "score_distribution": {str(i): 0 for i in range(0, 11)},
            "shooting_group_diameter": 0.0,
            "group_center_x": 0.0,
            "group_center_y": 0.0,
        }

    def _prepare_basic_analysis_data(
        self, stats: dict, detections: list, confidence_threshold: float
    ) -> dict:
        """Prepara datos básicos del análisis (compatible con modelo v2)"""
        return {
            "total_impacts_detected": stats["total_impacts"],
            "fresh_impacts_inside": stats["fresh_impacts_inside"],
            "fresh_impacts_outside": stats["fresh_impacts_outside"],
            "covered_impacts_inside": stats.get(
                "covered_impacts_inside", 0
            ),  # ← usar .get() con default 0
            "covered_impacts_outside": stats.get(
                "covered_impacts_outside", 0
            ),  # ← usar .get() con default 0
            "accuracy_percentage": stats["accuracy_percentage"],
            "average_confidence": stats["average_confidence"],
            "impact_coordinates": detections,
            "confidence_stats": stats["confidence_stats"],
            "confidence_threshold": confidence_threshold,
            "analysis_method": "YOLO_v8",
            "model_version": "2.0",  # ← ACTUALIZAR versión
        }

    def _create_analysis_with_scoring(
        self, target_image_id: UUID, basic_data: dict, scoring_data: Optional[dict]
    ) -> TargetAnalysisModel:
        """Crea nuevo análisis con datos de puntuación opcionales"""
        return TargetAnalysisRepository.create_with_scoring(
            self.db, target_image_id, basic_data, scoring_data
        )

    def _update_analysis_with_scoring(
        self, analysis_id: UUID, basic_data: dict, scoring_data: Optional[dict]
    ) -> TargetAnalysisModel:
        """Actualiza análisis existente con datos de puntuación"""
        # Actualizar datos básicos
        updated_analysis = TargetAnalysisRepository.update(
            self.db, analysis_id, basic_data
        )

        # Actualizar datos de puntuación si están disponibles
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

    # ✅ MÉTODOS EXISTENTES MANTENIDOS (compatibilidad)
    def get_exercise_analysis(
        self, exercise_id: UUID
    ) -> Tuple[Optional[ExerciseAnalysisResponse], Optional[str]]:
        """Método de compatibilidad con el servicio original"""
        return self.get_exercise_analysis_with_scoring(exercise_id)

    def _download_image_from_s3(self, s3_path: str) -> bytes:
        """Descarga imagen desde S3 (método existente)"""
        s3_url = f"{s3_path}"
        response = requests.get(s3_url)
        response.raise_for_status()
        return response.content

    def _get_latest_analysis(
        self, target_image_id: UUID
    ) -> Optional[TargetAnalysisModel]:
        """Obtiene análisis más reciente (método existente)"""
        return TargetAnalysisRepository.get_by_image_id(self.db, target_image_id)

    def _consolidate_exercise_after_analysis(self, exercise_id: UUID):
        """Consolidación después del análisis (método existente)"""
        try:
            result = self.consolidation_service.update_exercise_from_analysis(
                exercise_id=exercise_id
            )
            if result and result.ammunition_validation.warning:
                logger.warning(
                    f"Consolidación con advertencia: {result.ammunition_validation.warning}"
                )
            return result
        except Exception as e:
            logger.error(f"Error en consolidación: {str(e)}")
            return None
