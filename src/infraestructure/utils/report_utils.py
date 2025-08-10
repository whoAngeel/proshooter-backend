from typing import Dict, List, Any, Optional


class ReportUtils:
    """Utilidades adicionales para reportes"""

    @staticmethod
    def calculate_improvement_percentage(old_value: float, new_value: float) -> float:
        """Calcular porcentaje de mejora"""
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100

    @staticmethod
    def get_performance_trend(
        sessions: List[Dict[str, Any]], metric: str = "accuracy"
    ) -> str:
        """Determinar tendencia de rendimiento"""
        if len(sessions) < 3:
            return "Insuficientes datos"

        values = [session.get(metric, 0) for session in sessions[-5:]]

        # Calcular tendencia simple
        first_half = sum(values[: len(values) // 2]) / max(len(values) // 2, 1)
        second_half = sum(values[len(values) // 2 :]) / max(
            len(values) - len(values) // 2, 1
        )

        difference = second_half - first_half

        if difference > 5:
            return "Tendencia Ascendente"
        elif difference < -5:
            return "Tendencia Descendente"
        else:
            return "Tendencia Estable"

    @staticmethod
    def get_recommendations(accuracy: float, consistency: float) -> List[str]:
        """Generar recomendaciones basadas en rendimiento"""
        recommendations = []

        if accuracy < 70:
            recommendations.append("Enfocarse en ejercicios de precisión básicos")
            recommendations.append(
                "Revisar fundamentos de tiro (postura, empuñe, respiración)"
            )

        if consistency < 60:
            recommendations.append("Practicar ejercicios de consistencia")
            recommendations.append("Trabajar en rutina de pre-disparo")

        if accuracy >= 90:
            recommendations.append(
                "Nivel experto alcanzado - mantener práctica regular"
            )
            recommendations.append("Considerar ejercicios de tiro avanzado")

        return recommendations
