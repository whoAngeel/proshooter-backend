import io
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib import colors
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
from io import BytesIO
import logging

# matplotlib.use("Agg")  # Use a non-GUI backend for matplotlib
logger = logging.getLogger(__name__)

from src.presentation.schemas.reports import ReportData


class PDFReportGenerator:
    """Generador de reportes PDF para tiradores deportivos"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()

    def _create_custom_styles(self) -> Dict[str, ParagraphStyle]:
        """Crear estilos personalizados para el reporte"""
        return {
            "title": ParagraphStyle(
                "CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # Center
                textColor=colors.navy,
            ),
            "subtitle": ParagraphStyle(
                "CustomSubtitle",
                parent=self.styles["Heading2"],
                fontSize=14,
                spaceAfter=20,
                textColor=colors.darkblue,
            ),
            "normal_bold": ParagraphStyle(
                "NormalBold",
                parent=self.styles["Normal"],
                fontSize=10,
                fontName="Helvetica-Bold",
            ),
        }

    def generate_session_report(self, report_data: ReportData) -> bytes:
        """Generar reporte de sesión individual"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        # Título principal
        title = Paragraph("REPORTE DE SESIÓN DE PRÁCTICA", self.custom_styles["title"])
        story.append(title)
        story.append(Spacer(1, 20))

        # Información del tirador
        story.extend(self._add_shooter_info(report_data.shooter_info))
        story.append(Spacer(1, 20))

        # Información de la sesión
        if report_data.sessions:
            story.extend(self._add_session_details(report_data.sessions[0]))
            story.append(Spacer(1, 20))

        # Estadísticas
        story.extend(self._add_statistics_section(report_data.statistics))
        story.append(Spacer(1, 20))

        # Ejercicios realizados
        if report_data.exercises:
            story.extend(self._add_exercises_section(report_data.exercises))
            story.append(Spacer(1, 20))

        if report_data.analysis_images:
            story.extend(self._add_image_analysis_section(report_data.analysis_images))
            story.append(Spacer(1, 20))

        # Análisis de disparos con imágenes
        if report_data.include_analysis and report_data.analysis_images:
            story.extend(self._add_analysis_section(report_data.analysis_images))

        # Evaluaciones
        if report_data.evaluations:
            story.extend(self._add_evaluations_section(report_data.evaluations))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_monthly_report(self, report_data: ReportData) -> bytes:
        """Generar reporte mensual"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        # Título
        title = Paragraph(
            "REPORTE MENSUAL DE ENTRENAMIENTO", self.custom_styles["title"]
        )
        story.append(title)
        story.append(Spacer(1, 20))

        # Información del tirador
        story.extend(self._add_shooter_info(report_data.shooter_info))
        story.append(Spacer(1, 20))

        # Resumen estadístico
        story.extend(self._add_monthly_summary(report_data))
        story.append(Spacer(1, 20))

        story.extend(self._add_image_analysis_section(report_data.analysis_images))
        story.append(Spacer(1, 20))

        # Evolución del tirador
        story.extend(self._add_evolution_chart(report_data.sessions))
        story.append(Spacer(1, 20))

        # Tabla de sesiones
        story.extend(self._add_sessions_table(report_data.sessions))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _add_shooter_info(self, shooter_info: Dict[str, Any]) -> List:
        """Agregar información del tirador"""
        elements = []

        subtitle = Paragraph("INFORMACIÓN DEL TIRADOR", self.custom_styles["subtitle"])
        elements.append(subtitle)

        full_name = shooter_info.get("full_name", "N/A")

        data = [
            ["Nombre Completo:", full_name],
            ["Email:", shooter_info.get("email", "N/A")],
            ["Teléfono:", shooter_info.get("phone_number", "N/A")],
            ["Clasificación:", shooter_info.get("classification", "Sin clasificar")],
            ["Club:", shooter_info.get("club_name", "Sin club")],
            [
                "Ciudad:",
                f"{shooter_info.get('city', '')}, {shooter_info.get('state', '')}",
            ],
            ["País:", shooter_info.get("country", "N/A")],
            ["Fecha de Reporte:", datetime.now().strftime("%d/%m/%Y %H:%M")],
        ]

        table = Table(data, colWidths=[2.5 * inch, 4 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 1, colors.navy),
                ]
            )
        )

        elements.append(table)
        return elements

    def _add_session_details(self, session: Dict[str, Any]) -> List:
        """Agregar detalles de la sesión"""
        elements = []

        subtitle = Paragraph("DETALLES DE LA SESIÓN", self.custom_styles["subtitle"])
        elements.append(subtitle)

        data = [
            ["Fecha:", session.get("date", "N/A")],
            ["Ubicación:", session.get("location", "N/A")],
            ["Instructor:", session.get("instructor_name", "N/A")],
            ["Total de Disparos:", str(session.get("total_shots_fired", 0))],
            ["Impactos Totales:", str(session.get("total_hits", 0))],
            ["Precisión General:", f"{session.get('accuracy_percentage', 0):.1f}%"],
            ["Puntuación Total:", f"{session.get('total_session_score', 0)} pts"],
            [
                "Promedio por Ejercicio:",
                f"{session.get('average_score_per_exercise', 0):.1f} pts",
            ],
            ["Mejor Disparo:", f"{session.get('best_shot_score', 0)} pts"],
            ["Estado:", "Finalizada" if session.get("is_finished") else "En Progreso"],
        ]

        table = Table(data, colWidths=[2.5 * inch, 3.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 1, colors.darkblue),
                ]
            )
        )

        elements.append(table)
        return elements

    def _add_statistics_section(self, statistics: Dict[str, Any]) -> List:
        """Agregar sección de estadísticas"""
        elements = []

        subtitle = Paragraph("ESTADÍSTICAS DEL TIRADOR", self.custom_styles["subtitle"])
        elements.append(subtitle)

        # Clasificación actual
        classification_text = statistics.get("classification", "Sin clasificar")

        # Primera tabla - Estadísticas generales
        general_data = [
            ["Precisión Promedio:", f"{statistics.get('accuracy', 0):.1f}%"],
            ["Total de Sesiones:", str(statistics.get("total_sessions", 0))],
            ["Total de Disparos:", str(statistics.get("total_shots", 0))],
            ["Clasificación Actual:", classification_text],
            ["Puntuación Promedio:", f"{statistics.get('average_score', 0):.1f} pts"],
            ["Mejor Puntuación:", f"{statistics.get('best_score_session', 0)} pts"],
        ]

        general_table = Table(general_data, colWidths=[2.5 * inch, 3.5 * inch])
        general_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 1, colors.darkgreen),
                ]
            )
        )

        elements.append(general_table)
        elements.append(Spacer(1, 15))

        # Segunda tabla - Estadísticas por tipo de ejercicio
        subtitle2 = Paragraph(
            "RENDIMIENTO POR TIPO DE EJERCICIO", self.custom_styles["subtitle"]
        )
        elements.append(subtitle2)

        exercise_data = [
            ["Tipo de Ejercicio", "Precisión", "Puntuación Promedio"],
            [
                "Precisión",
                f"{statistics.get('precision_exercise_accuracy', 0):.1f}%",
                f"{statistics.get('precision_exercise_avg_score', 0):.1f} pts",
            ],
            [
                "Reacción",
                f"{statistics.get('reaction_exercise_accuracy', 0):.1f}%",
                f"{statistics.get('reaction_exercise_avg_score', 0):.1f} pts",
            ],
            [
                "Movimiento",
                f"{statistics.get('movement_exercise_accuracy', 0):.1f}%",
                f"{statistics.get('movement_exercise_avg_score', 0):.1f} pts",
            ],
        ]

        exercise_table = Table(exercise_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
        exercise_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        elements.append(exercise_table)
        elements.append(Spacer(1, 15))

        # Tercera tabla - Tendencias y tiempos
        subtitle3 = Paragraph("TENDENCIAS Y TIEMPOS", self.custom_styles["subtitle"])
        elements.append(subtitle3)

        trends_data = [
            ["Tendencia de Precisión:", f"{statistics.get('trend_accuracy', 0):.1f}%"],
            [
                "Promedio Últimas 10 Sesiones:",
                f"{statistics.get('last_10_sessions_avg', 0):.1f}%",
            ],
            [
                "Tiempo Promedio Desenfunde:",
                f"{statistics.get('draw_time_avg', 0):.2f}s",
            ],
            [
                "Tiempo Promedio Recarga:",
                f"{statistics.get('reload_time_avg', 0):.2f}s",
            ],
            [
                "Factor de Impacto Promedio:",
                f"{statistics.get('average_hit_factor', 0):.2f}",
            ],
            ["Efectividad General:", f"{statistics.get('effectiveness', 0):.1f}%"],
        ]

        trends_table = Table(trends_data, colWidths=[3 * inch, 2 * inch])
        trends_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 1, colors.blue),
                ]
            )
        )

        elements.append(trends_table)

        # Zonas de error comunes si están disponibles
        if statistics.get("common_error_zones"):
            elements.append(Spacer(1, 10))
            error_text = (
                f"Zonas de Error Comunes: {statistics.get('common_error_zones')}"
            )
            error_paragraph = Paragraph(error_text, self.styles["Normal"])
            elements.append(error_paragraph)

        elements.append(Spacer(1, 10))
        update_text = f"Última Actualización: {statistics.get('last_updated', 'N/A')}"
        update_paragraph = Paragraph(update_text, self.styles["Normal"])
        elements.append(update_paragraph)

        return elements

    def _add_exercises_section(self, exercises: List[Dict[str, Any]]) -> List:
        """Agregar sección de ejercicios"""
        elements = []

        subtitle = Paragraph("EJERCICIOS REALIZADOS", self.custom_styles["subtitle"])
        elements.append(subtitle)

        if not exercises:
            no_exercises = Paragraph(
                "No se encontraron ejercicios registrados.", self.styles["Normal"]
            )
            elements.append(no_exercises)
            return elements

        for i, exercise in enumerate(exercises, 1):
            # Título del ejercicio
            exercise_title = Paragraph(
                f"EJERCICIO {i}: {exercise.get('name', 'Ejercicio Desconocido')}",
                self.custom_styles["normal_bold"],
            )
            elements.append(exercise_title)
            elements.append(Spacer(1, 5))

            # Datos básicos del ejercicio
            basic_data = [
                ["Distancia:", f"{exercise.get('distance', 'N/A')}"],
                ["Arma:", exercise.get("weapon", "N/A")],
                ["Munición:", exercise.get("ammunition", "N/A")],
                ["Tipo de Blanco:", exercise.get("target", "N/A")],
            ]

            basic_table = Table(basic_data, colWidths=[1.5 * inch, 2.5 * inch])
            basic_table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )

            elements.append(basic_table)
            elements.append(Spacer(1, 5))

            # Resultados del ejercicio
            results_data = [
                ["Disparos Realizados:", str(exercise.get("shots", 0))],
                ["Impactos:", str(exercise.get("hits", 0))],
                ["Precisión:", f"{exercise.get('accuracy', 0):.1f}%"],
                ["Puntuación Total:", f"{exercise.get('score', 0)} pts"],
                ["Puntuación Máxima:", f"{exercise.get('max_score', 0)} pts"],
            ]

            # Agregar tiempo de reacción si está disponible
            if exercise.get("reaction_time"):
                results_data.append(
                    ["Tiempo de Reacción:", f"{exercise.get('reaction_time'):.3f}s"]
                )

            # Agregar diámetro de agrupación si está disponible
            if exercise.get("group_diameter"):
                results_data.append(
                    [
                        "Diámetro de Agrupación:",
                        f"{exercise.get('group_diameter'):.2f}mm",
                    ]
                )

            results_table = Table(results_data, colWidths=[2 * inch, 2 * inch])
            results_table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("BOX", (0, 0), (-1, -1), 1, colors.gray),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                    ]
                )
            )

            elements.append(results_table)

            # Observaciones
            if exercise.get("observations"):
                elements.append(Spacer(1, 5))
                obs_text = f"<b>Observaciones:</b> {exercise.get('observations')}"
                obs_paragraph = Paragraph(obs_text, self.styles["Normal"])
                elements.append(obs_paragraph)

            elements.append(Spacer(1, 15))

        return elements

    def _add_analysis_section(self, analysis_images: List[str]) -> List:
        """Agregar sección de análisis con imágenes"""
        elements = []

        subtitle = Paragraph("ANÁLISIS DE DISPAROS", self.custom_styles["subtitle"])
        elements.append(subtitle)

        # Generar imagen de análisis de blanco
        target_image = self._generate_target_analysis()
        if target_image:
            elements.append(target_image)
            elements.append(Spacer(1, 10))

        # Agregar texto de análisis
        analysis_text = """
        ANÁLISIS DE PATRONES DE DISPARO:

        Basado en los fundamentos del tiro de precisión de la Marina de México:
        1. Postura - Evaluar estabilidad corporal
        2. Empuñe - Verificar sujeción del arma
        3. Imagen - Controlar alineación visual
        4. Alineación de órganos de puntería
        5. Respiración - Sincronización con disparo
        6. Acción del dedo sobre el disparador
        7. Seguimiento - Mantener puntería post-disparo
        8. Recuperación - Preparación para siguiente disparo

        Las agrupaciones en diferentes zonas del blanco indican errores específicos
        que pueden corregirse mediante práctica enfocada.
        """

        analysis_paragraph = Paragraph(analysis_text, self.styles["Normal"])
        elements.append(analysis_paragraph)

        return elements

    def _add_evaluations_section(self, evaluations: List[Dict[str, Any]]) -> List:
        """Agregar sección de evaluaciones"""
        elements = []

        subtitle = Paragraph(
            "EVALUACIONES DEL INSTRUCTOR", self.custom_styles["subtitle"]
        )
        elements.append(subtitle)

        for evaluation in evaluations:
            eval_data = [
                ["Fecha:", evaluation.get("date", "N/A")],
                ["Puntuación:", f"{evaluation.get('score', 0)}/100"],
                ["Instructor:", evaluation.get("instructor_name", "N/A")],
                ["Comentarios:", evaluation.get("comments", "Sin comentarios")],
            ]

            table = Table(eval_data, colWidths=[2 * inch, 4 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("BOX", (0, 0), (-1, -1), 1, colors.blue),
                    ]
                )
            )

            elements.append(table)
            elements.append(Spacer(1, 10))

        return elements

    def _generate_target_analysis(self) -> Optional[Image]:
        """Generar imagen de análisis de blanco"""
        try:
            fig, ax = plt.subplots(1, 1, figsize=(6, 6))

            # Dibujar blanco concéntrico
            center = (0, 0)
            radii = [1, 2, 3, 4, 5]
            colors_list = ["red", "gold", "blue", "black", "white"]

            for radius, color in zip(radii, colors_list):
                circle = patches.Circle(
                    center,
                    radius,
                    linewidth=2,
                    edgecolor="black",
                    facecolor=color,
                    alpha=0.7,
                )
                ax.add_patch(circle)

            # Agregar zonas numeradas del 1-9 según el documento
            zones = {
                1: (0, 0),
                2: (0, 2),
                3: (2, 0),
                4: (0, -2),
                5: (-2, 0),
                6: (0, -3),
                7: (-2, -2),
                8: (-3, 0),
                9: (2, 2),
            }

            for zone, (x, y) in zones.items():
                ax.text(
                    x,
                    y,
                    str(zone),
                    fontsize=12,
                    ha="center",
                    va="center",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                )

            ax.set_xlim(-6, 6)
            ax.set_ylim(-6, 6)
            ax.set_aspect("equal")
            ax.set_title(
                "ANÁLISIS DE ZONAS DE IMPACTO\n(Basado en Programa Marina de México)"
            )
            ax.grid(True, alpha=0.3)

            # Guardar imagen en memoria
            buffer = BytesIO()
            plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)
            plt.close()

            return Image(buffer, width=4 * inch, height=4 * inch)

        except Exception as e:
            logger.error(f"❌ Error generando imagen de análisis: {e}")
            return None

    def _add_monthly_summary(self, report_data: ReportData) -> List:
        """Agregar resumen mensual"""
        elements = []

        subtitle = Paragraph("RESUMEN MENSUAL", self.custom_styles["subtitle"])
        elements.append(subtitle)

        sessions = report_data.sessions
        total_sessions = len(sessions)

        if total_sessions == 0:
            no_data = Paragraph(
                "No hay datos disponibles para el período seleccionado.",
                self.styles["Normal"],
            )
            elements.append(no_data)
            return elements

        # Calcular métricas
        avg_accuracy = sum(s.get("accuracy_percentage", 0) for s in sessions) / max(
            total_sessions, 1
        )
        total_shots = sum(s.get("total_shots_fired", 0) for s in sessions)
        total_score = sum(s.get("total_session_score", 0) for s in sessions)
        avg_score = total_score / max(total_sessions, 1)

        # Contar sesiones completadas
        completed_sessions = sum(1 for s in sessions if s.get("is_finished", False))
        completion_rate = (
            (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        )

        data = [
            ["Sesiones Realizadas:", str(total_sessions)],
            ["Sesiones Completadas:", f"{completed_sessions} ({completion_rate:.1f}%)"],
            ["Precisión Promedio:", f"{avg_accuracy:.1f}%"],
            ["Puntuación Promedio:", f"{avg_score:.1f} pts"],
            ["Total de Disparos:", str(total_shots)],
            ["Progreso:", self._calculate_progress(sessions)],
        ]

        table = Table(data, colWidths=[2.5 * inch, 3.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 1, colors.darkgreen),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.lightgreen),
                ]
            )
        )

        elements.append(table)

        # Agregar análisis de tendencias si hay suficientes datos
        if total_sessions >= 3:
            elements.append(Spacer(1, 15))
            trend_subtitle = Paragraph(
                "ANÁLISIS DE TENDENCIAS", self.custom_styles["subtitle"]
            )
            elements.append(trend_subtitle)

            trend_analysis = self._analyze_monthly_trends(sessions)
            trend_paragraph = Paragraph(trend_analysis, self.styles["Normal"])
            elements.append(trend_paragraph)

        return elements

    def _analyze_monthly_trends(self, sessions: List[Dict[str, Any]]) -> str:
        """Analizar tendencias mensuales"""
        if len(sessions) < 3:
            return "Insuficientes datos para análisis de tendencias."

        # Ordenar sesiones por fecha
        sorted_sessions = sorted(sessions, key=lambda x: x.get("date", ""))

        # Comparar primera mitad vs segunda mitad
        mid_point = len(sorted_sessions) // 2
        first_half = sorted_sessions[:mid_point]
        second_half = sorted_sessions[mid_point:]

        first_avg_accuracy = sum(
            s.get("accuracy_percentage", 0) for s in first_half
        ) / len(first_half)
        second_avg_accuracy = sum(
            s.get("accuracy_percentage", 0) for s in second_half
        ) / len(second_half)

        first_avg_score = sum(
            s.get("total_session_score", 0) for s in first_half
        ) / len(first_half)
        second_avg_score = sum(
            s.get("total_session_score", 0) for s in second_half
        ) / len(second_half)

        accuracy_change = second_avg_accuracy - first_avg_accuracy
        score_change = second_avg_score - first_avg_score

        analysis = []

        # Análisis de precisión
        if accuracy_change > 5:
            analysis.append(
                f"📈 <b>Mejora notable en precisión:</b> +{accuracy_change:.1f}% de incremento."
            )
        elif accuracy_change < -5:
            analysis.append(
                f"📉 <b>Declive en precisión:</b> {accuracy_change:.1f}% de reducción."
            )
        else:
            analysis.append(
                f"📊 <b>Precisión estable:</b> Variación de {accuracy_change:.1f}%."
            )

        # Análisis de puntuación
        if score_change > 10:
            analysis.append(
                f"🎯 <b>Mejora en puntuación:</b> +{score_change:.1f} puntos de incremento."
            )
        elif score_change < -10:
            analysis.append(
                f"⚠️ <b>Declive en puntuación:</b> {score_change:.1f} puntos de reducción."
            )
        else:
            analysis.append(
                f"⚖️ <b>Puntuación estable:</b> Variación de {score_change:.1f} puntos."
            )

        # Recomendaciones
        if accuracy_change < -3 or score_change < -5:
            analysis.append(
                "<b>Recomendación:</b> Revisar técnicas fundamentales y considerar sesiones de práctica adicionales."
            )
        elif accuracy_change > 3 and score_change > 5:
            analysis.append(
                "<b>Recomendación:</b> Excelente progreso. Mantener la rutina actual y considerar ejercicios más avanzados."
            )

        return "<br/><br/>".join(analysis)

    def _add_sessions_table(self, sessions: List[Dict[str, Any]]) -> List:
        """Agregar tabla de sesiones"""
        elements = []

        subtitle = Paragraph("REGISTRO DE SESIONES", self.custom_styles["subtitle"])
        elements.append(subtitle)

        if not sessions:
            no_sessions = Paragraph(
                "No se encontraron sesiones registradas.", self.styles["Normal"]
            )
            elements.append(no_sessions)
            return elements

        headers = [
            "Fecha",
            "Ubicación",
            "Disparos",
            "Precisión",
            "Puntuación",
            "Estado",
        ]
        data = [headers]

        for session in sessions[-15:]:  # Últimas 15 sesiones
            status = "✓ Completa" if session.get("is_finished") else "⚠ Pendiente"
            row = [
                session.get("date", "N/A")[:10],  # Solo fecha
                session.get("location", "N/A")[:20],  # Limitar ubicación
                str(session.get("total_shots_fired", 0)),
                f"{session.get('accuracy_percentage', 0):.1f}%",
                f"{session.get('total_session_score', 0)} pts",
                status,
            ]
            data.append(row)

        table = Table(
            data,
            colWidths=[
                1 * inch,
                1.5 * inch,
                0.8 * inch,
                0.8 * inch,
                1 * inch,
                1 * inch,
            ],
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.lightgrey],
                    ),
                ]
            )
        )

        elements.append(table)
        return elements

    def _get_classification_text(self, accuracy: float) -> str:
        """Obtener clasificación según precisión (basado en documento Marina)"""
        if accuracy >= 90:
            return "TIRADOR EXPERTO (TE) - 90-100%"
        elif accuracy >= 70:
            return "TIRADOR CONFIABLE (TC) - 70-89%"
        elif accuracy >= 40:
            return "TIRADOR MEDIO (TM) - 40-69%"
        else:
            return "TIRADOR REGULAR (TR) - 10-39%"

    def _calculate_progress(self, sessions: List[Dict[str, Any]]) -> str:
        """Calcular progreso del tirador"""
        if len(sessions) < 2:
            return "Insuficientes datos"

        # Ordenar sesiones por fecha
        sorted_sessions = sorted(sessions, key=lambda x: x.get("date", ""))

        first_sessions = (
            sorted_sessions[:3] if len(sorted_sessions) >= 6 else sorted_sessions[:1]
        )
        last_sessions = (
            sorted_sessions[-3:] if len(sorted_sessions) >= 6 else sorted_sessions[-1:]
        )

        first_avg = sum(s.get("accuracy_percentage", 0) for s in first_sessions) / len(
            first_sessions
        )
        last_avg = sum(s.get("accuracy_percentage", 0) for s in last_sessions) / len(
            last_sessions
        )

        improvement = last_avg - first_avg

        if improvement > 5:
            return f"🚀 MEJORA SIGNIFICATIVA (+{improvement:.1f}%)"
        elif improvement > 1:
            return f"📈 MEJORA LEVE (+{improvement:.1f}%)"
        elif improvement < -5:
            return f"📉 DECLIVE SIGNIFICATIVO ({improvement:.1f}%)"
        elif improvement < -1:
            return f"⚠️ DECLIVE LEVE ({improvement:.1f}%)"
        else:
            return f"⚖️ RENDIMIENTO ESTABLE ({improvement:.1f}%)"

    def _add_evolution_chart(self, sessions: List[Dict[str, Any]]) -> List:
        """Agregar gráfico de evolución"""
        elements = []

        try:
            if len(sessions) > 1:
                # Ordenar sesiones por fecha
                sorted_sessions = sorted(sessions, key=lambda x: x.get("date", ""))
                recent_sessions = sorted_sessions[-10:]  # Últimas 10 sesiones

                dates = [s.get("date", "")[:10] for s in recent_sessions]
                accuracies = [s.get("accuracy_percentage", 0) for s in recent_sessions]
                scores = [s.get("total_session_score", 0) for s in recent_sessions]

                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

                # Gráfico de precisión
                ax1.plot(
                    range(len(accuracies)),
                    accuracies,
                    marker="o",
                    linewidth=2,
                    markersize=6,
                    color="blue",
                    label="Precisión",
                )
                ax1.set_title("EVOLUCIÓN DE PRECISIÓN", fontweight="bold")
                ax1.set_ylabel("Precisión (%)")
                ax1.grid(True, alpha=0.3)
                ax1.set_ylim(0, 100)
                ax1.legend()

                # Gráfico de puntuación
                ax2.plot(
                    range(len(scores)),
                    scores,
                    marker="s",
                    linewidth=2,
                    markersize=6,
                    color="green",
                    label="Puntuación",
                )
                ax2.set_title("EVOLUCIÓN DE PUNTUACIÓN", fontweight="bold")
                ax2.set_ylabel("Puntuación (pts)")
                ax2.set_xlabel("Sesiones Recientes")
                ax2.grid(True, alpha=0.3)
                ax2.legend()

                # Ajustar diseño
                plt.tight_layout()

                buffer = BytesIO()
                plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
                buffer.seek(0)
                plt.close()

                chart_image = Image(buffer, width=7 * inch, height=4 * inch)
                elements.append(chart_image)

        except Exception as e:
            logger.error(f"❌ Error generando gráfico de evolución: {e}")
            # Agregar texto alternativo si falla el gráfico
            alt_text = Paragraph(
                "Error generando gráfico de evolución. Los datos están disponibles en las tablas.",
                self.styles["Normal"],
            )
            elements.append(alt_text)

        return elements

    def _generate_analysis_images(self, sessions: List[Dict[str, Any]]) -> List[str]:
        """Generar imágenes de análisis basadas en las sesiones"""
        images = []

        try:
            # Generar gráfico de distribución de ejercicios
            exercise_distribution = self._analyze_exercise_distribution(sessions)
            if exercise_distribution:
                distribution_image = self._create_exercise_distribution_chart(
                    exercise_distribution
                )
                if distribution_image:
                    images.append(distribution_image)

            # Generar análisis de zonas de error si hay datos disponibles
            error_zones = self._analyze_error_zones(sessions)
            if error_zones:
                error_zone_image = self._create_error_zone_analysis(error_zones)
                if error_zone_image:
                    images.append(error_zone_image)

        except Exception as e:
            logger.error(f"❌ Error generando imágenes de análisis: {e}")

        return images

    def _analyze_exercise_distribution(
        self, sessions: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Analizar distribución de tipos de ejercicios"""
        distribution = {}

        for session in sessions:
            exercises = session.get("exercises", [])
            for exercise in exercises:
                exercise_type = exercise.get("exercise_type", "Desconocido")
                distribution[exercise_type] = distribution.get(exercise_type, 0) + 1

        return distribution

    def _create_exercise_distribution_chart(
        self, distribution: Dict[str, int]
    ) -> Optional[str]:
        """Crear gráfico de distribución de ejercicios"""
        try:
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))

            exercise_types = list(distribution.keys())
            counts = list(distribution.values())

            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", "#6C5CE7"]

            wedges, texts, autotexts = ax.pie(
                counts,
                labels=exercise_types,
                autopct="%1.1f%%",
                colors=colors[: len(exercise_types)],
                startangle=90,
            )

            ax.set_title(
                "DISTRIBUCIÓN DE TIPOS DE EJERCICIOS", fontweight="bold", fontsize=14
            )

            # Mejorar legibilidad
            for text in texts:
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")

            plt.tight_layout()

            buffer = BytesIO()
            plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)
            plt.close()

            # Convertir a base64 para almacenamiento
            import base64

            image_data = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{image_data}"

        except Exception as e:
            logger.error(f"❌ Error creando gráfico de distribución: {e}")
            return None

    def _analyze_error_zones(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizar zonas de error comunes"""
        # Esta función puede expandirse cuando se integre con el análisis de imágenes
        # Por ahora, simular datos basados en las estadísticas disponibles

        error_data = {
            "zones": {
                "1": 25,  # Centro
                "2": 15,  # Arriba
                "3": 10,  # Derecha
                "4": 12,  # Abajo
                "5": 8,  # Izquierda
                "6": 8,  # Abajo
                "7": 7,  # Abajo-Izquierda
                "8": 10,  # Izquierda
                "9": 5,  # Arriba-Derecha
            },
            "total_shots": 100,
        }

        return error_data

    def _create_error_zone_analysis(self, error_zones: Dict[str, Any]) -> Optional[str]:
        """Crear análisis visual de zonas de error"""
        try:
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))

            # Crear representación del blanco con zonas
            zones = error_zones.get("zones", {})

            # Posiciones de las zonas según el diagrama de la Marina
            zone_positions = {
                "1": (0, 0),  # Centro
                "2": (0, 1),  # Arriba
                "3": (1, 0),  # Derecha
                "4": (0, -1),  # Abajo
                "5": (-1, 0),  # Izquierda
                "6": (0, -1.5),  # Abajo
                "7": (-1, -1),  # Abajo-Izquierda
                "8": (-1.5, 0),  # Izquierda
                "9": (1, 1),  # Arriba-Derecha
            }

            # Dibujar círculos concéntricos del blanco
            for radius in [3, 2.5, 2, 1.5, 1, 0.5]:
                circle = plt.Circle(
                    (0, 0), radius, fill=False, color="black", linewidth=1
                )
                ax.add_patch(circle)

            # Representar la frecuencia de impactos en cada zona
            max_hits = max(zones.values()) if zones else 1

            for zone, hits in zones.items():
                if zone in zone_positions:
                    x, y = zone_positions[zone]
                    # Tamaño del punto proporcional a la frecuencia
                    size = (hits / max_hits) * 300 + 50
                    color_intensity = hits / max_hits

                    ax.scatter(
                        x,
                        y,
                        s=size,
                        c=color_intensity,
                        cmap="Reds",
                        alpha=0.7,
                        edgecolors="black",
                        linewidth=1,
                    )

                    # Etiqueta con el número de zona y cantidad de impactos
                    ax.annotate(
                        f"Z{zone}\n({hits})",
                        (x, y),
                        ha="center",
                        va="center",
                        fontsize=8,
                        fontweight="bold",
                    )

            ax.set_xlim(-4, 4)
            ax.set_ylim(-4, 4)
            ax.set_aspect("equal")
            ax.set_title(
                "ANÁLISIS DE ZONAS DE IMPACTO\n(Basado en Programa Marina de México)",
                fontweight="bold",
                fontsize=12,
            )
            ax.grid(True, alpha=0.3)

            # Agregar leyenda
            legend_text = """
            Zonas de Error Comunes:
            • Zona 1: Centro (Ideal)
            • Zona 2: Error de anticipación
            • Zona 3: Dedo muy adentro
            • Zona 4: Movimiento brusco
            • Zona 5: Presión con pulgar
            • Zonas 6-9: Combinaciones de errores
            """

            ax.text(
                4.5,
                2,
                legend_text,
                fontsize=8,
                verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8),
            )

            plt.tight_layout()

            buffer = BytesIO()
            plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)
            plt.close()

            # Convertir a base64
            import base64

            image_data = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{image_data}"

        except Exception as e:
            print(f"Error creando análisis de zonas de error: {e}")
            return None

    def _add_image_analysis_section(
        self, analysis_images: List[Any]  # Puede ser List[AnalysisImage]
    ) -> List:
        """Agregar sección de análisis de imágenes con impactos detectados"""
        elements = []

        if not analysis_images:
            return elements

        subtitle = Paragraph(
            "ANÁLISIS DE IMÁGENES CON IMPACTOS DETECTADOS",
            self.custom_styles["subtitle"],
        )
        elements.append(subtitle)

        for img_data in analysis_images:
            analysis = img_data.analysis

            # Título del ejercicio
            exercise_title = Paragraph(
                f"EJERCICIO: {img_data.exercise_name} - {str(img_data.session_date)[:10]}",
                self.custom_styles["normal_bold"],
            )

            elements.append(exercise_title)
            elements.append(Spacer(1, 10))

            # Tabla de datos del análisis
            analysis_data = [
                ["Total de Impactos:", str(analysis.get("total_impacts", 0))],
                [
                    "Impactos Frescos (Dentro):",
                    str(analysis.get("fresh_impacts_inside", 0)),
                ],
                [
                    "Impactos Frescos (Fuera):",
                    str(analysis.get("fresh_impacts_outside", 0)),
                ],
                ["Precisión:", f"{analysis.get('accuracy_percentage', 0):.1f}%"],
                ["Puntuación Total:", f"{analysis.get('total_score', 0)} pts"],
                [
                    "Puntuación Promedio/Disparo:",
                    f"{analysis.get('average_score_per_shot', 0):.1f} pts",
                ],
                [
                    "Diámetro de Agrupación:",
                    (
                        f"{analysis.get('group_diameter', 0):.1f}mm"
                        if analysis.get("group_diameter")
                        else "N/A"
                    ),
                ],
            ]

            analysis_table = Table(analysis_data, colWidths=[2.5 * inch, 2 * inch])
            analysis_table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("GRID", (0, 0), (-1, -1), 1, colors.blue),
                    ]
                )
            )

            elements.append(analysis_table)
            elements.append(Spacer(1, 10))

            # Imagen con impactos marcados
            try:
                image_data = img_data.image_data
                if image_data:
                    import base64
                    from io import BytesIO
                    from reportlab.lib.utils import ImageReader

                    image_bytes = base64.b64decode(image_data)
                    image_buffer = BytesIO(image_bytes)

                    # Redimensionar para el PDF
                    target_image = Image(image_buffer, width=4 * inch, height=3 * inch)
                    elements.append(target_image)

            except Exception as e:
                logger.error(f"❌ Error agregando imagen al PDF: {e}")
                error_text = Paragraph(
                    "Error cargando imagen de análisis", self.styles["Normal"]
                )
                elements.append(error_text)

            elements.append(Spacer(1, 20))

        return elements
