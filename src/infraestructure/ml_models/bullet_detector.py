import os
import io
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image
import cv2
from ultralytics import YOLO
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class BulletDetectorError(Exception):
    """Excepción personalizada para errores del detector"""

    pass


class BulletDetector:
    """
    Detector de impactos de bala usando modelo YOLO entrenado.
    Implementa patrón Singleton para evitar cargar el modelo múltiples veces.
    """

    _instance = None
    _model = None
    _model_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # No cargar el modelo en __init__, hacerlo lazy
        pass

    def _ensure_model_loaded(self):
        """Carga el modelo solo cuando se necesite (lazy loading)"""
        if not self._model_loaded:
            self._load_model()

    def _load_model(self):
        """Carga el modelo YOLO desde el archivo .pt"""
        try:
            # Ruta relativa al modelo
            current_dir = Path(__file__).parent
            model_path = current_dir / "models_versions" / "BulletDetector_v1.pt"

            # Debug: mostrar rutas para diagnóstico
            logger.info(f"Directorio actual: {current_dir}")
            logger.info(f"Buscando modelo en: {model_path}")
            logger.info(f"Archivo existe: {model_path.exists()}")

            # Listar archivos en el directorio para debug
            if current_dir.exists():
                logger.info(f"Archivos en {current_dir}: {list(current_dir.iterdir())}")
                models_dir = current_dir / "models_versions"
                if models_dir.exists():
                    logger.info(
                        f"Archivos en models_versions: {list(models_dir.iterdir())}"
                    )

            if not model_path.exists():
                raise BulletDetectorError(f"Modelo no encontrado en: {model_path}")

            logger.info(f"Cargando modelo desde: {model_path}")
            self._model = YOLO(str(model_path))
            self._model_loaded = True

            # Verificar que el modelo tiene las clases esperadas
            expected_classes = [
                "impacto_fresco_dentro",
                "impacto_fresco_fuera",
                "impacto_tapado_dentro",
                "impacto_tapado_fuera",
            ]

            model_classes = list(self._model.names.values())
            logger.info(f"Clases del modelo: {model_classes}")

            # Verificar compatibilidad (al menos las clases principales)
            if not any("fresco" in cls for cls in model_classes):
                logger.warning("Modelo podría no tener las clases esperadas")

            logger.info("Modelo cargado exitosamente")

        except Exception as e:
            logger.error(f"Error cargando modelo: {str(e)}")
            print(f"DETECTION_ERROR: No se pudo cargar el modelo: {str(e)}")
            raise BulletDetectorError(f"No se pudo cargar el modelo: {str(e)}")

    def _preprocess_image(self, image_data: bytes) -> np.ndarray:
        """
        Preprocesa los datos de imagen para el modelo.

        Args:
            image_data: Bytes de la imagen

        Returns:
            numpy array de la imagen en formato RGB
        """
        try:
            # Convertir bytes a imagen PIL
            image = Image.open(io.BytesIO(image_data))

            # Convertir a RGB si es necesario
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Convertir a numpy array
            image_array = np.array(image)

            return image_array

        except Exception as e:
            raise BulletDetectorError(f"Error procesando imagen: {str(e)}")

    def detect_impacts(
        self, image_data: bytes, confidence_threshold: float = 0.25
    ) -> List[Dict]:
        """
        Detecta impactos en una imagen de blanco de tiro.

        Args:
            image_data: Datos binarios de la imagen
            confidence_threshold: Umbral mínimo de confianza para detecciones

        Returns:
            Lista de diccionarios con información de cada impacto detectado
        """

        # Cargar modelo si no está cargado (lazy loading)
        self._ensure_model_loaded()

        try:
            # Preprocesar imagen
            image_array = self._preprocess_image(image_data)

            # Ejecutar detección
            results = self._model.predict(
                source=image_array, conf=confidence_threshold, verbose=False
            )

            # Procesar resultados
            detections = self._process_predictions(results[0])

            logger.info(
                f"Detectados {len(detections)} impactos con confianza >= {confidence_threshold}"
            )

            return detections

        except BulletDetectorError:
            raise
        except Exception as e:
            logger.error(f"Error en detección: {str(e)}")
            raise BulletDetectorError(f"Error durante la detección: {str(e)}")

    def _process_predictions(self, prediction_result) -> List[Dict]:
        """
        Procesa los resultados de predicción del modelo YOLO.

        Args:
            prediction_result: Resultado de predicción de YOLO

        Returns:
            Lista de detecciones procesadas
        """
        detections = []

        if prediction_result.boxes is None:
            return detections

        boxes = prediction_result.boxes

        for i in range(len(boxes)):
            # Información básica de la detección
            clase_id = int(boxes.cls[i])
            confianza = float(boxes.conf[i])
            x1, y1, x2, y2 = boxes.xyxy[i].tolist()
            nombre_clase = self._model.names[clase_id]

            # Calcular centro del impacto
            centro_x = (x1 + x2) / 2
            centro_y = (y1 + y2) / 2

            # Clasificar el impacto usando las etiquetas del modelo
            es_fresco = "fresco" in nombre_clase.lower()
            dentro_blanco = "dentro" in nombre_clase.lower()

            # Crear objeto de detección
            detection = {
                "tipo": nombre_clase,
                "confianza": confianza,
                "centro_x": centro_x,
                "centro_y": centro_y,
                "bbox": [x1, y1, x2, y2],
                "es_fresco": es_fresco,
                "dentro_blanco": dentro_blanco,
                "area": (x2 - x1) * (y2 - y1),
            }

            detections.append(detection)

        return detections

    def get_model_info(self) -> Dict:
        """
        Retorna información sobre el modelo cargado.

        Returns:
            Diccionario con metadatos del modelo
        """
        if not self._model_loaded:
            try:
                self._ensure_model_loaded()
            except:
                return {"status": "not_loaded", "error": "Failed to load model"}

        return {
            "status": "loaded",
            "model_type": "YOLOv8",
            "classes": list(self._model.names.values()),
            "num_classes": len(self._model.names),
            "version": "1.0",
        }

    def validate_image(self, image_data: bytes) -> Tuple[bool, Optional[str]]:
        """
        Valida que la imagen sea procesable por el modelo.

        Args:
            image_data: Datos binarios de la imagen

        Returns:
            Tupla (es_valida, mensaje_error)
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            # Verificar formato
            if image.format not in ["JPEG", "PNG", "BMP"]:
                return False, f"Formato no soportado: {image.format}"

            # Verificar dimensiones mínimas
            width, height = image.size
            if width < 100 or height < 100:
                return False, f"Imagen muy pequeña: {width}x{height}"

            # Verificar dimensiones máximas (para evitar problemas de memoria)
            if width > 5000 or height > 5000:
                return False, f"Imagen muy grande: {width}x{height}"

            return True, None

        except Exception as e:
            return False, f"Error validando imagen: {str(e)}"

    def analyze_with_stats(
        self, image_data: bytes, confidence_threshold: float = 0.25
    ) -> Dict:
        """
        Analiza imagen y retorna estadísticas detalladas.

        Args:
            image_data: Datos binarios de la imagen
            confidence_threshold: Umbral de confianza

        Returns:
            Diccionario con detecciones y estadísticas
        """
        # Validar imagen
        is_valid, error_msg = self.validate_image(image_data)
        if not is_valid:
            raise BulletDetectorError(f"Imagen inválida: {error_msg}")

        # Detectar impactos
        detections = self.detect_impacts(image_data, confidence_threshold)

        # Calcular estadísticas
        stats = self._calculate_statistics(detections)

        return {
            "detections": detections,
            "statistics": stats,
            "analysis_metadata": {
                "confidence_threshold": confidence_threshold,
                "total_detections": len(detections),
                "model_version": "1.0",
            },
        }

    def _calculate_statistics(self, detections: List[Dict]) -> Dict:
        """
        Calcula estadísticas detalladas de las detecciones.

        Args:
            detections: Lista de detecciones

        Returns:
            Diccionario con estadísticas calculadas
        """
        if not detections:
            return {
                "total_impacts": 0,
                "fresh_impacts_inside": 0,
                "fresh_impacts_outside": 0,
                "covered_impacts_inside": 0,
                "covered_impacts_outside": 0,
                "accuracy_percentage": 0.0,
                "average_confidence": 0.0,
                "confidence_stats": {"min": 0.0, "max": 0.0, "mean": 0.0, "std": 0.0},
            }

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
        confidences = [d["confianza"] for d in detections]
        confidence_stats = {
            "min": min(confidences),
            "max": max(confidences),
            "mean": np.mean(confidences),
            "std": np.std(confidences),
        }

        return {
            "total_impacts": total_fresh,
            "fresh_impacts_inside": len(fresh_inside),
            "fresh_impacts_outside": len(fresh_outside),
            "covered_impacts_inside": len(covered_inside),
            "covered_impacts_outside": len(covered_outside),
            "accuracy_percentage": accuracy,
            "average_confidence": float(confidence_stats["mean"]),
            "confidence_stats": {
                "min": float(confidence_stats["min"]),
                "max": float(confidence_stats["max"]),
                "mean": float(confidence_stats["mean"]),
                "std": float(confidence_stats["std"]),
            },
        }


# NO crear instancia global en import
# bullet_detector = BulletDetector()  # ← Comentado


def get_bullet_detector() -> BulletDetector:
    """
    Función helper para obtener la instancia del detector.
    Útil para dependency injection en FastAPI.
    """
    return BulletDetector()  # Se crea cuando se necesita
